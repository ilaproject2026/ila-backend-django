import uuid
from django.db import models


class TimeStampedUUIDModel(models.Model):
    """
    Abstract base model providing UUID primary keys, cryptographic audit timestamps,
    and soft-delete indexing.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


# ==============================================================================
# A. Importers & Verified Buyers
# ==============================================================================

class ImporterTier(models.TextChoices):
    VERIFIED_GOLD = 'Verified Gold', 'Verified Gold'
    VERIFIED_SILVER = 'Verified Silver', 'Verified Silver'
    STANDARD_BUYER = 'Standard Buyer', 'Standard Buyer'


class Importer(TimeStampedUUIDModel):
    reference_id = models.CharField(max_length=32, unique=True, db_index=True)  # e.g. IMP-1048
    name = models.CharField(max_length=255, db_index=True)
    country = models.CharField(max_length=100, db_index=True)
    flag = models.CharField(max_length=8, default='🌐')
    tier = models.CharField(max_length=32, choices=ImporterTier.choices, default=ImporterTier.VERIFIED_GOLD)
    rating = models.CharField(max_length=16, default='4.9 ★')
    annual_volume_usd = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    port_of_destination = models.CharField(max_length=150)
    categories = models.JSONField(default=list)  # e.g. ["Industrial Machinery", "Semiconductors"]
    contact_person = models.CharField(max_length=150)
    contact_email = models.EmailField()
    credit_score = models.CharField(max_length=100, default='AAA (Clean)')
    status = models.CharField(max_length=50, default='Active Buyer')
    last_active = models.CharField(max_length=100, default='Verified Just Now')
    established_year = models.PositiveIntegerField(null=True, blank=True)
    employees_count = models.CharField(max_length=50, default='100+')
    tax_id = models.CharField(max_length=100, blank=True)
    bank_partner = models.CharField(max_length=150)
    escrow_deposit_capacity_usd = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    audit_status = models.CharField(max_length=150, default='KYC Verified (Sanctions Cleared)')
    preferred_incoterms = models.JSONField(default=list)
    historical_trades_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference_id} - {self.name} ({self.country})"


# ==============================================================================
# B. Exporters & Certified Producers
# ==============================================================================

class ExporterTier(models.TextChoices):
    TIER_1_PRODUCER = 'Certified Producer (Tier-1)', 'Certified Producer (Tier-1)'
    TIER_2_SUPPLIER = 'Certified Supplier (Tier-2)', 'Certified Supplier (Tier-2)'


class Exporter(TimeStampedUUIDModel):
    reference_id = models.CharField(max_length=32, unique=True, db_index=True)  # e.g. EXP-801
    name = models.CharField(max_length=255, db_index=True)
    country = models.CharField(max_length=100, db_index=True)
    flag = models.CharField(max_length=8, default='🏭')
    tier = models.CharField(max_length=64, choices=ExporterTier.choices, default=ExporterTier.TIER_1_PRODUCER)
    rating = models.CharField(max_length=16, default='5.0 ★')
    annual_export_capacity_usd = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    port_of_origin = models.CharField(max_length=150)
    specialties = models.JSONField(default=list)
    compliance_certificates = models.JSONField(default=list)  # e.g. ["ISO 9001", "CE", "REACH"]
    production_lead_time = models.CharField(max_length=100, default='15 - 25 Days')
    moq = models.CharField(max_length=100, default='1,000 Units')
    contact_person = models.CharField(max_length=150)
    contact_email = models.EmailField()
    bank_partner = models.CharField(max_length=150)
    inspection_agency = models.CharField(max_length=150, default='SGS / TÜV Rheinland')
    status = models.CharField(max_length=50, default='Verified Supplier')
    factory_area_sqm = models.CharField(max_length=100, default='50,000 m²')
    established_year = models.PositiveIntegerField(null=True, blank=True)
    historical_exports_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference_id} - {self.name} ({self.country})"


# ==============================================================================
# C. RFQ Tenders & Vendor Proposals
# ==============================================================================

class RFQStatus(models.TextChoices):
    OPEN = 'Open for Bidding', 'Open for Bidding'
    UNDER_EVALUATION = 'Under Evaluation', 'Under Evaluation'
    AWARDED = 'Awarded & Escrow Locked', 'Awarded & Escrow Locked'
    CLOSED = 'Closed', 'Closed'


class RFQ(TimeStampedUUIDModel):
    reference_id = models.CharField(max_length=32, unique=True, db_index=True)  # e.g. RFQ-881
    buyer = models.ForeignKey(Importer, on_delete=models.CASCADE, related_name='rfq_tenders')
    title = models.CharField(max_length=255)
    hs_code = models.CharField(max_length=32, db_index=True)
    target_quantity = models.CharField(max_length=150)
    target_budget_usd = models.DecimalField(max_digits=16, decimal_places=2)
    incoterm = models.CharField(max_length=64, default='CIF Destination')
    delivery_deadline = models.CharField(max_length=100)
    inspection_agency = models.CharField(max_length=150, default='SGS International Oracle')
    status = models.CharField(max_length=64, choices=RFQStatus.choices, default=RFQStatus.OPEN)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference_id} - {self.title} (${self.target_budget_usd})"


class RFQProposal(TimeStampedUUIDModel):
    rfq = models.ForeignKey(RFQ, on_delete=models.CASCADE, related_name='proposals')
    bidder_name = models.CharField(max_length=255)
    total_price_usd = models.DecimalField(max_digits=16, decimal_places=2)
    unit_price_usd = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    delivery_window = models.CharField(max_length=100)
    payment_terms = models.CharField(max_length=150, default='100% Nexus Smart Escrow')
    inspection_guarantee = models.CharField(max_length=150, default='SGS Pre-Shipment Inspection Included')
    is_accepted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Proposal for {self.rfq.reference_id} by {self.bidder_name}"


# ==============================================================================
# D. Consignment Transactions & 3-of-4 Smart Escrow Vaults
# ==============================================================================

class ConsignmentStage(models.IntegerChoices):
    STAGE_1 = 1, 'Stage 1: Contract Signed & 100% Escrow Vault Locked'
    STAGE_2 = 2, 'Stage 2: Port Loading & SGS Pre-Shipment Inspection Passed (20% Payout)'
    STAGE_3 = 3, 'Stage 3: Deep-Sea Maritime Transit & AIS Voyage Tracking'
    STAGE_4 = 4, 'Stage 4: Destination Port Arrival & Customs Clearance (70% Payout)'
    STAGE_5 = 5, 'Stage 5: Cargo Discharged, Inspected & 100% Escrow Settled'


class Transaction(TimeStampedUUIDModel):
    reference_id = models.CharField(max_length=32, unique=True, db_index=True)  # e.g. TX-74820
    title = models.CharField(max_length=255)
    buyer = models.CharField(max_length=255)
    buyer_flag = models.CharField(max_length=8, default='🌐')
    seller = models.CharField(max_length=255)
    seller_flag = models.CharField(max_length=8, default='🏭')
    amount_usd = models.DecimalField(max_digits=16, decimal_places=2)
    escrow_status = models.CharField(max_length=255)
    escrow_progress = models.PositiveIntegerField(default=20)  # 20, 25, 50, 75, 100
    stage_index = models.PositiveSmallIntegerField(choices=ConsignmentStage.choices, default=ConsignmentStage.STAGE_1)
    bill_of_lading = models.CharField(max_length=100, db_index=True)
    shipping_line = models.CharField(max_length=150, default='Maersk / CMA CGM Consortium')
    port_of_loading = models.CharField(max_length=150)
    port_of_discharge = models.CharField(max_length=150)
    current_stage = models.CharField(max_length=255)
    eta = models.CharField(max_length=100)
    status_badge = models.CharField(max_length=50, default='Escrow Locked')
    last_update = models.TextField(blank=True)
    container_count = models.PositiveIntegerField(default=1)
    container_type = models.CharField(max_length=100, default='40ft High Cube (HQ)')
    hs_code = models.CharField(max_length=32)
    incoterm = models.CharField(max_length=64, default='CIF Named Port')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference_id} - {self.title} (${self.amount_usd})"


class SmartVault(TimeStampedUUIDModel):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name='smart_vault')
    contract_address = models.CharField(max_length=66, unique=True)  # 0x...
    multi_sig_requirement = models.CharField(max_length=100, default='3 of 4 Signatures Required')
    collateral_rating = models.CharField(max_length=100, default='AAA Backed by Bank Tier 1')
    funds_locked_usd = models.DecimalField(max_digits=16, decimal_places=2)
    funds_released_usd = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Vault {self.contract_address[:10]}... for {self.transaction.reference_id}"


class VaultSignature(TimeStampedUUIDModel):
    vault = models.ForeignKey(SmartVault, on_delete=models.CASCADE, related_name='signatures')
    role = models.CharField(max_length=100)  # 'Buyer Signatory', 'Seller Signatory', 'SGS Inspection Oracle', 'Nexus Neutral Trustee'
    signer_name = models.CharField(max_length=150)
    signed = models.BooleanField(default=False)
    timestamp = models.CharField(max_length=100, default='Pending')

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role} - {self.signer_name} ({'Signed' if self.signed else 'Pending'})"


class AisTelemetry(TimeStampedUUIDModel):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name='ais_telemetry')
    vessel_name = models.CharField(max_length=150)
    coordinates = models.CharField(max_length=100)
    current_speed_knots = models.CharField(max_length=50, default='0.0 Knots')
    heading = models.CharField(max_length=50, default='At Berth')
    nautical_miles_covered = models.CharField(max_length=50, default='0 NM')
    next_waypoint = models.CharField(max_length=150)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.vessel_name} ({self.coordinates})"


class ConsignmentDocument(TimeStampedUUIDModel):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='documents')
    doc_type = models.CharField(max_length=100)  # 'Commercial Invoice', 'Pro-Forma Bill of Lading', 'SGS Certificate'
    name = models.CharField(max_length=255)
    file_url = models.URLField(blank=True)
    status = models.CharField(max_length=100, default='Escrow Locked')
    size = models.CharField(max_length=50, default='500 KB')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.doc_type})"


# ==============================================================================
# E. CEO Executive Approvals Desk
# ==============================================================================

class CeoApproval(TimeStampedUUIDModel):
    reference_id = models.CharField(max_length=32, unique=True, db_index=True)  # e.g. APP-901
    title = models.CharField(max_length=255)
    buyer = models.CharField(max_length=255)
    seller = models.CharField(max_length=255)
    value_usd = models.DecimalField(max_digits=16, decimal_places=2)
    department = models.CharField(max_length=100, default='Trade Finance & Escrow Treasury')
    risk_score = models.CharField(max_length=50, default='Low (1.8/10)')
    urgent = models.BooleanField(default=False)
    memo = models.TextField(blank=True)
    status = models.CharField(max_length=50, default='Pending Authorization')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference_id} - {self.title} (${self.value_usd})"


# ==============================================================================
# F. Sanctions, KYC & Compliance Radar
# ==============================================================================

class SanctionsLog(TimeStampedUUIDModel):
    reference_id = models.CharField(max_length=32, unique=True, db_index=True)  # e.g. SANC-4821
    entity_name = models.CharField(max_length=255, db_index=True)
    country = models.CharField(max_length=100)
    flag = models.CharField(max_length=8, default='🌐')
    entity_type = models.CharField(max_length=100, default='Screened Entity')
    watchlists_checked = models.JSONField(default=list)  # ["OFAC SDN", "EU Consolidated", "UN Sanctions", "FATF Clean"]
    risk_score = models.CharField(max_length=50, default='0.1 / 10 (Clean)')
    status = models.CharField(max_length=100, default='Cleared & Whitelisted')
    certificate_hash = models.CharField(max_length=66, unique=True)  # 0x...

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference_id} - {self.entity_name} ({self.status})"


# ==============================================================================
# G. HR & Accounts Treasury
# ==============================================================================

class StaffMember(TimeStampedUUIDModel):
    employee_id = models.CharField(max_length=32, unique=True)  # EMP-101
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=150)
    department = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    timezone = models.CharField(max_length=50, default='UTC+0')
    email = models.EmailField(unique=True)
    clearance_level = models.CharField(max_length=100, default='Level 2 (Standard)')
    base_salary_usd = models.DecimalField(max_digits=12, decimal_places=2, default=120000.00)
    monthly_commission_usd = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    active_caseload = models.PositiveIntegerField(default=0)
    performance_rating = models.CharField(max_length=20, default='95.0%')
    status = models.CharField(max_length=50, default='On Duty (Active)')
    avatar_bg = models.CharField(max_length=100, default='bg-teal-500/20 text-teal-400')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee_id} - {self.name} ({self.role})"


class JobVacancy(TimeStampedUUIDModel):
    reference_id = models.CharField(max_length=32, unique=True)  # VAC-12
    title = models.CharField(max_length=150)
    department = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    job_type = models.CharField(max_length=50, default='Full-Time')
    applicants_count = models.PositiveIntegerField(default=0)
    urgency = models.CharField(max_length=50, default='Priority')
    salary_range = models.CharField(max_length=100, default='$120,000 - $150,000')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference_id} - {self.title} ({self.department})"


class LedgerEntry(TimeStampedUUIDModel):
    reference_id = models.CharField(max_length=32, unique=True)  # LED-9102
    tx_ref = models.CharField(max_length=100)
    description = models.TextField()
    entry_type = models.CharField(max_length=100)  # 'Disbursement (Debit)', 'Deposit (Credit)'
    category = models.CharField(max_length=100)
    amount_usd = models.DecimalField(max_digits=16, decimal_places=2)
    fee_earned_usd = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    status = models.CharField(max_length=100)
    ledger_hash = models.CharField(max_length=66, unique=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference_id} - {self.tx_ref}: {self.amount_usd} USD"


class TreasuryReserve(TimeStampedUUIDModel):
    currency = models.CharField(max_length=10)  # 'USD', 'EUR', 'SGD', 'USDC'
    name = models.CharField(max_length=150)
    balance_formatted = models.CharField(max_length=50)
    balance_usd = models.DecimalField(max_digits=16, decimal_places=2)
    share_percent = models.CharField(max_length=20)
    bank = models.CharField(max_length=150)
    tier = models.CharField(max_length=100)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.currency} - {self.name} ({self.balance_formatted})"


# ==============================================================================
# H. Strategic Tie-ups & Inter-Agency MoUs
# ==============================================================================

class StrategicTieup(TimeStampedUUIDModel):
    reference_id = models.CharField(max_length=32, unique=True)  # MOU-501
    partner_name = models.CharField(max_length=255, blank=True, default='')
    partner_type = models.CharField(max_length=100, blank=True, default='')  # 'Port Authority', 'Inspection Agency', 'Trade Bank'
    country = models.CharField(max_length=100, blank=True, default='Global')
    flag = models.CharField(max_length=8, default='🤝')
    scope = models.TextField(blank=True, default='')
    signed_date = models.CharField(max_length=100, blank=True, default='')
    status = models.CharField(max_length=50, default='Active Agreement')
    mou_document_url = models.URLField(blank=True)

    # B2B Partnership Task Extensions
    partnership_title = models.CharField(max_length=255, blank=True, default='')
    lead_party = models.CharField(max_length=255, blank=True, default='')
    counter_party = models.CharField(max_length=255, blank=True, default='')
    deal_type = models.CharField(max_length=150, blank=True, default='')
    target_annual_value = models.CharField(max_length=100, blank=True, default='')
    current_stage = models.CharField(max_length=255, blank=True, default='Initial Due Diligence Review')
    sla_compliance = models.CharField(max_length=50, blank=True, default='99.1%')
    next_milestone = models.CharField(max_length=255, blank=True, default='Customs Inter-Agency MoU')
    priority = models.CharField(max_length=50, blank=True, default='High')
    assigned_director = models.CharField(max_length=150, blank=True, default='Arthur Sterling (CEO Office)')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        title = self.partnership_title or self.partner_name or self.reference_id
        return f"{self.reference_id} - {title}"


# ==============================================================================
# J. Platform Governance Settings
# ==============================================================================

class PlatformSettings(TimeStampedUUIDModel):
    escrow_fee_percent = models.DecimalField(max_digits=5, decimal_places=2, default=1.25)
    sanctions_auto_screen = models.BooleanField(default=True)
    multi_sig_quorum = models.CharField(max_length=50, default='3 of 4')
    oracle_inspection_required = models.BooleanField(default=True)
    auto_disburse_payroll = models.BooleanField(default=True)
    ais_telemetry_tracking = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Platform Governance Settings'
        verbose_name_plural = 'Platform Governance Settings'

    def __str__(self):
        return f"Governance Settings (Escrow Fee: {self.escrow_fee_percent}%)"


# ==============================================================================
# I. Public Portal Catalog: Articles & Demands
# ==============================================================================

class Article(TimeStampedUUIDModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    summary = models.TextField()
    content = models.TextField()
    category = models.CharField(max_length=100, default='Maritime Logistics')
    author = models.CharField(max_length=150, default='NEXUS Research Desk')
    read_time = models.CharField(max_length=50, default='5 min read')
    published_at = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title


class DemandItem(TimeStampedUUIDModel):
    title = models.CharField(max_length=255)
    hs_code = models.CharField(max_length=32)
    origin_country = models.CharField(max_length=100)
    destination_country = models.CharField(max_length=100)
    volume = models.CharField(max_length=100)
    urgency = models.CharField(max_length=50, default='High Urgency')
    budget_usd = models.DecimalField(max_digits=16, decimal_places=2)
    status = models.CharField(max_length=50, default='Sourcing Active')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.volume})"
