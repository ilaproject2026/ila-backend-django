from rest_framework import serializers
from .models import DepartmentInquiry, FollowUpAutoTriggerRule, SocialMediaCampaign


class DepartmentInquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentInquiry
        fields = "__all__"


class FollowUpAutoTriggerRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowUpAutoTriggerRule
        fields = "__all__"


class SocialMediaCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMediaCampaign
        fields = "__all__"
