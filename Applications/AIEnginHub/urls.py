from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CourseViewSet, PermanentCourseViewSet, CategoryViewSet,
    ChatSessionViewSet, ChatMessageViewSet, LegacyChatHistoryViewSet,
    TieupLeadViewSet, PolicyViewSet, OutreachLogViewSet, SmtpConfigurationViewSet,
    VerifySmtpView, SendSingleSmtpView, DispatchSmtpBatchView,
    RegionalTTSProxyView, AIGenerateProxyView, CourseDocxExportView,
    HealthCheckView, DashboardStatsView,
    PresetViewSet, GenerationJobViewSet, TelemetryViewSet
)

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='ai-hub-courses')
router.register(r'permanent-courses', PermanentCourseViewSet, basename='ai-hub-permanent-courses')
router.register(r'categories', CategoryViewSet, basename='ai-hub-categories')
router.register(r'sessions', ChatSessionViewSet, basename='ai-hub-sessions')
router.register(r'messages', ChatMessageViewSet, basename='ai-hub-messages')
router.register(r'chat-history', LegacyChatHistoryViewSet, basename='ai-hub-chat-history')
router.register(r'tieup-leads', TieupLeadViewSet, basename='ai-hub-tieup-leads')
router.register(r'tieup-policies', PolicyViewSet, basename='ai-hub-tieup-policies')
router.register(r'tieup-outreach-logs', OutreachLogViewSet, basename='ai-hub-tieup-outreach-logs')
router.register(r'outreach-logs', OutreachLogViewSet, basename='ai-hub-outreach-logs')
router.register(r'smtp-configs', SmtpConfigurationViewSet, basename='ai-hub-smtp-configs')
router.register(r'presets', PresetViewSet, basename='ai-hub-presets')
router.register(r'generation-jobs', GenerationJobViewSet, basename='ai-hub-generation-jobs')
router.register(r'telemetry', TelemetryViewSet, basename='ai-hub-telemetry')

urlpatterns = [
    # Health & Telemetry
    path('health/', HealthCheckView.as_view(), name='ai-hub-health'),
    path('dashboard/stats/', DashboardStatsView.as_view(), name='ai-hub-dashboard-stats'),

    # Regional Low-Latency Audio Streaming Proxy
    path('tts/', RegionalTTSProxyView.as_view(), name='ai-hub-tts-stream'),

    # Universal Google Gemini AI Generation Proxy (17 Tools)
    path('ai/generate/', AIGenerateProxyView.as_view(), name='ai-hub-generate'),
    path('ai/execute/', AIGenerateProxyView.as_view(), name='ai-hub-execute'),

    # Standalone DOCX Export
    path('courses/<str:pk>/export-docx/', CourseDocxExportView.as_view(), name='ai-hub-course-export-docx-pk'),
    path('export-docx/', CourseDocxExportView.as_view(), name='ai-hub-export-docx'),

    # Email & Outreach Verification & Dispatches
    path('outreach/verify-smtp/', VerifySmtpView.as_view(), name='ai-hub-verify-smtp'),
    path('outreach/send-single/', SendSingleSmtpView.as_view(), name='ai-hub-send-single'),
    path('outreach/send-single-smtp/', SendSingleSmtpView.as_view(), name='ai-hub-send-single-smtp'),
    path('outreach/dispatch-batch/', DispatchSmtpBatchView.as_view(), name='ai-hub-dispatch-batch'),
    path('outreach/dispatch-smtp/', DispatchSmtpBatchView.as_view(), name='ai-hub-dispatch-smtp'),

    # Router ViewSets
    path('', include(router.urls)),
]
