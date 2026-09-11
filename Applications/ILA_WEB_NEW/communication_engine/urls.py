from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CommunicationWorkflowRuleViewSet,
    DispatchLogViewSet,
    ConsultantChatSessionViewSet
)

router = DefaultRouter()
router.register(r'workflows', CommunicationWorkflowRuleViewSet, basename='comm-workflow')
router.register(r'logs', DispatchLogViewSet, basename='comm-log')
router.register(r'chat-sessions', ConsultantChatSessionViewSet, basename='chat-session')

urlpatterns = [
    path('', include(router.urls)),
]
