from rest_framework import serializers
from .studiocore_models import Application, PackageTier


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = [
            'id',
            'full_name',
            'email',
            'business_name',
            'industry',
            'package_option',
            'status',
            'notes',
            'created_at',
        ]
        read_only_fields = ['id', 'status', 'created_at']

    def validate_email(self, value):
        if not value or '@' not in value:
            raise serializers.ValidationError("Please provide a valid corporate email address.")
        return value.lower()


class PackageTierSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='slug', read_only=True)
    shareCapital = serializers.CharField(source='share_capital')
    setupFee = serializers.CharField(source='setup_fee')
    monthlyFee = serializers.CharField(source='monthly_fee')

    class Meta:
        model = PackageTier
        fields = [
            'id',
            'name',
            'subtitle',
            'shareCapital',
            'setupFee',
            'ownership',
            'monthlyFee',
            'features',
            'highlight',
        ]


class AssistantChatSerializer(serializers.Serializer):
    prompt = serializers.CharField(required=True, max_length=3000)
    session_id = serializers.CharField(required=False, allow_blank=True, default="default-session")
    history = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list
    )
