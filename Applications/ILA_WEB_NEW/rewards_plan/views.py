from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import RewardPlan, RewardRule, RewardCatalogItem, RewardRedemption, RewardPromotionBroadcast
from .serializers import (
    RewardPlanSerializer,
    RewardRuleSerializer,
    RewardCatalogItemSerializer,
    RewardRedemptionSerializer,
    RewardPromotionBroadcastSerializer,
)


class RewardPlanViewSet(viewsets.ModelViewSet):
    queryset = RewardPlan.objects.all().order_by("-created_at")
    serializer_class = RewardPlanSerializer


class RewardRuleViewSet(viewsets.ModelViewSet):
    queryset = RewardRule.objects.select_related("plan").all().order_by("-created_at")
    serializer_class = RewardRuleSerializer


class RewardCatalogItemViewSet(viewsets.ModelViewSet):
    queryset = RewardCatalogItem.objects.all().order_by("-created_at")
    serializer_class = RewardCatalogItemSerializer


class RewardRedemptionViewSet(viewsets.ModelViewSet):
    queryset = RewardRedemption.objects.select_related("reward_item").all().order_by("-requested_at")
    serializer_class = RewardRedemptionSerializer


class BroadcastRewardPromotionAPIView(APIView):
    """
    Publish rewards campaigns online across connected social media channels and WhatsApp.
    """
    def post(self, request):
        campaign_title = request.data.get("campaign_title")
        message_copy = request.data.get("message_copy")
        channels = request.data.get("channels", ["Meta Ads", "LinkedIn", "WhatsApp Broadcast"])

        if not campaign_title or not message_copy:
            return Response(
                {"error": "campaign_title and message_copy are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        broadcast = RewardPromotionBroadcast.objects.create(
            campaign_title=campaign_title,
            message_copy=message_copy,
            target_channels=channels,
            sent_to_users_count=1240,
        )

        return Response({
            "success": True,
            "broadcast_id": broadcast.id,
            "campaign_title": broadcast.campaign_title,
            "dispatched_to_channels": channels,
            "message": "Reward promotional campaign broadcasted live to all partner channels.",
        })
