from django.urls import path, include

v1_patterns = [
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
    # ILA_APP Modular App Suite (Study Abroad, Work-Study, Jobs, Comm Engine, Intake, Rewards)
    path('ila-app/', include('Applications.ILA_APP.urls')),
    path('app/', include('Applications.ILA_APP.urls')),
    path('study-abroad/', include('Applications.ILA_APP.study_abroad.urls')),
    path('work-study/', include('Applications.ILA_APP.work_study.urls')),
    path('work-study-hub/', include('Applications.ILA_APP.work_study.urls')),
    path('jobs/', include('Applications.ILA_APP.job_search.urls')),
    path('job-search/', include('Applications.ILA_APP.job_search.urls')),
    path('communication-engine/', include('Applications.ILA_APP.communication_engine.urls')),
    path('communication/', include('Applications.ILA_APP.communication_engine.urls')),
    path('intake-tracking/', include('Applications.ILA_APP.intake_tracking.urls')),
    path('intake/', include('Applications.ILA_APP.intake_tracking.urls')),
    path('rewards-plan/', include('Applications.ILA_APP.rewards_plan.urls')),
    path('rewards/', include('Applications.ILA_APP.rewards_plan.urls')),
    # ILA AI Engine Hub & Course Creator Ecosystem
    path('ai-engine/', include('Applications.AIEnginHub.urls')),
    path('ai-hub/', include('Applications.AIEnginHub.urls')),
    path('', include('Applications.AIEnginHub.urls')),
    path('', include('Applications.CorporateAdmin.urls')),
]


urlpatterns = [
    # Support both /api/v1/... and /api/...
    path('v1/', include(v1_patterns)),
    path('', include(v1_patterns)),
]