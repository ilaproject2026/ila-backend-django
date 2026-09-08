from django.contrib import admin
from .models import (
    Landlord,
    MasterLease,
    Property,
    Room,
    TenantUser,
    DocumentRecord,
    PlacedTenantReferral,
    ProfitShareLedgerEntry,
    DutyRosterTask,
    HygienePenalty,
    ERPInvoice,
    ERPStaff,
    ERPKanbanTask,
    MaintenanceTicket,
    BrokerRecord,
    MarketingCampaign,
    CommercialDeal,
    SupplyProduct,
    ComplianceItem,
    ExpansionHubKPI,
)


@admin.register(Landlord)
class LandlordAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'company_name', 'country', 'created_at')
    search_fields = ('full_name', 'email', 'company_name')


class RoomInline(admin.TabularInline):
    model = Room
    extra = 0


@admin.register(MasterLease)
class MasterLeaseAdmin(admin.ModelAdmin):
    list_display = ('building_name', 'generated_property_uid', 'city_name', 'monthly_master_rent', 'currency', 'status')
    search_fields = ('building_name', 'generated_property_uid', 'city_name', 'landlord_name')
    list_filter = ('status', 'city_code', 'currency')


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'property_uid', 'city', 'total_rooms', 'active_occupancy', 'featured', 'syndication_active')
    search_fields = ('title', 'property_uid', 'city', 'country')
    list_filter = ('city_code', 'featured', 'syndication_active')
    inlines = [RoomInline]


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_uid', 'property', 'room_number', 'room_type', 'regular_rent_amount', 'micro_investor_rent_amount', 'is_available')
    search_fields = ('room_uid', 'room_number', 'property__title')
    list_filter = ('room_type', 'is_available', 'currency')


class DocumentRecordInline(admin.TabularInline):
    model = DocumentRecord
    extra = 0


class PlacedTenantReferralInline(admin.TabularInline):
    model = PlacedTenantReferral
    extra = 0


class ProfitShareLedgerEntryInline(admin.TabularInline):
    model = ProfitShareLedgerEntry
    extra = 0


@admin.register(TenantUser)
class TenantUserAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'referral_code', 'option_type', 'property_title', 'wallet_balance', 'hygiene_score')
    search_fields = ('full_name', 'email', 'referral_code', 'property_title')
    list_filter = ('option_type', 'role')
    inlines = [DocumentRecordInline, PlacedTenantReferralInline, ProfitShareLedgerEntryInline]


@admin.register(DutyRosterTask)
class DutyRosterTaskAdmin(admin.ModelAdmin):
    list_display = ('assigned_zone', 'property_title', 'tenant_name', 'scheduled_date', 'status', 'penalty_amount')
    search_fields = ('assigned_zone', 'tenant_name', 'property_title')
    list_filter = ('status', 'scheduled_date')


@admin.register(HygienePenalty)
class HygienePenaltyAdmin(admin.ModelAdmin):
    list_display = ('tenant_name', 'property_uid', 'penalty_amount', 'currency', 'status', 'logged_at')
    search_fields = ('tenant_name', 'property_uid', 'reason')
    list_filter = ('status', 'currency')


@admin.register(ERPInvoice)
class ERPInvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'recipient_name', 'property_uid', 'amount', 'currency', 'category', 'status')
    search_fields = ('invoice_number', 'recipient_name', 'property_uid')
    list_filter = ('status', 'category')


@admin.register(ERPStaff)
class ERPStaffAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'department', 'hub', 'email', 'active_tasks_count')
    search_fields = ('name', 'role', 'email')
    list_filter = ('department', 'hub')


@admin.register(ERPKanbanTask)
class ERPKanbanTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'assigned_to_name', 'department', 'priority', 'status', 'due_date')
    search_fields = ('title', 'assigned_to_name', 'property_uid')
    list_filter = ('status', 'priority', 'department')


@admin.register(MaintenanceTicket)
class MaintenanceTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_code', 'title', 'property_uid', 'room_uid', 'priority', 'status', 'cost_estimate')
    search_fields = ('ticket_code', 'title', 'tenant_name')
    list_filter = ('status', 'priority', 'category')


@admin.register(BrokerRecord)
class BrokerRecordAdmin(admin.ModelAdmin):
    list_display = ('name', 'agency', 'referral_code', 'total_placements', 'total_commission_paid', 'pending_payout', 'status')
    search_fields = ('name', 'agency', 'referral_code')
    list_filter = ('status',)


@admin.register(MarketingCampaign)
class MarketingCampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'channel', 'target_city', 'budget', 'leads_generated', 'conversions', 'status')
    search_fields = ('title', 'target_segment')
    list_filter = ('status', 'channel')


@admin.register(CommercialDeal)
class CommercialDealAdmin(admin.ModelAdmin):
    list_display = ('deal_code', 'title', 'city', 'country', 'total_acquisition_cost', 'expected_cap_rate_pct', 'status')
    search_fields = ('deal_code', 'title', 'city')
    list_filter = ('status', 'country')


@admin.register(SupplyProduct)
class SupplyProductAdmin(admin.ModelAdmin):
    list_display = ('sku', 'name', 'category', 'unit_price', 'in_stock', 'reorder_point', 'status')
    search_fields = ('sku', 'name')
    list_filter = ('status', 'category')


@admin.register(ComplianceItem)
class ComplianceItemAdmin(admin.ModelAdmin):
    list_display = ('property_uid', 'jurisdiction', 'regulation_type', 'status', 'next_audit_date')
    search_fields = ('property_uid', 'regulation_type', 'legal_counsel')
    list_filter = ('status', 'jurisdiction')


@admin.register(ExpansionHubKPI)
class ExpansionHubKPIAdmin(admin.ModelAdmin):
    list_display = ('city', 'country', 'region', 'active_properties', 'total_beds', 'occupancy_rate_pct', 'growth_potential')
    search_fields = ('city', 'country')
    list_filter = ('region', 'growth_potential')
