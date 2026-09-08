from django.contrib import admin
from .models import (
    Importer,
    Exporter,
    RFQ,
    RFQProposal,
    Transaction,
    SmartVault,
    VaultSignature,
    AisTelemetry,
    ConsignmentDocument,
    CeoApproval,
    SanctionsLog,
    StaffMember,
    JobVacancy,
    LedgerEntry,
    TreasuryReserve,
    StrategicTieup,
    Article,
    DemandItem,
)


@admin.register(Importer)
class ImporterAdmin(admin.ModelAdmin):
    list_display = ('reference_id', 'name', 'country', 'tier', 'annual_volume_usd', 'status')
    search_fields = ('name', 'reference_id', 'country', 'contact_person')
    list_filter = ('tier', 'country', 'status')


@admin.register(Exporter)
class ExporterAdmin(admin.ModelAdmin):
    list_display = ('reference_id', 'name', 'country', 'tier', 'annual_export_capacity_usd', 'status')
    search_fields = ('name', 'reference_id', 'country', 'contact_person')
    list_filter = ('tier', 'country', 'status')


class RFQProposalInline(admin.TabularInline):
    model = RFQProposal
    extra = 0


@admin.register(RFQ)
class RFQAdmin(admin.ModelAdmin):
    list_display = ('reference_id', 'title', 'buyer', 'target_budget_usd', 'status', 'created_at')
    search_fields = ('reference_id', 'title', 'hs_code')
    list_filter = ('status', 'incoterm')
    inlines = [RFQProposalInline]


class VaultSignatureInline(admin.TabularInline):
    model = VaultSignature
    extra = 0


@admin.register(SmartVault)
class SmartVaultAdmin(admin.ModelAdmin):
    list_display = ('contract_address', 'transaction', 'funds_locked_usd', 'funds_released_usd')
    inlines = [VaultSignatureInline]


class ConsignmentDocumentInline(admin.TabularInline):
    model = ConsignmentDocument
    extra = 0


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('reference_id', 'title', 'buyer', 'seller', 'amount_usd', 'stage_index', 'status_badge')
    search_fields = ('reference_id', 'title', 'bill_of_lading', 'buyer', 'seller')
    list_filter = ('stage_index', 'status_badge')
    inlines = [ConsignmentDocumentInline]


@admin.register(AisTelemetry)
class AisTelemetryAdmin(admin.ModelAdmin):
    list_display = ('vessel_name', 'transaction', 'coordinates', 'current_speed_knots', 'heading')


@admin.register(CeoApproval)
class CeoApprovalAdmin(admin.ModelAdmin):
    list_display = ('reference_id', 'title', 'buyer', 'seller', 'value_usd', 'status', 'urgent')
    search_fields = ('reference_id', 'title', 'buyer', 'seller')
    list_filter = ('status', 'urgent', 'department')


@admin.register(SanctionsLog)
class SanctionsLogAdmin(admin.ModelAdmin):
    list_display = ('reference_id', 'entity_name', 'country', 'risk_score', 'status', 'created_at')
    search_fields = ('reference_id', 'entity_name', 'certificate_hash')
    list_filter = ('status', 'country')


@admin.register(StaffMember)
class StaffMemberAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'name', 'role', 'department', 'status', 'clearance_level')
    search_fields = ('employee_id', 'name', 'email', 'role')
    list_filter = ('department', 'status', 'clearance_level')


@admin.register(JobVacancy)
class JobVacancyAdmin(admin.ModelAdmin):
    list_display = ('reference_id', 'title', 'department', 'location', 'urgency', 'applicants_count')


@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = ('reference_id', 'tx_ref', 'entry_type', 'amount_usd', 'fee_earned_usd', 'status')
    search_fields = ('reference_id', 'tx_ref', 'ledger_hash')
    list_filter = ('entry_type', 'category', 'status')


@admin.register(TreasuryReserve)
class TreasuryReserveAdmin(admin.ModelAdmin):
    list_display = ('currency', 'name', 'balance_formatted', 'balance_usd', 'share_percent', 'bank')


@admin.register(StrategicTieup)
class StrategicTieupAdmin(admin.ModelAdmin):
    list_display = ('reference_id', 'partner_name', 'partner_type', 'country', 'status')


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'read_time', 'is_featured', 'published_at')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(DemandItem)
class DemandItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'hs_code', 'origin_country', 'destination_country', 'volume', 'budget_usd', 'status')
