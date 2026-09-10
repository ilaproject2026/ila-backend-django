from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ConsultantChatAPIView,
    ConsultantSessionViewSet,
    ConsultantChatView,
    TokenAnalyticsSummaryView,
)

router = DefaultRouter()
router.register(r'sessions', ConsultantSessionViewSet, basename='consultant-sessions')

urlpatterns = [
    path('chat/', ConsultantChatAPIView.as_view(), name='consultant-chat'),
    path('legacy-chat/', ConsultantChatView.as_view(), name='consultant-chat-legacy'),
    path('tokens/summary/', TokenAnalyticsSummaryView.as_view(), name='token-analytics-summary'),
    path('', include(router.urls)),
]

