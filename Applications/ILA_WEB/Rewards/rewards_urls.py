from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .rewards_views import ReferralRecordViewSet, TierRuleViewSet

router = DefaultRouter()
router.register(r'referrals', ReferralRecordViewSet, basename='referral')
router.register(r'tiers', TierRuleViewSet, basename='tier-rules')

urlpatterns = [
    path('', include(router.urls)),
]
