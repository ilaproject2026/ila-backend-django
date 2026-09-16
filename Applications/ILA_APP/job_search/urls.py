from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PartnerCompanyViewSet,
    JobListingViewSet,
    CandidateResumeViewSet,
    JobMatchViewSet,
)

router = DefaultRouter()
router.register(r"companies", PartnerCompanyViewSet, basename="partner-company")
router.register(r"listings", JobListingViewSet, basename="job-listing")
router.register(r"resumes", CandidateResumeViewSet, basename="candidate-resume")
router.register(r"matches", JobMatchViewSet, basename="job-match")

urlpatterns = [
    path("", include(router.urls)),
]
