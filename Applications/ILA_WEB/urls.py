from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomLoginView, RegisterView, CurrentUserView,
    StaffViewSet, FranchiseViewSet, InquiryViewSet, FollowUpRecordViewSet,
    PartnerInstitutionViewSet, TieUpOutreachLogViewSet, MarketingCampaignViewSet,
    FieldVisitLogViewSet, DepartmentMeetingViewSet, RewardProfileViewSet,
    RewardTransactionViewSet, WorkStudyApplicationViewSet,
    VisaRequirementRuleViewSet, SettlementServiceViewSet,
    EnterpriseTaskViewSet, AttendanceViewSet, ApprovalViewSet
)

router = DefaultRouter()
# Central 12 Blueprint ViewSets
router.register(r'staff', StaffViewSet, basename='staff')
router.register(r'franchises', FranchiseViewSet, basename='franchises')
router.register(r'inquiries', InquiryViewSet, basename='inquiries')
router.register(r'partners', PartnerInstitutionViewSet, basename='partners')
router.register(r'campaigns', MarketingCampaignViewSet, basename='campaigns')
router.register(r'rewards', RewardProfileViewSet, basename='rewards')
router.register(r'work-study-applications', WorkStudyApplicationViewSet, basename='work-study')
router.register(r'visa-rules', VisaRequirementRuleViewSet, basename='visa-rules')
router.register(r'settlement-requests', SettlementServiceViewSet, basename='settlement')
router.register(r'tasks', EnterpriseTaskViewSet, basename='tasks')
router.register(r'attendance', AttendanceViewSet, basename='attendance')
router.register(r'approvals', ApprovalViewSet, basename='approvals')

# Extended Auxiliary ViewSets
router.register(r'follow-ups', FollowUpRecordViewSet, basename='follow-ups')
router.register(r'outreach-logs', TieUpOutreachLogViewSet, basename='outreach-logs')
router.register(r'field-visits', FieldVisitLogViewSet, basename='field-visits')
router.register(r'department-meetings', DepartmentMeetingViewSet, basename='department-meetings')
router.register(r'reward-transactions', RewardTransactionViewSet, basename='reward-transactions')

urlpatterns = [
    # Authentication Endpoints (Part 6 & 7)
    path('auth/login/', CustomLoginView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', RegisterView.as_view(), name='auth_register'),
    path('auth/me/', CurrentUserView.as_view(), name='current_user'),

    # Live AI Consultant Endpoints (Gemini Live Consultant)
    path('consultant/', include('Applications.ILA_WEB.IlaConsultant.urls')),
    path('ila-consultant/', include('Applications.ILA_WEB.IlaConsultant.urls')),

    # Central REST API Endpoints
    path('', include(router.urls)),
]


