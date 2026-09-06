from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .academics_views import (
    GlobalCategoryViewSet,
    TeachingStrategyViewSet,
    StudentAnalyzingStrategyViewSet,
    GlobalCourseViewSet,
    GlobalPathViewSet,
    GlobalBatchViewSet,
    ClassScheduleSessionViewSet,
    CourseMaterialViewSet,
    StudentEnrollmentViewSet,
)

router = DefaultRouter()
router.register(r'categories', GlobalCategoryViewSet, basename='academic-category')
router.register(r'strategies/teaching', TeachingStrategyViewSet, basename='teaching-strategy')
router.register(r'strategies/analyzing', StudentAnalyzingStrategyViewSet, basename='analyzing-strategy')
router.register(r'courses', GlobalCourseViewSet, basename='course')
router.register(r'paths', GlobalPathViewSet, basename='path')
router.register(r'batches', GlobalBatchViewSet, basename='batch')
router.register(r'timetable', ClassScheduleSessionViewSet, basename='timetable')
router.register(r'materials', CourseMaterialViewSet, basename='material')
router.register(r'enrollments', StudentEnrollmentViewSet, basename='enrollment')

urlpatterns = [
    path('', include(router.urls)),
]
