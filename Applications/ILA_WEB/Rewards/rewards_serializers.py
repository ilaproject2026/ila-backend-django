from rest_framework import serializers
from .rewards_models import ReferralRecord, TierRule


class ReferralRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralRecord
        fields = '__all__'


class TierRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TierRule
        fields = '__all__'
