from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkStudyPackageViewSet, WorkStudyCandidateViewSet

router = DefaultRouter()
router.register(r'packages', WorkStudyPackageViewSet, basename='work-study-package')
router.register(r'candidates', WorkStudyCandidateViewSet, basename='work-study-candidate')

urlpatterns = [
    path('', include(router.urls)),
]
