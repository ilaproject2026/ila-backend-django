import uuid
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import CommunicationWorkflowRule, DispatchLog
from .serializers import (
    CommunicationWorkflowRuleSerializer,
    DispatchLogSerializer,
    TriggerSimulationSerializer
)

class CommunicationWorkflowRuleViewSet(viewsets.ModelViewSet):
    """
    CRUD ViewSet for Communication Workflow Rules & Triggers
    """
    queryset = CommunicationWorkflowRule.objects.all()
    serializer_class = CommunicationWorkflowRuleSerializer

    @action(detail=True, methods=['post'], url_path='toggle-active')
    def toggle_active(self, request, pk=None):
        rule = self.get_object()
        rule.is_active = not rule.is_active
        rule.save()
        return Response({'id': rule.id, 'is_active': rule.is_active}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='simulate-trigger')
    def simulate_trigger(self, request):
        """
        Simulate instant multi-channel dispatch with live parameter injection
        """
        serializer = TriggerSimulationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        wf_id = serializer.validated_data['workflow_id']
        name = serializer.validated_data['student_name']
        email = serializer.validated_data['student_email']
        phone = serializer.validated_data['student_phone']
        course = serializer.validated_data['course_track']

        try:
            workflow = CommunicationWorkflowRule.objects.get(id=wf_id)
        except CommunicationWorkflowRule.DoesNotExist:
            return Response({'error': 'Workflow not found'}, status=status.HTTP_404_NOT_FOUND)

        # Replace dynamic tokens
        compiled_message = (
            workflow.message_template
            .replace('{{name}}', name)
            .replace('{{course}}', course)
            .replace('{{time}}', '09:00 AM CET')
            .replace('{{tutor}}', 'Frau Lisa Weber')
            .replace('{{portal_link}}', 'https://ilas.global/student-portal')
        )

        # Create dispatch log
        log = DispatchLog.objects.create(
            id=f"LOG-{uuid.uuid4().hex[:6].upper()}",
            workflow=workflow,
            recipient_name=name,
            recipient_email=email,
            recipient_phone=phone,
            course_or_batch=course,
            channel=workflow.channel,
            status='Delivered',
            message_preview=compiled_message,
            latency_ms=320,
            delivered_at=timezone.now()
        )

        # Update workflow stats
        workflow.total_dispatched += 1
        workflow.delivered_count += 1
        workflow.last_triggered = timezone.now()
        workflow.save()

        return Response({
            'success': True,
            'log_id': log.id,
            'channel': workflow.channel,
            'recipient_name': name,
            'message_preview': compiled_message,
            'status': 'Delivered'
        }, status=status.HTTP_200_OK)


class DispatchLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only audit log for communication dispatches
    """
    queryset = DispatchLog.objects.all().select_related('workflow')
    serializer_class = DispatchLogSerializer


from rest_framework.permissions import AllowAny
from .models import ConsultantChatSession, ConsultantChatMessage
from .serializers import ConsultantChatSessionSerializer, ConsultantChatMessageSerializer


class ConsultantChatSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Live Consultant chat sessions, message logs, and transcript syncing
    """
    permission_classes = [AllowAny]
    queryset = ConsultantChatSession.objects.all().order_by('-updated_at')
    serializer_class = ConsultantChatSessionSerializer
    lookup_field = 'session_id'

    def create(self, request, *args, **kwargs):
        session_id = request.data.get('session_id') or f"chat_{uuid.uuid4().hex[:12]}"
        user_name = request.data.get('user_name', 'Guest Aspirant')
        user_email = request.data.get('user_email', '')
        user_phone = request.data.get('user_phone', '')
        topic = request.data.get('topic', 'general')
        metadata = request.data.get('metadata', {})

        session, created = ConsultantChatSession.objects.get_or_create(
            session_id=session_id,
            defaults={
                'user_name': user_name,
                'user_email': user_email,
                'user_phone': user_phone,
                'topic': topic,
                'metadata': metadata,
            }
        )

        if not created:
            # Update latest user info or topic if provided
            updated = False
            if user_name and session.user_name == 'Guest Aspirant':
                session.user_name = user_name
                updated = True
            if user_email and not session.user_email:
                session.user_email = user_email
                updated = True
            if topic and session.topic != topic:
                session.topic = topic
                updated = True
            if metadata:
                session.metadata.update(metadata)
                updated = True
            if updated:
                session.save()

        serializer = self.get_serializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='message')
    def add_message(self, request, session_id=None):
        session = self.get_object()
        sender = request.data.get('sender', 'user')
        if sender == 'assistant' or sender == 'bot':
            sender = 'assistant'
        else:
            sender = 'user'

        content = request.data.get('content', '').strip()
        topic = request.data.get('topic', session.topic)
        msg_id = request.data.get('id') or f"msg_{uuid.uuid4().hex[:10]}"

        if not content:
            return Response({'error': 'Message content cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)

        # Create persistent message record
        chat_msg = ConsultantChatMessage.objects.create(
            id=msg_id,
            session=session,
            sender=sender,
            content=content,
            topic=topic
        )

        # Append to session history JSON
        history_item = {
            'id': chat_msg.id,
            'role': chat_msg.sender,
            'content': chat_msg.content,
            'topic': chat_msg.topic,
            'timestamp': chat_msg.timestamp.isoformat()
        }
        
        history = list(session.messages_history or [])
        # Avoid duplicate by id
        if not any(item.get('id') == chat_msg.id for item in history):
            history.append(history_item)
            session.messages_history = history

        session.message_count = len(history)
        session.topic = topic
        session.save()

        return Response({
            'success': True,
            'message_id': chat_msg.id,
            'session_id': session.session_id,
            'message_count': session.message_count,
            'recorded_at': chat_msg.timestamp
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='sync')
    def sync_session(self, request):
        """
        Batch synchronizes conversation messages and user context
        """
        session_id = request.data.get('session_id') or f"chat_{uuid.uuid4().hex[:12]}"
        user_name = request.data.get('user_name', 'Guest Aspirant')
        user_email = request.data.get('user_email', '')
        user_phone = request.data.get('user_phone', '')
        topic = request.data.get('topic', 'general')
        messages = request.data.get('messages', [])
        metadata = request.data.get('metadata', {})

        session, _ = ConsultantChatSession.objects.get_or_create(
            session_id=session_id,
            defaults={
                'user_name': user_name,
                'user_email': user_email,
                'user_phone': user_phone,
                'topic': topic,
                'metadata': metadata,
            }
        )

        if user_name and session.user_name == 'Guest Aspirant':
            session.user_name = user_name
        if user_email and not session.user_email:
            session.user_email = user_email
        if topic:
            session.topic = topic
        if metadata:
            session.metadata.update(metadata)

        # Process messages list
        history = list(session.messages_history or [])
        existing_history_ids = {item.get('id') for item in history if item.get('id')}
        
        new_history_items = []
        msg_items = []
        for m in messages:
            m_id = m.get('id') or f"msg_{uuid.uuid4().hex[:8]}"
            m_role = 'assistant' if m.get('role') in ['assistant', 'bot'] else 'user'
            m_content = m.get('content', '')
            m_topic = m.get('topic', session.topic)

            if m_id not in existing_history_ids:
                existing_history_ids.add(m_id)
                new_history_items.append({
                    'id': m_id,
                    'role': m_role,
                    'content': m_content,
                    'topic': m_topic,
                    'timestamp': m.get('timestamp') or timezone.now().isoformat()
                })
            msg_items.append((m_id, m_role, m_content, m_topic))

        if msg_items:
            existing_db_ids = set(ConsultantChatMessage.objects.filter(
                id__in=[item[0] for item in msg_items]
            ).values_list('id', flat=True))

            to_create = [
                ConsultantChatMessage(
                    id=m_id,
                    session=session,
                    sender=m_role,
                    content=m_content,
                    topic=m_topic
                )
                for m_id, m_role, m_content, m_topic in msg_items
                if m_id not in existing_db_ids
            ]
            if to_create:
                ConsultantChatMessage.objects.bulk_create(to_create, ignore_conflicts=True)

        if new_history_items:
            history.extend(new_history_items)

        session.messages_history = history
        session.message_count = len(history)
        session.save()

        return Response({
            'success': True,
            'session_id': session.session_id,
            'message_count': session.message_count,
            'session': ConsultantChatSessionSerializer(session).data
        }, status=status.HTTP_200_OK)
