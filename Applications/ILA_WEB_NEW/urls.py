from django.urls import path, include

urlpatterns = [
    # Auth & Accounts
    path('auth/', include('Applications.ILA_WEB_NEW.accounts.urls')),
    path('accounts/', include('Applications.ILA_WEB_NEW.accounts.urls')),

    # Communication Engine
    path('communication/', include('Applications.ILA_WEB_NEW.communication_engine.urls')),
    path('communication-engine/', include('Applications.ILA_WEB_NEW.communication_engine.urls')),

    # Intake Tracking & Department Inquiries
    # path('intake/', include('Applications.ILA_WEB_NEW.intake_tracking.urls')),
    path('intake-tracking/', include('Applications.ILA_WEB_NEW.intake_tracking.urls')),

    # Job Search, Matches & Candidate Resumes
    path('jobs/', include('Applications.ILA_WEB_NEW.job_search.urls')),
    path('job-search/', include('Applications.ILA_WEB_NEW.job_search.urls')),

    # Rewards Plan, Catalog & Redemptions
    path('rewards/', include('Applications.ILA_WEB_NEW.rewards_plan.urls')),
    path('rewards-plan/', include('Applications.ILA_WEB_NEW.rewards_plan.urls')),

    # Study Abroad, Countries, Colleges, Courses & ATS
    path('study-abroad/', include('Applications.ILA_WEB_NEW.study_abroad.urls')),

    # Work & Study Packages & Candidates
    path('work-study/', include('Applications.ILA_WEB_NEW.work_study.urls')),
]
