from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .frontoffice_views import InquiryViewSet, VisitorLogCreateView

router = DefaultRouter()
router.register(r'inquiries', InquiryViewSet, basename='inquiry')

urlpatterns = [
    path('visitor-log/', VisitorLogCreateView.as_view(), name='visitor-log'),
    path('', include(router.urls)),
]
