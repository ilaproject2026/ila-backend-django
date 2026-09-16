from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DepartmentInquiryViewSet,
    FollowUpAutoTriggerRuleViewSet,
    SocialMediaCampaignViewSet,
)

router = DefaultRouter()
router.register(r"inquiries", DepartmentInquiryViewSet, basename="department-inquiry")
router.register(r"triggers", FollowUpAutoTriggerRuleViewSet, basename="followup-trigger")
router.register(r"campaigns", SocialMediaCampaignViewSet, basename="social-campaign")

urlpatterns = [
    path("", include(router.urls)),
]
