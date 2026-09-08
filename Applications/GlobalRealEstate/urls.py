from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    health_check,
    PropertyViewSet,
    RoomViewSet,
    MasterLeaseViewSet,
    TenantViewSet,
    DutyRosterViewSet,
    HygienePenaltyViewSet,
    ERPInvoiceViewSet,
    ERPStaffViewSet,
    ERPKanbanTaskViewSet,
    MaintenanceTicketViewSet,
    BrokerRecordViewSet,
    MarketingCampaignViewSet,
    CommercialDealViewSet,
    SupplyProductViewSet,
    ComplianceItemViewSet,
    ExpansionHubKPIViewSet,
)

router = DefaultRouter()

# 1. Properties & Master Leases
router.register(r'properties', PropertyViewSet, basename='property')
router.register(r'rooms', RoomViewSet, basename='room')
router.register(r'master-leases', MasterLeaseViewSet, basename='master-lease')

# 2. Tenants & Growth Loop
router.register(r'tenants', TenantViewSet, basename='tenant')

# 3. Hygiene & Duty Rosters
router.register(r'duty-rosters', DutyRosterViewSet, basename='duty-roster')
router.register(r'hygiene-penalties', HygienePenaltyViewSet, basename='hygiene-penalty')

# 4. 12-Module Enterprise ERP
router.register(r'invoices', ERPInvoiceViewSet, basename='invoice')
router.register(r'staff', ERPStaffViewSet, basename='staff')
router.register(r'kanban-tasks', ERPKanbanTaskViewSet, basename='kanban-task')
router.register(r'maintenance-tickets', MaintenanceTicketViewSet, basename='maintenance-ticket')
router.register(r'brokers', BrokerRecordViewSet, basename='broker')
router.register(r'campaigns', MarketingCampaignViewSet, basename='campaign')
router.register(r'commercial-deals', CommercialDealViewSet, basename='commercial-deal')
router.register(r'supply-products', SupplyProductViewSet, basename='supply-product')
router.register(r'compliance-audits', ComplianceItemViewSet, basename='compliance-audit')
router.register(r'expansion-hubs', ExpansionHubKPIViewSet, basename='expansion-hub')

urlpatterns = [
    path('health/', health_check, name='global-studio-health-check'),
    path('', include(router.urls)),
]
