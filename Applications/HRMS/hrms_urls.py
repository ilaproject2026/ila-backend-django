from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .hrms_views import (
    StaffProfileViewSet,
    AttendanceLogViewSet,
    HRCandidateViewSet,
    EnterpriseTaskViewSet,
    ApprovalRequestViewSet,
    PayrollSyncView,
)

router = DefaultRouter()
router.register(r'staff', StaffProfileViewSet, basename='staff')
router.register(r'attendance', AttendanceLogViewSet, basename='attendance')
router.register(r'candidates', HRCandidateViewSet, basename='candidate')
router.register(r'tasks', EnterpriseTaskViewSet, basename='task')
router.register(r'approvals', ApprovalRequestViewSet, basename='approval')

urlpatterns = [
    path('payroll/sync-finance/', PayrollSyncView.as_view(), name='payroll-sync'),
    path('', include(router.urls)),
]
