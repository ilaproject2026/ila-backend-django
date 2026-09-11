from django.urls import path, include

v1_patterns = [
    path('', include('Applications.ILA_WEB.urls')),
    # Primary Central Authentication App
    path('auth/', include('Applications.Authentication.auth_urls')),
    path('', include('Applications.BusinessStudio.urls')),
    # Studio & Industry Verticals
    path('studio/', include('Applications.BusinessStudio.StudioCore.studiocore_urls')),
    path('import-export/', include('Applications.ImportExport.urls')),
    path('global-real-estate/', include('Applications.GlobalRealEstate.urls')),
    # Corporate Administration & Dashboard
    path('corporate-admin/', include('Applications.CorporateAdmin.urls')),
    path('centralized-dashboard/', include('Applications.CorporateAdmin.urls')),
    # Next-Generation Modular App Suite (ILA_WEB_NEW)
    path('ila-web-new/', include('Applications.ILA_WEB_NEW.urls')),
    path('web-new/', include('Applications.ILA_WEB_NEW.urls')),
    path('study-abroad/', include('Applications.ILA_WEB_NEW.study_abroad.urls')),
    path('work-study/', include('Applications.ILA_WEB_NEW.work_study.urls')),
    path('work-study-hub/', include('Applications.ILA_WEB_NEW.work_study.urls')),
    path('jobs/', include('Applications.ILA_WEB_NEW.job_search.urls')),
    path('job-search/', include('Applications.ILA_WEB_NEW.job_search.urls')),
    path('communication-engine/', include('Applications.ILA_WEB_NEW.communication_engine.urls')),
    path('intake-tracking/', include('Applications.ILA_WEB_NEW.intake_tracking.urls')),
    path('rewards-plan/', include('Applications.ILA_WEB_NEW.rewards_plan.urls')),
    path('web-new/accounts/', include('Applications.ILA_WEB_NEW.accounts.urls')),
    path('web-new/auth/', include('Applications.ILA_WEB_NEW.accounts.urls')),
    path('', include('Applications.CorporateAdmin.urls')),
]


urlpatterns = [
    # Support both /api/v1/... and /api/...
    path('v1/', include(v1_patterns)),
    path('', include(v1_patterns)),
]