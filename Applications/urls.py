from django.urls import path, include

v1_patterns = [
    path('auth/', include('Applications.Authentication.auth_urls')),
    path('frontoffice/', include('Applications.FrontOffice.frontoffice_urls')),
    path('academics/', include('Applications.Academics.academics_urls')),
    path('hrms/', include('Applications.HRMS.hrms_urls')),
    path('finance/', include('Applications.Finance.finance_urls')),
    path('rewards/', include('Applications.Rewards.rewards_urls')),
    path('ai/', include('Applications.AIEngine.ai_urls')),
]

urlpatterns = [
    # Support both /api/v1/... and /api/...
    path('v1/', include(v1_patterns)),
    path('', include(v1_patterns)),
]