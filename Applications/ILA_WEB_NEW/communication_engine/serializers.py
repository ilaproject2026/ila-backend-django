from rest_framework import serializers
from .models import (
    CommunicationWorkflowRule,
    DispatchLog,
    ConsultantChatSession,
    ConsultantChatMessage
)


class CommunicationWorkflowRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunicationWorkflowRule
        fields = '__all__'


class DispatchLogSerializer(serializers.ModelSerializer):
    workflow_name = serializers.CharField(source='workflow.name', read_only=True)

    class Meta:
        model = DispatchLog
        fields = '__all__'


class TriggerSimulationSerializer(serializers.Serializer):
    workflow_id = serializers.CharField()
    student_name = serializers.CharField(default='Ananya Sharma')
    student_email = serializers.EmailField(default='ananya.sharma@example.com')
    student_phone = serializers.CharField(default='+91 98765 43210')
    course_track = serializers.CharField(default='German Language B2 Executive Track')


class ConsultantChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultantChatMessage
        fields = ['id', 'session', 'sender', 'content', 'topic', 'timestamp']
        read_only_fields = ['id', 'timestamp']


class ConsultantChatSessionSerializer(serializers.ModelSerializer):
    chat_messages = ConsultantChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = ConsultantChatSession
        fields = [
            'id',
            'session_id',
            'user_name',
            'user_email',
            'user_phone',
            'topic',
            'status',
            'message_count',
            'messages_history',
            'metadata',
            'created_at',
            'updated_at',
            'chat_messages',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
