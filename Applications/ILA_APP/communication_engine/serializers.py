from rest_framework import serializers
from .models import CommunicationWorkflowRule, DispatchLog

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
