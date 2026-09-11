from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CountryViewSet,
    CollegeViewSet,
    StudyAbroadCourseViewSet,
    StudentApplicationViewSet,
    DocumentChecklistViewSet,
    ConsultantATSTaskViewSet,
    HybridAILogViewSet,
    ProfileMatchAPIView,
    ResumeParserAPIView,
    CountryCategoriesAPIView,
)

router = DefaultRouter()
router.register(r"countries", CountryViewSet, basename="country")
router.register(r"colleges", CollegeViewSet, basename="college")
router.register(r"courses", StudyAbroadCourseViewSet, basename="course")
router.register(r"applications", StudentApplicationViewSet, basename="application")
router.register(r"checklists", DocumentChecklistViewSet, basename="checklist")
router.register(r"ats-tasks", ConsultantATSTaskViewSet, basename="ats-task")
router.register(r"hybrid-logs", HybridAILogViewSet, basename="hybrid-log")

urlpatterns = [
    path("", include(router.urls)),
    path("profile-match/", ProfileMatchAPIView.as_view(), name="study-abroad-profile-match"),
    path("parse-resume/", ResumeParserAPIView.as_view(), name="study-abroad-parse-resume"),
    path("country-categories/", CountryCategoriesAPIView.as_view(), name="study-abroad-country-categories"),
]
