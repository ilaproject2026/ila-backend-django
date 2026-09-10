import logging
import uuid
from django.conf import settings
from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.db.models import Sum, Count
from django.db import transaction
import google.generativeai as genai

from .serializers import (
    ConsultantChatRequestSerializer, ConsultantChatResponseSerializer,
    ConsultantChatMessageSerializer, ConsultantSessionSerializer, ConsultantChatInputSerializer
)
from .prompts import ILA_CONSULTANT_SYSTEM_INSTRUCTION
from .models import AITokenUsageLog
from ..models import ConsultantSession, ConsultantChatMessage, Inquiry

logger = logging.getLogger(__name__)

# Configure Google Generative AI
gemini_key = getattr(settings, 'GEMINI_API_KEY', None)
if gemini_key:
    try:
        genai.configure(api_key=gemini_key)
    except Exception as e:
        logger.warning(f"Could not configure genai with key: {e}")


class ConsultantChatView(APIView):
    """
    POST /api/v1/consultant/chat/
    Receives user chat messages, appends ILA system context, calls Gemini 1.5 Flash,
    and returns a structured AI response.
    """
    permission_classes = [AllowAny]

    # Apply IP-based rate limiting (20 requests per minute per IP)
    @method_decorator(ratelimit(key='ip', rate='20/m', method='POST', block=True))
    def post(self, request):
        serializer = ConsultantChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        user_message = data['message']
        topic = data.get('topic', 'general')
        history = data.get('history', [])

        current_key = getattr(settings, 'GEMINI_API_KEY', None)
        # Fallback if Gemini key is missing
        if not current_key:
            actions = ["Call Us", "View Programs", "Talk to Consultant"]
            return Response({
                "reply": "Thank you for reaching out to ILA Academy! Our consultants specialize in German language courses (A1-B2), Opportunity Card (Chancenkarte), and work while you study programs in Germany. How can we best assist your journey?",
                "topic": topic,
                "suggested_actions": actions,
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
            }, status=status.HTTP_200_OK)

        try:
            # Re-ensure configuration with current key
            genai.configure(api_key=current_key)

            # Initialize model with system instruction
            model = genai.GenerativeModel(
                model_name="gemini-3.6-flash",
                system_instruction=ILA_CONSULTANT_SYSTEM_INSTRUCTION,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 600,
                }
            )

            # Format history for Gemini SDK
            gemini_history = []
            for item in history[-6:]:  # Keep last 6 exchanges for context
                role = "user" if item['role'] == 'user' else "model"
                gemini_history.append({
                    "role": role,
                    "parts": [item['content']]
                })

            chat = model.start_chat(history=gemini_history)
            response = chat.send_message(user_message)
            reply_text = response.text.strip()

            # Extract Token Usage from Google Gemini metadata
            prompt_tokens = 0
            completion_tokens = 0
            total_tokens = 0
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                prompt_tokens = getattr(response.usage_metadata, 'prompt_token_count', 0)
                completion_tokens = getattr(response.usage_metadata, 'candidates_token_count', 0)
                total_tokens = getattr(response.usage_metadata, 'total_token_count', 0)

            # Persist token audit log to database
            try:
                ip_addr = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
                if ',' in ip_addr:
                    ip_addr = ip_addr.split(',')[0].strip()
                AITokenUsageLog.objects.create(
                    ip_address=ip_addr[:45] if ip_addr else None,
                    topic=topic,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                    model_name="gemini-3.6-flash"
                )
            except Exception as log_err:
                logger.warning(f"Could not persist AITokenUsageLog: {log_err}")

            # Dynamic suggested action chips based on topic
            actions = ["Talk to Consultant"]
            if topic == 'visa':
                actions = ["Check Visa Checklist", "Book Embassy Prep", "Blocked Account Guide"]
            elif topic == 'jobs':
                actions = ["Chancenkarte Evaluation", "AI Resume Match", "Ausbildung Programs"]
            elif topic == 'housing':
                actions = ["WG Accommodations", "Blocked Account Guide", "Anmeldung Registration"]
            elif topic == 'arrival':
                actions = ["Arrival Checklist PDF", "Anmeldung Guide", "Airport Reception"]
            elif topic == 'education':
                actions = ["View German Courses", "Download Syllabus", "Book Free Demo"]

            return Response({
                "reply": reply_text,
                "topic": topic,
                "suggested_actions": actions,
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens
                }
            })

        except Exception as exc:
            logger.error(f"Gemini API error in ConsultantChatView: {str(exc)}")
            
            # Domain-aware smart fallback response so the chat remains helpful
            user_msg_lower = user_message.lower()
            if any(k in user_msg_lower for k in ["chancenkarte", "opportunity card", "points"]):
                reply_text = (
                    "The German Opportunity Card (Chancenkarte) is a points-based job search visa launched in June 2024. "
                    "You need a minimum of 6 points based on criteria including qualifications, German (A2-B2) or English (C1), "
                    "age (under 35 gets maximum points), work experience, and ties to Germany. You also need proof of funds (€1,027/month) "
                    "or an €11,904 blocked account. Would you like our advisors to calculate your exact score?"
                )
                actions = ["Chancenkarte Evaluation", "Points Calculator", "Talk to Consultant"]
            elif any(k in user_msg_lower for k in ["course", "german", "a1", "a2", "b1", "b2", "language", "class"]):
                reply_text = (
                    "At ILA Academy, we offer Goethe and TELC-aligned German language courses from A1 through B2. "
                    "Our classes are led by certified bilingual trainers, featuring live interactive sessions, daily practice modules, "
                    "and official Goethe-Zertifikat exam preparation. Would you like to check the upcoming batch dates or book a free trial class?"
                )
                actions = ["View German Courses", "Download Syllabus", "Book Free Demo"]
            elif any(k in user_msg_lower for k in ["blocked account", "sperrkonto", "fund", "money", "cost", "fee"]):
                reply_text = (
                    "For German student and job seeker visas, the German Federal Foreign Office requires an official Blocked Account "
                    "(Sperrkonto). For 2024-2025, the required amount is typically €11,904/year (€992 - €1,027/month). "
                    "ILA assists with end-to-end blocked account setup and student health insurance partners like Expatrio and Coracle."
                )
                actions = ["Blocked Account Guide", "Talk to Consultant", "Visa Checklist"]
            elif any(k in user_msg_lower for k in ["ausbildung", "vocational", "nursing", "hospitality"]):
                reply_text = (
                    "Ausbildung is a dual-vocational training program in Germany where you work and study simultaneously while earning "
                    "a monthly stipend (€900 - €1,400/month). Tuition is 100% free! Minimum requirement is usually B1/B2 German. "
                    "Top sectors include Nursing, IT, Mechatronics, and Hotel Management."
                )
                actions = ["Ausbildung Programs", "Language Requirement", "Talk to Consultant"]
            elif any(k in user_msg_lower for k in ["visa", "appointment", "vfs"]):
                reply_text = (
                    "German visa processing requires verified documentation, APS certificate (for academic degrees), blocked account, "
                    "health insurance, and certified German language proficiency. ILA Academy provides mock visa interviews, "
                    "document pre-screening, and VFS appointment guidance."
                )
                actions = ["Check Visa Checklist", "Book Embassy Prep", "Talk to Consultant"]
            else:
                reply_text = (
                    "Thank you for contacting ILA Academy! We guide students and professionals into Germany through our German language training "
                    "(A1-B2), Chancenkarte points verification, university admissions, and Ausbildung placements. "
                    "How can we best assist your relocation journey today?"
                )
                actions = ["Talk to Consultant", "View Programs", "Book Callback"]

            return Response({
                "reply": reply_text,
                "topic": topic,
                "suggested_actions": actions,
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
            }, status=status.HTTP_200_OK)


class TokenAnalyticsSummaryView(APIView):
    """
    GET /api/v1/consultant/tokens/summary/
    Returns aggregate token usage, query counts, and cost estimates.
    """
    permission_classes = [AllowAny]  # Can also be restricted or authenticated

    def get(self, request):
        stats = AITokenUsageLog.objects.aggregate(
            total_tokens=Sum('total_tokens'),
            total_prompt_tokens=Sum('prompt_tokens'),
            total_completion_tokens=Sum('completion_tokens'),
            total_queries=Count('id')
        )

        total_tokens = stats['total_tokens'] or 0
        prompt_tokens = stats['total_prompt_tokens'] or 0
        completion_tokens = stats['total_completion_tokens'] or 0
        
        # Estimate cost (Gemini 1.5 Flash standard tier rates)
        est_cost_usd = ((prompt_tokens / 1_000_000) * 0.075) + ((completion_tokens / 1_000_000) * 0.30)
        est_cost_inr = est_cost_usd * 86.50

        return Response({
            "total_queries": stats['total_queries'] or 0,
            "total_tokens": total_tokens,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "estimated_cost": {
                "usd": round(est_cost_usd, 4),
                "inr": round(est_cost_inr, 2)
            }
        })


class ConsultantChatAPIView(APIView):
    """
    POST /api/v1/consultant/chat/
    Tracks the session, saves incoming user messages, and returns the session state.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = ConsultantChatInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        session_key = data.get('session_id') or str(uuid.uuid4())
        topic = data.get('topic', 'general')
        user_message_text = data.get('message')

        # 1. Retrieve or Create Chat Session
        session, created = ConsultantSession.objects.get_or_create(
            session_key=session_key,
            defaults={
                'user': request.user if request.user.is_authenticated else None,
                'user_email': data.get('user_email') or (request.user.email if request.user.is_authenticated else ''),
                'user_phone': data.get('user_phone', ''),
                'user_name': data.get('user_name', ''),
                'initial_topic': topic,
                'current_topic': topic,
                'ip_address': request.META.get('REMOTE_ADDR'),
                'user_agent': request.META.get('HTTP_USER_AGENT', '')[:255],
            }
        )
        if not created and topic != session.current_topic:
            session.current_topic = topic
            session.save(update_fields=['current_topic', 'last_activity'])

        # 2. Save incoming User Message
        user_message = ConsultantChatMessage.objects.create(
            session=session,
            role='user',
            content=user_message_text
        )

        # 3. Update Session Stats
        session.total_messages = session.messages.count()
        session.save(update_fields=['total_messages', 'last_activity'])

        return Response({
            'session_id': session.session_key,
            'topic': session.current_topic,
            'status': 'received',
            'message': ConsultantChatMessageSerializer(user_message).data,
            'total_messages': session.total_messages,
            'reply': None,
        }, status=status.HTTP_200_OK)


class ConsultantSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/v1/consultant/sessions/
    GET /api/v1/consultant/sessions/{session_key}/
    GET /api/v1/consultant/sessions/{session_key}/history/
    """
    queryset = ConsultantSession.objects.all().prefetch_related('messages')
    serializer_class = ConsultantSessionSerializer
    lookup_field = 'session_key'
    permission_classes = [AllowAny]  # Visitors can fetch their own session by key

    @action(detail=True, methods=['get'])
    def history(self, request, session_key=None):
        session = self.get_object()
        serializer = ConsultantChatMessageSerializer(session.messages.all(), many=True)
        return Response({
            'session_id': session.session_key,
            'topic': session.current_topic,
            'status': session.status,
            'messages': serializer.data
        })

    @action(detail=True, methods=['post'], url_path='convert-to-inquiry')
    def convert_to_inquiry(self, request, session_key=None):
        """
        POST /api/v1/consultant/sessions/{session_key}/convert-to-inquiry/
        Converts active chat lead directly into CRM front office Inquiry record!
        """
        session = self.get_object()
        name = request.data.get('name') or session.user_name or 'Live Consultant Lead'
        email = request.data.get('email') or session.user_email
        phone = request.data.get('phone') or session.user_phone

        if not email and not phone:
            return Response({'error': 'Email or phone required to create inquiry.'}, status=status.HTTP_400_BAD_REQUEST)

        category_map = {
            'visa': 'Visa',
            'jobs': 'Jobs',
            'arrival': 'General Front Office',
            'housing': 'Study Abroad',
            'general': 'General Front Office'
        }

        inquiry = Inquiry.objects.create(
            name=name,
            email=email or 'lead@ilaglobal.com',
            phone=phone or 'N/A',
            type='Online',
            category=category_map.get(session.current_topic, 'General Front Office'),
            crm_status='New Lead',
            pipeline_stage='Intake',
        )

        session.inquiry = inquiry
        session.status = 'converted_to_lead'
        session.save(update_fields=['inquiry', 'status'])

        return Response({
            'success': True,
            'inquiry_id': str(inquiry.id),
            'message': 'Session converted to CRM lead successfully.'
        })

