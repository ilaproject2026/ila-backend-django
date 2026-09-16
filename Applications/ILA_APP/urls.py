from django.urls import path, include

urlpatterns = [
    # Study Abroad: Countries, Colleges, Courses, ATS & Match Engine
    path('study-abroad/', include('Applications.ILA_APP.study_abroad.urls')),

    # Work & Study: Packages, Candidate Intakes & Applications
    path('work-study/', include('Applications.ILA_APP.work_study.urls')),
    path('work-study-hub/', include('Applications.ILA_APP.work_study.urls')),

    # Jobs & Career: Partner Companies, Job Listings, Resumes & Matches
    path('jobs/', include('Applications.ILA_APP.job_search.urls')),
    path('job-search/', include('Applications.ILA_APP.job_search.urls')),

    # Communication Engine: Workflows, Automated Triggers & Dispatch Logs
    path('communication/', include('Applications.ILA_APP.communication_engine.urls')),
    path('communication-engine/', include('Applications.ILA_APP.communication_engine.urls')),

    # Intake Tracking: Department Inquiries & Campaign Triggers
    path('intake/', include('Applications.ILA_APP.intake_tracking.urls')),
    path('intake-tracking/', include('Applications.ILA_APP.intake_tracking.urls')),

    # Rewards Plan: Points Rules, Rewards Catalog, Redemptions & Promos
    path('rewards/', include('Applications.ILA_APP.rewards_plan.urls')),
    path('rewards-plan/', include('Applications.ILA_APP.rewards_plan.urls')),
]
