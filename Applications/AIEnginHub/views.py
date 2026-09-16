import io
import uuid
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Q
from rest_framework import viewsets, status, filters
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    CourseCategory, LibraryCourse, CourseChapter, CourseVersionSnapshot,
    ChatSession, ChatMessage, LegacyChatHistory,
    TieupLead, TieupPolicy, OutreachStatusLog, SmtpConfiguration,
    AIProductPreset, GenerationJob, SystemActivityLog, MetricSnapshot
)
from .serializers import (
    CourseCategorySerializer, LibraryCourseSerializer, CourseChapterSerializer,
    CourseVersionSnapshotSerializer, ChatSessionSerializer, ChatMessageSerializer,
    LegacyChatHistorySerializer, TieupLeadSerializer, TieupPolicySerializer,
    OutreachStatusLogSerializer, SmtpConfigurationSerializer,
    AIProductPresetSerializer, GenerationJobSerializer,
    SystemActivityLogSerializer, MetricSnapshotSerializer
)
from .services.gemini_client import gemini_client, PROMPT_REGISTRY
from .services.docx_builder import build_course_docx
from .services.smtp_service import verify_smtp_connection, send_single_email, dispatch_batch_campaign
from .services.tts_service import get_tts_audio_bytes


# ---------------------------------------------------------------------------
# 1. Course Creator & Permanent Library ViewSets
# ---------------------------------------------------------------------------

class CourseViewSet(viewsets.ModelViewSet):
    queryset = LibraryCourse.objects.all().prefetch_related('chapters', 'version_snapshots')
    serializer_class = LibraryCourseSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'subtitle', 'category', 'overview', 'tags']
    ordering_fields = ['created_at', 'updated_at', 'title', 'download_count']
    ordering = ['-updated_at']

    @action(detail=True, methods=['post'], url_path='toggle-chapter')
    def toggle_chapter(self, request, pk=None):
        course = self.get_object()
        chapter_id = request.data.get('chapterId') or request.data.get('chapter_id')
        if not chapter_id:
            return Response({'error': 'chapterId is required'}, status=status.HTTP_400_BAD_REQUEST)

        chapter = course.chapters.filter(id=chapter_id).first()
        if not chapter:
            return Response({'error': 'Chapter not found'}, status=status.HTTP_404_NOT_FOUND)

        chapter.is_completed = not chapter.is_completed
        chapter.save()
        return Response({'success': True, 'chapterId': chapter.id, 'isCompleted': chapter.is_completed, 'course': LibraryCourseSerializer(course).data})

    @action(detail=False, methods=['post'], url_path='import')
    def import_courses(self, request):
        courses_data = request.data.get('courses', request.data if isinstance(request.data, list) else [])
        created_count = 0
        errors = []
        for item in courses_data:
            serializer = LibraryCourseSerializer(data=item)
            if serializer.is_valid():
                serializer.save()
                created_count += 1
            else:
                errors.append(serializer.errors)
        return Response({'success': True, 'count': created_count, 'errors': errors[:5]}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get', 'post'], url_path='export-docx')
    def export_docx(self, request, pk=None):
        course = self.get_object()
        serializer = LibraryCourseSerializer(course)
        docx_buffer = build_course_docx(serializer.data)

        response = HttpResponse(
            docx_buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        safe_title = "".join(c for c in course.title if c.isalnum() or c in (' ', '_', '-')).strip() or "Course"
        response['Content-Disposition'] = f'attachment; filename="{safe_title}_Curriculum.docx"'
        return response

    @action(detail=False, methods=['delete'], url_path='clear-all')
    def clear_all(self, request):
        count, _ = LibraryCourse.objects.filter(locked=False).delete()
        return Response({'success': True, 'deletedCount': count})


class PermanentCourseViewSet(viewsets.ModelViewSet):
    queryset = LibraryCourse.objects.filter(is_permanent=True).prefetch_related('chapters', 'version_snapshots')
    serializer_class = LibraryCourseSerializer
    permission_classes = [AllowAny]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        manual_confirm = request.data.get('manualConfirm', False) if isinstance(request.data, dict) else False
        if instance.locked and not manual_confirm:
            return Response(
                {'error': 'Cannot delete locked permanent course without manual confirmation (manualConfirm=true)'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_path='download')
    def download(self, request, pk=None):
        course = self.get_object()
        course.download_count += 1
        course.last_downloaded_at = timezone.now()
        course.save()
        return Response({'success': True, 'downloadCount': course.download_count, 'lastDownloadedAt': course.last_downloaded_at})


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = CourseCategory.objects.all()
    serializer_class = CourseCategorySerializer
    permission_classes = [AllowAny]


# ---------------------------------------------------------------------------
# 2. Universal AI Chat & Multi-Turn Session ViewSets
# ---------------------------------------------------------------------------

class ChatSessionViewSet(viewsets.ModelViewSet):
    queryset = ChatSession.objects.all().prefetch_related('messages')
    serializer_class = ChatSessionSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'product_type', 'studied_by', 'target_audience']
    ordering_fields = ['is_pinned', 'updated_at', 'created_at', 'title']
    ordering = ['-is_pinned', '-updated_at']

    @action(detail=True, methods=['post', 'patch'], url_path='title')
    def title(self, request, pk=None):
        session = self.get_object()
        new_title = request.data.get('title')
        if not new_title:
            return Response({'error': 'title field is required'}, status=status.HTTP_400_BAD_REQUEST)
        session.title = new_title
        session.save()
        return Response({'success': True, 'session': ChatSessionSerializer(session).data})

    @action(detail=True, methods=['post'], url_path='pin')
    def pin(self, request, pk=None):
        session = self.get_object()
        session.is_pinned = not session.is_pinned
        session.save()
        return Response({'success': True, 'isPinned': session.is_pinned, 'session': ChatSessionSerializer(session).data})

    @action(detail=True, methods=['post'], url_path='messages')
    def add_message(self, request, pk=None):
        session = self.get_object()
        msg_data = request.data.copy()
        msg_data['session'] = session.id
        serializer = ChatMessageSerializer(data=msg_data)
        if serializer.is_valid():
            msg = serializer.save()
            session.updated_at = timezone.now()
            session.save(update_fields=['updated_at'])
            return Response(ChatMessageSerializer(msg).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['delete'], url_path='clear-all')
    def clear_all(self, request):
        count, _ = ChatSession.objects.filter(locked=False).delete()
        return Response({'success': True, 'deletedCount': count})

    @action(detail=False, methods=['post'], url_path='import')
    def import_sessions(self, request):
        sessions_data = request.data.get('sessions', request.data if isinstance(request.data, list) else [])
        created_count = 0
        for item in sessions_data:
            serializer = ChatSessionSerializer(data=item)
            if serializer.is_valid():
                serializer.save()
                created_count += 1
        return Response({'success': True, 'count': created_count})


class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = [AllowAny]


class LegacyChatHistoryViewSet(viewsets.ModelViewSet):
    queryset = LegacyChatHistory.objects.all()
    serializer_class = LegacyChatHistorySerializer
    permission_classes = [AllowAny]


# ---------------------------------------------------------------------------
# 3. University Tie-Up & Outreach ViewSets
# ---------------------------------------------------------------------------

class TieupLeadViewSet(viewsets.ModelViewSet):
    queryset = TieupLead.objects.all()
    serializer_class = TieupLeadSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_partner', 'country', 'category', 'anti_spam_status']
    search_fields = ['name', 'country', 'location_main', 'contact_person', 'contact_email']
    ordering = ['-updated_at']

    @action(detail=False, methods=['post'], url_path='batch')
    def batch(self, request):
        leads_data = request.data.get('leads', request.data if isinstance(request.data, list) else [])
        created_count = 0
        errors = []
        for lead_item in leads_data:
            serializer = TieupLeadSerializer(data=lead_item)
            if serializer.is_valid():
                serializer.save()
                created_count += 1
            else:
                errors.append(serializer.errors)
        return Response({'success': True, 'count': created_count, 'errors': errors[:5]}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='partner')
    def partner(self, request, pk=None):
        lead = self.get_object()
        lead.is_partner = not lead.is_partner
        lead.save()
        return Response({'success': True, 'isPartner': lead.is_partner, 'lead': TieupLeadSerializer(lead).data})


class PolicyViewSet(viewsets.ModelViewSet):
    queryset = TieupPolicy.objects.all()
    serializer_class = TieupPolicySerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        # Always guarantee global_policy exists
        policy, _ = TieupPolicy.objects.get_or_create(
            id='global_policy',
            defaults={
                'min_commission_percent': 15.0,
                'target_commission_percent': 20.0,
                'partnership_criteria': 'Accredited university with international student programs.',
                'preferred_payment_terms': 'Net 30 on student semester enrollment'
            }
        )
        return Response(TieupPolicySerializer(policy).data)


class OutreachLogViewSet(viewsets.ModelViewSet):
    queryset = OutreachStatusLog.objects.all().select_related('lead')
    serializer_class = OutreachStatusLogSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'phase', 'sender_email']
    search_fields = ['institution_name', 'recipient_email', 'subject']
    ordering = ['-created_at']


class SmtpConfigurationViewSet(viewsets.ModelViewSet):
    queryset = SmtpConfiguration.objects.all()
    serializer_class = SmtpConfigurationSerializer
    permission_classes = [AllowAny]


# ---------------------------------------------------------------------------
# 4. Standalone SMTP & Email Outreach APIViews
# ---------------------------------------------------------------------------

class VerifySmtpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        host = data.get('host', 'smtp.gmail.com').strip()
        port = int(data.get('port', 587))
        user = (data.get('senderEmail') or data.get('user', '')).strip()
        password = (data.get('appPassword') or data.get('pass', '')).strip()
        secure = bool(data.get('secure', port == 465))

        res = verify_smtp_connection(host, port, user, password, secure)
        if res.get('success'):
            return Response(res, status=status.HTTP_200_OK)
        return Response(res, status=status.HTTP_400_BAD_REQUEST)


class SendSingleSmtpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        host = data.get('host', 'smtp.gmail.com')
        port = int(data.get('port', 587))
        sender_email = data.get('senderEmail') or data.get('sender_email')
        app_password = data.get('appPassword') or data.get('app_password')
        recipient_email = data.get('recipientEmail') or data.get('recipient_email')
        subject = data.get('subject', 'Partnership Outreach')
        content = data.get('content') or data.get('body', '')
        lead_id = data.get('leadId') or data.get('lead_id')
        institution_name = data.get('institutionName', '')
        secure = bool(data.get('secure', port == 465))

        if not all([sender_email, app_password, recipient_email]):
            return Response({'error': 'senderEmail, appPassword, and recipientEmail are required.'}, status=status.HTTP_400_BAD_REQUEST)

        res = send_single_email(
            host=host, port=port, sender_email=sender_email, app_password=app_password,
            recipient_email=recipient_email, subject=subject, content=content,
            lead_id=lead_id, institution_name=institution_name, secure=secure
        )
        return Response(res, status=status.HTTP_200_OK if res.get('success') else status.HTTP_400_BAD_REQUEST)


class DispatchSmtpBatchView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.data
        # Run bulk campaign
        res = dispatch_batch_campaign(payload)
        return Response(res, status=status.HTTP_200_OK if res.get('success') else status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------------------------------------
# 5. Regional TTS Audio Stream Proxy View
# ---------------------------------------------------------------------------

class RegionalTTSProxyView(APIView):
    """
    Streams Google Translate TTS audio with server-side Redis/Memory caching
    for low-latency voice synthesis across all supported regional languages.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        query = request.GET.get('q', '').strip()
        target_lang = request.GET.get('tl', 'en').strip()

        if not query:
            return JsonResponse({'error': 'Missing text parameter q'}, status=400)

        audio_bytes, error = get_tts_audio_bytes(query, target_lang)
        if error:
            return JsonResponse({'error': 'Failed to synthesize TTS audio', 'message': error}, status=502)

        response = HttpResponse(audio_bytes, content_type='audio/mpeg')
        response['Cache-Control'] = 'public, max-age=604800'
        return response


# ---------------------------------------------------------------------------
# 6. AI Generation Gateway (17 AI Products & Gemini Proxy)
# ---------------------------------------------------------------------------

class AIGenerateProxyView(APIView):
    """
    Direct proxy to Google Gemini 2.5/Pro engine with support for all 17 AI Hub tools.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        prompt = request.data.get('prompt', '')
        system_instruction = request.data.get('systemInstruction') or request.data.get('system_instruction')
        product_type = request.data.get('productType') or request.data.get('product_type')
        model = request.data.get('model')
        temperature = float(request.data.get('temperature', 0.7))

        if not prompt:
            return Response({'error': 'Prompt parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        result = gemini_client.generate_content(
            prompt=prompt,
            system_instruction=system_instruction,
            model=model,
            product_type=product_type,
            temperature=temperature
        )
        return Response(result)


# ---------------------------------------------------------------------------
# 7. Course DOCX Standalone Export View
# ---------------------------------------------------------------------------

class CourseDocxExportView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk=None):
        if pk:
            course = LibraryCourse.objects.filter(id=pk).first()
            if not course:
                return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
            course_data = LibraryCourseSerializer(course).data
        else:
            course_data = request.query_params.dict()

        docx_buffer = build_course_docx(course_data)
        response = HttpResponse(
            docx_buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        title = course_data.get('title', 'Course')
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '_', '-')).strip()
        response['Content-Disposition'] = f'attachment; filename="{safe_title}_Curriculum.docx"'
        return response

    def post(self, request, pk=None):
        if pk:
            course = LibraryCourse.objects.filter(id=pk).first()
            if not course:
                return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
            course_data = LibraryCourseSerializer(course).data
        else:
            course_data = request.data

        docx_buffer = build_course_docx(course_data)
        response = HttpResponse(
            docx_buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        title = course_data.get('title', 'Course')
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '_', '-')).strip()
        response['Content-Disposition'] = f'attachment; filename="{safe_title}_Curriculum.docx"'
        return response


# ---------------------------------------------------------------------------
# 8. Central Telemetry, Health & Dashboard Stats
# ---------------------------------------------------------------------------

class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'status': 'healthy',
            'app': 'AIEnginHub',
            'version': '1.0.0',
            'database': 'connected',
            'geminiEngine': 'active' if gemini_client.api_key else 'mock_fallback',
            'timestamp': timezone.now().isoformat()
        })


class DashboardStatsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        total_courses = LibraryCourse.objects.count()
        permanent_courses = LibraryCourse.objects.filter(is_permanent=True).count()
        total_sessions = ChatSession.objects.count()
        total_leads = TieupLead.objects.count()
        partner_leads = TieupLead.objects.filter(is_partner=True).count()
        total_outreach = OutreachStatusLog.objects.count()
        delivered_outreach = OutreachStatusLog.objects.filter(status='delivered').count()

        return Response({
            'totalCourses': total_courses,
            'permanentCourses': permanent_courses,
            'totalSessions': total_sessions,
            'totalLeads': total_leads,
            'partnerLeads': partner_leads,
            'totalOutreachLogs': total_outreach,
            'deliveredOutreach': delivered_outreach,
            'timestamp': timezone.now()
        })


class PresetViewSet(viewsets.ModelViewSet):
    queryset = AIProductPreset.objects.all()
    serializer_class = AIProductPresetSerializer
    permission_classes = [AllowAny]


class GenerationJobViewSet(viewsets.ModelViewSet):
    queryset = GenerationJob.objects.all()
    serializer_class = GenerationJobSerializer
    permission_classes = [AllowAny]


class TelemetryViewSet(viewsets.ModelViewSet):
    queryset = SystemActivityLog.objects.all()
    serializer_class = SystemActivityLogSerializer
    permission_classes = [AllowAny]
