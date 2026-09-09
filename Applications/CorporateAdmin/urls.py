from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    LoginView, CurrentUserView, SwitchRoleView,
    OrganizationViewSet, BranchViewSet, DepartmentViewSet, TeamViewSet,
    EmployeeViewSet, InquiryViewSet, LeadViewSet, OpportunityViewSet,
    CandidateViewSet, OnboardingViewSet, TaskViewSet, ApprovalViewSet,
    ExpenseViewSet, FinanceSummaryView, CampaignViewSet,
    NotificationViewSet, AuditLogViewSet,
    AnalyticsDashboardView, ExecutiveDashboardAnalyticsView,
    AnalyticsActivityStreamView, AnalyticsReportsView
)

router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'branches', BranchViewSet, basename='branch')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'inquiries', InquiryViewSet, basename='inquiry')
router.register(r'leads', LeadViewSet, basename='lead')
router.register(r'opportunities', OpportunityViewSet, basename='opportunity')
router.register(r'candidates', CandidateViewSet, basename='candidate')
router.register(r'onboarding', OnboardingViewSet, basename='onboarding')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'approvals', ApprovalViewSet, basename='approval')
router.register(r'expenses', ExpenseViewSet, basename='expense')
router.register(r'campaigns', CampaignViewSet, basename='campaign')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'audit/logs', AuditLogViewSet, basename='audit-log')

urlpatterns = [
    # Auth endpoints
    path('auth/login/', LoginView.as_view(), name='corporate-auth-login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='corporate-auth-refresh'),
    path('auth/me/', CurrentUserView.as_view(), name='corporate-auth-me'),
    path('auth/switch-role/', SwitchRoleView.as_view(), name='corporate-auth-switch-role'),

    # Finance summary
    path('finance/summary/', FinanceSummaryView.as_view(), name='corporate-finance-summary'),

    # Analytics & Dashboard
    path('analytics/dashboard/', ExecutiveDashboardAnalyticsView.as_view(), name='corporate-analytics-dashboard'),
    path('analytics/activity-stream/', AnalyticsActivityStreamView.as_view(), name='corporate-analytics-activity-stream'),
    path('analytics/reports/', AnalyticsReportsView.as_view(), name='corporate-analytics-reports'),

    # Backward compatibility alias for tests and prior blueprints
    path('centelized/dashboard/', AnalyticsDashboardView.as_view(), name='centelized-analytics-dashboard'),

    # Router ViewSets
    path('', include(router.urls)),
]
