import uuid
from django.db import models
from django.conf import settings


# ==============================================================================
# Choices
# ==============================================================================

class CurrencyChoice(models.TextChoices):
    EUR = 'EUR', 'EUR (€)'
    USD = 'USD', 'USD ($)'
    GBP = 'GBP', 'GBP (£)'
    AED = 'AED', 'AED (د.إ)'
    SGD = 'SGD', 'SGD (S$)'
    JPY = 'JPY', 'JPY (¥)'


class RoomTypeChoice(models.TextChoices):
    PRIVATE_ENSUITE = 'Private Ensuite', 'Private Ensuite'
    COLIVING_STUDIO = 'Co-Living Studio', 'Co-Living Studio'
    MASTER_SUITE = 'Master Suite', 'Master Suite'
    MICRO_POD = 'Micro-Pod Suite', 'Micro-Pod Suite'


class MasterLeaseStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Active'
    PENDING = 'PENDING', 'Pending'
    RENEWAL_DUE = 'RENEWAL_DUE', 'Renewal Due'
    EXPIRED = 'EXPIRED', 'Expired'


class OptionType(models.TextChoices):
    OPTION_A = 'OPTION_A', 'Option A (Standard Market Lease)'
    OPTION_B = 'OPTION_B', 'Option B (Micro-Investor Discounted)'


class DutyRosterStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    SUBMITTED = 'SUBMITTED_FOR_REVIEW', 'Submitted for Review'
    APPROVED = 'APPROVED', 'Approved'
    REJECTED = 'REJECTED_PENALIZED', 'Rejected & Penalized'


# ==============================================================================
# 1. Properties Domain
# ==============================================================================

class Landlord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.country})"


class MasterLease(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    landlord = models.ForeignKey(Landlord, on_delete=models.SET_NULL, null=True, blank=True)
    landlord_name = models.CharField(max_length=255)
    landlord_email = models.EmailField()
    landlord_phone = models.CharField(max_length=50)
    building_name = models.CharField(max_length=255)
    city_code = models.CharField(max_length=10)  # FFM, LDN, DXB, SIN, NYC
    city_name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    address = models.TextField()
    total_floors = models.IntegerField(default=1)
    total_capacity = models.IntegerField()
    monthly_master_rent = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, choices=CurrencyChoice.choices, default=CurrencyChoice.EUR)
    lease_start_date = models.DateField()
    lease_end_date = models.DateField()
    status = models.CharField(max_length=50, choices=MasterLeaseStatus.choices, default=MasterLeaseStatus.ACTIVE)
    generated_property_uid = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.building_name} ({self.generated_property_uid})"


class Property(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    master_lease = models.OneToOneField(MasterLease, on_delete=models.CASCADE, related_name='property_record', null=True, blank=True)
    property_uid = models.CharField(max_length=100, unique=True)  # e.g., GLB-FFM-BLD1
    title = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    city_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100)
    neighborhood = models.CharField(max_length=100, default='Prime Central Hub')
    address = models.TextField()
    image_url = models.URLField(max_length=500)
    images = models.JSONField(default=list)
    amenities = models.JSONField(default=list)
    total_rooms = models.IntegerField(default=1)
    active_occupancy = models.IntegerField(default=0)
    featured = models.BooleanField(default=False)
    syndication_active = models.BooleanField(default=True)
    total_valuation = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    co_invest_target = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    co_invest_raised = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    projected_roi_pct = models.DecimalField(max_digits=5, decimal_places=2, default=14.50)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Properties"

    def __str__(self):
        return f"{self.title} [{self.property_uid}]"


class Room(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='rooms')
    room_uid = models.CharField(max_length=100, unique=True)  # GLB-FFM-BLD1-RM1
    room_number = models.CharField(max_length=20)
    room_type = models.CharField(max_length=50, choices=RoomTypeChoice.choices, default=RoomTypeChoice.PRIVATE_ENSUITE)
    sqm = models.DecimalField(max_digits=6, decimal_places=2)
    regular_rent_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Option A
    micro_investor_rent_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Option B
    security_deposit_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, choices=CurrencyChoice.choices, default=CurrencyChoice.EUR)
    is_available = models.BooleanField(default=True)
    floor = models.IntegerField(default=1)
    features = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.room_uid} - {self.room_type}"


# ==============================================================================
# 2. Tenants & Growth Loop Domain
# ==============================================================================

class TenantUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    django_user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=50)
    avatar_url = models.URLField(max_length=500, blank=True)
    role = models.CharField(max_length=50, default='MICRO_INVESTOR')
    option_type = models.CharField(max_length=20, choices=OptionType.choices, default=OptionType.OPTION_B)

    assigned_property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_room_uid = models.CharField(max_length=100)
    property_title = models.CharField(max_length=255)
    city = models.CharField(max_length=100)

    lease_start_date = models.DateField()
    lease_end_date = models.DateField()
    monthly_rent_charged = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_held = models.DecimalField(max_digits=10, decimal_places=2)
    wallet_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_micro_invested = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    active_profit_share_tier = models.CharField(max_length=50, default='Silver (25%)')
    active_commission_pct = models.DecimalField(max_digits=5, decimal_places=2, default=25.00)
    referral_code = models.CharField(max_length=50, unique=True)
    hygiene_score = models.IntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.referral_code})"


class DocumentRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(TenantUser, on_delete=models.CASCADE, related_name='documents')
    doc_type = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    file_name = models.CharField(max_length=255)
    verified = models.BooleanField(default=True)
    uploaded_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.doc_type})"


class PlacedTenantReferral(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    referring_tenant = models.ForeignKey(TenantUser, on_delete=models.CASCADE, related_name='referrals')
    placed_tenant_name = models.CharField(max_length=255)
    placed_property_title = models.CharField(max_length=255)
    placed_room_uid = models.CharField(max_length=100)
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default='OCCUPIED_PAYING')
    commission_tier_pct = models.DecimalField(max_digits=5, decimal_places=2, default=25.00)
    monthly_profit_share_earned = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)
    placed_date = models.DateField()

    def __str__(self):
        return f"Referral: {self.placed_tenant_name} by {self.referring_tenant.full_name}"


class ProfitShareLedgerEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(TenantUser, on_delete=models.CASCADE, related_name='profit_ledger')
    date = models.DateField()
    transaction_type = models.CharField(max_length=50)  # RESIDUAL_PROFIT_YIELD, GROWTH_LOOP_BONUS, WITHDRAWAL, REINVESTMENT
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, choices=CurrencyChoice.choices, default=CurrencyChoice.EUR)
    description = models.TextField()
    status = models.CharField(max_length=50, default='COMPLETED')

    def __str__(self):
        return f"{self.transaction_type}: {self.amount} {self.currency}"


# ==============================================================================
# 3. Hygiene & Duty Roster Domain
# ==============================================================================

class DutyRosterTask(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    property_title = models.CharField(max_length=255)
    tenant = models.ForeignKey(TenantUser, on_delete=models.CASCADE)
    tenant_name = models.CharField(max_length=255)
    tenant_avatar = models.URLField(max_length=500, blank=True)
    assigned_zone = models.CharField(max_length=100)
    scheduled_date = models.DateField()
    day_of_week = models.CharField(max_length=20)
    due_time = models.CharField(max_length=20, default='22:00')
    status = models.CharField(max_length=50, choices=DutyRosterStatus.choices, default=DutyRosterStatus.PENDING)
    photo_proof_url = models.URLField(max_length=500, blank=True, null=True)
    submitted_at = models.CharField(max_length=100, blank=True, null=True)
    reviewed_by = models.CharField(max_length=255, blank=True, null=True)
    review_notes = models.TextField(blank=True, null=True)
    penalty_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.assigned_zone} ({self.scheduled_date}) - {self.status}"


class HygienePenalty(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    duty_roster = models.ForeignKey(DutyRosterTask, on_delete=models.CASCADE)
    tenant = models.ForeignKey(TenantUser, on_delete=models.CASCADE)
    tenant_name = models.CharField(max_length=255)
    property_uid = models.CharField(max_length=100)
    penalty_amount = models.DecimalField(max_digits=8, decimal_places=2, default=35.00)
    currency = models.CharField(max_length=10, choices=CurrencyChoice.choices, default=CurrencyChoice.EUR)
    reason = models.TextField()
    deducted_from = models.CharField(max_length=50, default='DEPOSIT_LEDGER')
    status = models.CharField(max_length=50, default='DEDUCTED')
    logged_at = models.CharField(max_length=100)

    def __str__(self):
        return f"Penalty {self.penalty_amount} {self.currency} for {self.tenant_name}"


# ==============================================================================
# 4. 12-Module Enterprise ERP Domain
# ==============================================================================

class ERPInvoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number = models.CharField(max_length=100, unique=True)
    recipient_name = models.CharField(max_length=255)
    recipient_email = models.EmailField()
    property_uid = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, choices=CurrencyChoice.choices, default=CurrencyChoice.EUR)
    category = models.CharField(max_length=50)
    issue_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=50, default='PAID')

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.recipient_name}"


class ERPStaff(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    hub = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    active_tasks_count = models.IntegerField(default=0)
    avatar = models.URLField(max_length=500)

    def __str__(self):
        return f"{self.name} ({self.role})"


class ERPKanbanTask(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    assigned_to_name = models.CharField(max_length=255)
    department = models.CharField(max_length=100)
    priority = models.CharField(max_length=50, default='MEDIUM')
    status = models.CharField(max_length=50, default='TODO')  # TODO, IN_PROGRESS, REVIEW, COMPLETED
    property_uid = models.CharField(max_length=100)
    due_date = models.DateField()

    def __str__(self):
        return f"{self.title} ({self.status})"


class MaintenanceTicket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket_code = models.CharField(max_length=50, unique=True)
    property_uid = models.CharField(max_length=100)
    room_uid = models.CharField(max_length=100)
    tenant_name = models.CharField(max_length=255)
    category = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(max_length=50, default='HIGH')
    status = models.CharField(max_length=50, default='DISPATCHED')
    assigned_contractor = models.CharField(max_length=255)
    cost_estimate = models.DecimalField(max_digits=10, decimal_places=2)
    logged_date = models.DateField()

    def __str__(self):
        return f"{self.ticket_code}: {self.title}"


class BrokerRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    agency = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    referral_code = models.CharField(max_length=50, unique=True)
    total_placements = models.IntegerField(default=0)
    total_commission_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    pending_payout = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    commission_rate_pct = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    status = models.CharField(max_length=50, default='ACTIVE')

    def __str__(self):
        return f"{self.name} - {self.agency} ({self.referral_code})"


class MarketingCampaign(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    channel = models.CharField(max_length=100)
    target_segment = models.CharField(max_length=100)
    target_city = models.CharField(max_length=100)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    leads_generated = models.IntegerField(default=0)
    conversions = models.IntegerField(default=0)
    status = models.CharField(max_length=50, default='ACTIVE')

    def __str__(self):
        return f"{self.title} ({self.channel})"


class CommercialDeal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    deal_code = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    floors = models.IntegerField()
    potential_rooms = models.IntegerField()
    total_acquisition_cost = models.DecimalField(max_digits=14, decimal_places=2)
    syndication_target = models.DecimalField(max_digits=14, decimal_places=2)
    syndication_raised = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    expected_cap_rate_pct = models.DecimalField(max_digits=5, decimal_places=2)
    projected_annual_yield_pct = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=50, default='STRUCTURING')
    timeline = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.deal_code} - {self.title} ({self.city})"


class SupplyProduct(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    in_stock = models.IntegerField(default=0)
    reorder_point = models.IntegerField(default=10)
    status = models.CharField(max_length=50, default='IN_STOCK')

    def __str__(self):
        return f"{self.sku}: {self.name} (Stock: {self.in_stock})"


class ComplianceItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property_uid = models.CharField(max_length=100)
    jurisdiction = models.CharField(max_length=100)
    regulation_type = models.CharField(max_length=100)
    status = models.CharField(max_length=50, default='COMPLIANT')
    next_audit_date = models.DateField()
    legal_counsel = models.CharField(max_length=255)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.property_uid} - {self.regulation_type} ({self.status})"


class ExpansionHubKPI(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    active_properties = models.IntegerField(default=1)
    total_beds = models.IntegerField(default=0)
    occupancy_rate_pct = models.DecimalField(max_digits=5, decimal_places=2)
    monthly_revenue_eur = models.DecimalField(max_digits=12, decimal_places=2)
    expansion_target_beds = models.IntegerField()
    growth_potential = models.CharField(max_length=50, default='HIGH')

    def __str__(self):
        return f"{self.city}, {self.country} ({self.growth_potential} Growth)"
