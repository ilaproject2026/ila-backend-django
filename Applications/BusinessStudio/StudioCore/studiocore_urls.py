from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .studiocore_views import ApplicationViewSet, PackageViewSet, AssistantChatView

router = DefaultRouter()
router.register(r'applications', ApplicationViewSet, basename='studio-application')
router.register(r'packages', PackageViewSet, basename='studio-package')

urlpatterns = [
    path('assistant/chat/', AssistantChatView.as_view(), name='studio-assistant-chat'),
    path('', include(router.urls)),
]
