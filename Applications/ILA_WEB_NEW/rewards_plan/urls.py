from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RewardPlanViewSet,
    RewardRuleViewSet,
    RewardCatalogItemViewSet,
    RewardRedemptionViewSet,
    BroadcastRewardPromotionAPIView,
)

router = DefaultRouter()
router.register(r"plans", RewardPlanViewSet, basename="reward-plan")
router.register(r"rules", RewardRuleViewSet, basename="reward-rule")
router.register(r"catalog", RewardCatalogItemViewSet, basename="reward-catalog")
router.register(r"redemptions", RewardRedemptionViewSet, basename="reward-redemption")

urlpatterns = [
    path("", include(router.urls)),
    path("broadcast-promo/", BroadcastRewardPromotionAPIView.as_view(), name="broadcast-reward-promo"),
]
