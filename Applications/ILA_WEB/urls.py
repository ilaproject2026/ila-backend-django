from django.urls import path, include

urlpatterns = [
    path('frontoffice/', include('Applications.ILA_WEB.FrontOffice.frontoffice_urls')),
    path('academics/', include('Applications.ILA_WEB.Academics.academics_urls')),
    path('hrms/', include('Applications.ILA_WEB.HRMS.hrms_urls')),
    path('finance/', include('Applications.ILA_WEB.Finance.finance_urls')),
    path('rewards/', include('Applications.ILA_WEB.Rewards.rewards_urls')),
    path('ai/', include('Applications.ILA_WEB.AIEngine.ai_urls')),
]
