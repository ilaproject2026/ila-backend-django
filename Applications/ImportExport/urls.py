from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ImporterViewSet,
    ExporterViewSet,
    RFQViewSet,
    TransactionViewSet,
    CeoApprovalViewSet,
    ComplianceViewSet,
    StaffMemberViewSet,
    JobVacancyViewSet,
    LedgerEntryViewSet,
    TreasuryReserveViewSet,
    StrategicTieupViewSet,
    ArticleViewSet,
    DemandItemViewSet,
    PortalMetricsView,
    GovernanceSettingsView,
)

router = DefaultRouter()
router.register(r'importers', ImporterViewSet, basename='importers')
router.register(r'exporters', ExporterViewSet, basename='exporters')
router.register(r'rfqs', RFQViewSet, basename='rfqs')
router.register(r'transactions', TransactionViewSet, basename='transactions')
router.register(r'ceo/approvals', CeoApprovalViewSet, basename='ceo-approvals')
router.register(r'compliance/sanctions', ComplianceViewSet, basename='compliance-sanctions')
router.register(r'hr/staff', StaffMemberViewSet, basename='hr-staff')
router.register(r'hr/vacancies', JobVacancyViewSet, basename='hr-vacancies')
router.register(r'accounts/ledger', LedgerEntryViewSet, basename='accounts-ledger')
router.register(r'accounts/treasury', TreasuryReserveViewSet, basename='accounts-treasury')
router.register(r'tieups', StrategicTieupViewSet, basename='tieups')
router.register(r'portal/articles', ArticleViewSet, basename='portal-articles')
router.register(r'portal/demands', DemandItemViewSet, basename='portal-demands')

urlpatterns = [
    path('portal/metrics/', PortalMetricsView.as_view(), name='portal-metrics'),
    path('settings/', GovernanceSettingsView.as_view(), name='governance-settings'),
    path('', include(router.urls)),
]
