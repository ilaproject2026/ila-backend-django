from rest_framework import serializers
from .hrms_models import (
    StaffProfile,
    AttendanceLog,
    HRCandidate,
    EnterpriseTask,
    ApprovalRequest,
)


class StaffProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    fullname = serializers.CharField(source='user.fullname', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    role = serializers.CharField(source='user.role', read_only=True)

    class Meta:
        model = StaffProfile
        fields = '__all__'


class AttendanceLogSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source='staff.user.fullname', read_only=True)
    employee_id = serializers.CharField(source='staff.employee_id', read_only=True)

    class Meta:
        model = AttendanceLog
        fields = '__all__'


class HRCandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HRCandidate
        fields = '__all__'


class EnterpriseTaskSerializer(serializers.ModelSerializer):
    assigned_staff_name = serializers.CharField(source='assigned_staff.fullname', read_only=True)

    class Meta:
        model = EnterpriseTask
        fields = '__all__'


class ApprovalRequestSerializer(serializers.ModelSerializer):
    requested_by_name = serializers.CharField(source='requested_by.fullname', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.fullname', read_only=True)

    class Meta:
        model = ApprovalRequest
        fields = '__all__'
