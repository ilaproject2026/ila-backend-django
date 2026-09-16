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
            .replace('{{portal_link}}', 'https://ila-acc-web-main-11-09-26-lui063n9t-ila13.vercel.app/#student-portal')
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
