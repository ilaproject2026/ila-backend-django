from django.urls import path
from .views import ConsultantChatView, TokenAnalyticsSummaryView

urlpatterns = [
    path('chat/', ConsultantChatView.as_view(), name='consultant-chat'),
    path('tokens/summary/', TokenAnalyticsSummaryView.as_view(), name='token-analytics-summary'),
]
