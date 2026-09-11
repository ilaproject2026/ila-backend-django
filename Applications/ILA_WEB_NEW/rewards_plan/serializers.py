from rest_framework import serializers
from .models import RewardPlan, RewardRule, RewardCatalogItem, RewardRedemption, RewardPromotionBroadcast


class RewardPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = RewardPlan
        fields = "__all__"


class RewardRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RewardRule
        fields = "__all__"


class RewardCatalogItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = RewardCatalogItem
        fields = "__all__"


class RewardRedemptionSerializer(serializers.ModelSerializer):
    reward_item_title = serializers.CharField(source="reward_item.title", read_only=True)

    class Meta:
        model = RewardRedemption
        fields = "__all__"


class RewardPromotionBroadcastSerializer(serializers.ModelSerializer):
    class Meta:
        model = RewardPromotionBroadcast
        fields = "__all__"
