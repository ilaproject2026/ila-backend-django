from rest_framework import serializers
from .frontoffice_models import Inquiry, FollowUpRecord, VisitorLog


class FollowUpRecordSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source='staff.fullname', read_only=True)

    class Meta:
        model = FollowUpRecord
        fields = '__all__'


class InquirySerializer(serializers.ModelSerializer):
    follow_up_history = FollowUpRecordSerializer(many=True, read_only=True)
    assigned_staff_name = serializers.CharField(source='assigned_staff.fullname', read_only=True)

    class Meta:
        model = Inquiry
        fields = '__all__'
        read_only_fields = ['id', 'token_number', 'created_at', 'updated_at']


class VisitorLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitorLog
        fields = '__all__'


class InquiryPaymentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=True)
    payment_status = serializers.ChoiceField(choices=Inquiry.PAYMENT_STATUS_CHOICES, default='Paid')
    notes = serializers.CharField(required=False, allow_blank=True)
