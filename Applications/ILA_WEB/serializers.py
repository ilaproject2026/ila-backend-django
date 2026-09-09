from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from .models import (
    FranchisePartner, Inquiry, FollowUpRecord,
    PartnerInstitution, TieUpOutreachLog, MarketingCampaign,
    FieldVisitLog, DepartmentMeeting, RewardProfile, RewardTransaction,
    WorkStudyApplication, VisaRequirementRule, SettlementServiceRequest,
    EnterpriseTask, AttendanceLog, ApprovalRequest
)

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'name': getattr(self.user, 'get_full_name', lambda: self.user.username)() or self.user.username,
            'role': getattr(self.user, 'role', 'Super Admin'),
            'department': getattr(self.user, 'department', ''),
            'is_biometric_authorized': getattr(self.user, 'is_biometric_authorized', False),
        }
        return data


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'name',
            'role', 'department', 'phone', 'hr_issued_id', 'status',
            'hr_approval_status', 'is_biometric_authorized'
        ]
        read_only_fields = ['id']

    def get_name(self, obj):
        if hasattr(obj, 'get_full_name'):
            return obj.get_full_name()
        return obj.username


class FranchisePartnerSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = FranchisePartner
        fields = '__all__'


class FollowUpRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowUpRecord
        fields = '__all__'


class InquirySerializer(serializers.ModelSerializer):
    follow_ups = FollowUpRecordSerializer(many=True, read_only=True)

    class Meta:
        model = Inquiry
        fields = '__all__'


class PartnerInstitutionSerializer(serializers.ModelSerializer):
    outreach_logs_count = serializers.IntegerField(source='outreach_logs.count', read_only=True)

    class Meta:
        model = PartnerInstitution
        fields = '__all__'


class TieUpOutreachLogSerializer(serializers.ModelSerializer):
    partner_name = serializers.CharField(source='partner.name', read_only=True)
    dispatched_by_name = serializers.CharField(source='dispatched_by.get_full_name', read_only=True)

    class Meta:
        model = TieUpOutreachLog
        fields = '__all__'


class MarketingCampaignSerializer(serializers.ModelSerializer):
    roi = serializers.SerializerMethodField()

    class Meta:
        model = MarketingCampaign
        fields = '__all__'

    def get_roi(self, obj):
        if obj.spent and obj.spent > 0:
            return round(float(obj.conversions_count * 199) / float(obj.spent), 2)
        return 0.0


class FieldVisitLogSerializer(serializers.ModelSerializer):
    logged_by_name = serializers.CharField(source='logged_by.get_full_name', read_only=True)

    class Meta:
        model = FieldVisitLog
        fields = '__all__'


class DepartmentMeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentMeeting
        fields = '__all__'


class RewardTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RewardTransaction
        fields = '__all__'


class RewardProfileSerializer(serializers.ModelSerializer):
    transactions = RewardTransactionSerializer(many=True, read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = RewardProfile
        fields = '__all__'


class WorkStudyApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkStudyApplication
        fields = '__all__'


class VisaRequirementRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisaRequirementRule
        fields = '__all__'


class SettlementServiceRequestSerializer(serializers.ModelSerializer):
    coordinator_name = serializers.CharField(source='assigned_coordinator.get_full_name', read_only=True)

    class Meta:
        model = SettlementServiceRequest
        fields = '__all__'


class EnterpriseTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnterpriseTask
        fields = '__all__'


class AttendanceLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceLog
        fields = '__all__'


class ApprovalRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalRequest
        fields = '__all__'
