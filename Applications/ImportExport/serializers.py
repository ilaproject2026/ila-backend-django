import hashlib
import random
import time
from decimal import Decimal
from rest_framework import serializers

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
    PlatformSettings,
)


def parse_currency_amount(val, default=0.0):
    """
    Parses currency strings like '$48.5M', '$15.0M', '$1,500,000' or raw numbers into Decimal.
    """
    if val is None:
        return Decimal(str(default))
    if isinstance(val, (int, float, Decimal)):
        return Decimal(str(val))
    s = str(val).replace('$', '').replace(',', '').strip()
    mult = 1
    if s.endswith('M') or s.endswith('m'):
        mult = 1000000
        s = s[:-1].strip()
    elif s.endswith('K') or s.endswith('k'):
        mult = 1000
        s = s[:-1].strip()
    elif s.endswith('B') or s.endswith('b'):
        mult = 1000000000
        s = s[:-1].strip()
    try:
        return Decimal(s) * Decimal(str(mult))
    except Exception:
        return Decimal(str(default))


class ReferenceIdModelSerializerMixin:
    """
    Ensures 'id' in output matches 'reference_id' (e.g. 'IMP-9201', 'TX-90412')
    as expected by frontend clients, while also retaining 'uuid' and 'reference_id'.
    On create/update, if 'id' was sent in request payload, maps to 'reference_id'.
    """
    reference_id = serializers.CharField(required=False)

    def to_internal_value(self, data):
        data_dict = data.copy() if hasattr(data, 'copy') else dict(data)
        client_id = data_dict.get('id')
        if client_id and not data_dict.get('reference_id'):
            data_dict['reference_id'] = str(client_id)
        elif not data_dict.get('reference_id'):
            model_name = getattr(self.Meta.model, '__name__', 'OBJ').upper()[:4]
            data_dict['reference_id'] = f"{model_name}-{random.randint(1000, 9999)}"
        return super().to_internal_value(data_dict)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        ref = getattr(instance, 'reference_id', None)
        if ref:
            data['id'] = ref
            data['uuid'] = str(instance.id)
            data['reference_id'] = ref
        return data


# ==============================================================================
# RFQ Serializers
# ==============================================================================

class RFQProposalSerializer(serializers.ModelSerializer):
    unitPriceUsd = serializers.DecimalField(source='unit_price_usd', max_digits=12, decimal_places=2, required=False, allow_null=True)
    totalPriceUsd = serializers.DecimalField(source='total_price_usd', max_digits=16, decimal_places=2)
    deliveryWindow = serializers.CharField(source='delivery_window')
    paymentTerms = serializers.CharField(source='payment_terms')
    inspectionGuarantee = serializers.CharField(source='inspection_guarantee')
    isAccepted = serializers.BooleanField(source='is_accepted')

    class Meta:
        model = RFQProposal
        fields = [
            'id', 'bidder_name', 'totalPriceUsd', 'unitPriceUsd',
            'deliveryWindow', 'paymentTerms', 'inspectionGuarantee', 'isAccepted'
        ]


class RFQSerializer(ReferenceIdModelSerializerMixin, serializers.ModelSerializer):
    proposals = RFQProposalSerializer(many=True, read_only=True)
    targetBudgetUsd = serializers.DecimalField(source='target_budget_usd', max_digits=16, decimal_places=2)
    targetQuantity = serializers.CharField(source='target_quantity')
    deliveryDeadline = serializers.CharField(source='delivery_deadline')
    inspectionAgency = serializers.CharField(source='inspection_agency')
    buyerName = serializers.CharField(source='buyer.name', read_only=True)
    buyerCountry = serializers.CharField(source='buyer.country', read_only=True)
    buyerFlag = serializers.CharField(source='buyer.flag', read_only=True)
    buyerPort = serializers.CharField(source='buyer.port_of_destination', read_only=True)
    buyerContact = serializers.CharField(source='buyer.contact_person', read_only=True)
    buyerEmail = serializers.CharField(source='buyer.contact_email', read_only=True)
    buyerCategories = serializers.JSONField(source='buyer.categories', read_only=True)
    hsCode = serializers.CharField(source='hs_code', required=False)
    commodityCategory = serializers.SerializerMethodField()

    class Meta:
        model = RFQ
        fields = [
            'id', 'reference_id', 'buyer', 'buyerName', 'buyerCountry', 'buyerFlag',
            'buyerPort', 'buyerContact', 'buyerEmail', 'buyerCategories',
            'title', 'hs_code', 'hsCode', 'commodityCategory',
            'targetQuantity', 'targetBudgetUsd', 'incoterm',
            'deliveryDeadline', 'inspectionAgency', 'status', 'proposals'
        ]

    def get_commodityCategory(self, obj):
        cats = getattr(obj.buyer, 'categories', [])
        return cats[0] if (cats and isinstance(cats, list)) else 'Industrial Metals & Metallurgy'

    def create(self, validated_data):
        initial = self.initial_data
        ref_id = initial.get('id') or initial.get('reference_id') or f"RFQ-{random.randint(800, 999)}"
        validated_data['reference_id'] = ref_id
        return super().create(validated_data)


# ==============================================================================
# Importer Serializer
# ==============================================================================

class ImporterSerializer(ReferenceIdModelSerializerMixin, serializers.ModelSerializer):
    rfqTenders = RFQSerializer(source='rfq_tenders', many=True, read_only=True)
    annualVolumeUsd = serializers.SerializerMethodField()
    portOfDestination = serializers.CharField(source='port_of_destination')
    contactPerson = serializers.CharField(source='contact_person')
    contactEmail = serializers.EmailField(source='contact_email')
    creditScore = serializers.CharField(source='credit_score')
    lastActive = serializers.CharField(source='last_active', required=False)
    established = serializers.IntegerField(source='established_year', required=False, allow_null=True)
    employees = serializers.CharField(source='employees_count', required=False)
    taxId = serializers.CharField(source='tax_id', required=False, allow_blank=True)
    bankPartner = serializers.CharField(source='bank_partner')
    escrowDepositCapacity = serializers.SerializerMethodField()
    auditStatus = serializers.CharField(source='audit_status', required=False)
    preferredIncoterms = serializers.ListField(source='preferred_incoterms', child=serializers.CharField(), required=False)
    historicalTradesCount = serializers.IntegerField(source='historical_trades_count', required=False)
    activeRfqs = serializers.SerializerMethodField()

    class Meta:
        model = Importer
        fields = [
            'id', 'reference_id', 'name', 'country', 'flag', 'tier', 'rating',
            'annualVolumeUsd', 'portOfDestination', 'categories', 'activeRfqs',
            'contactPerson', 'contactEmail', 'creditScore', 'status', 'lastActive',
            'established', 'employees', 'taxId', 'bankPartner', 'escrowDepositCapacity',
            'auditStatus', 'preferredIncoterms', 'historicalTradesCount', 'rfqTenders'
        ]

    def get_activeRfqs(self, obj):
        return obj.rfq_tenders.count()

    def get_annualVolumeUsd(self, obj):
        val = obj.annual_volume_usd or Decimal('0.00')
        if val >= 1000000:
            return f"${float(val) / 1000000:.1f}M"
        return f"${float(val):,.2f}"

    def get_escrowDepositCapacity(self, obj):
        val = obj.escrow_deposit_capacity_usd or Decimal('0.00')
        if val >= 1000000:
            return f"${float(val) / 1000000:.1f}M"
        return f"${float(val):,.2f}"

    def create(self, validated_data):
        initial = self.initial_data
        ref_id = initial.get('id') or initial.get('reference_id') or f"IMP-{random.randint(1000, 9999)}"
        validated_data['reference_id'] = ref_id

        # Parse currency fields if passed as strings like "$48.5M"
        if 'annualVolumeUsd' in initial:
            validated_data['annual_volume_usd'] = parse_currency_amount(initial['annualVolumeUsd'])
        if 'escrowDepositCapacity' in initial:
            validated_data['escrow_deposit_capacity_usd'] = parse_currency_amount(initial['escrowDepositCapacity'])

        return super().create(validated_data)

    def update(self, instance, validated_data):
        initial = self.initial_data
        if 'annualVolumeUsd' in initial:
            validated_data['annual_volume_usd'] = parse_currency_amount(initial['annualVolumeUsd'])
        if 'escrowDepositCapacity' in initial:
            validated_data['escrow_deposit_capacity_usd'] = parse_currency_amount(initial['escrowDepositCapacity'])
        return super().update(instance, validated_data)


# ==============================================================================
# Exporter Serializer
# ==============================================================================

class ExporterSerializer(ReferenceIdModelSerializerMixin, serializers.ModelSerializer):
    annualExportCapacityUsd = serializers.SerializerMethodField()
    portOfOrigin = serializers.CharField(source='port_of_origin')
    complianceCertificates = serializers.ListField(source='compliance_certificates', child=serializers.CharField(), required=False)
    productLines = serializers.ListField(source='specialties', child=serializers.CharField(), required=False)
    productionLeadTime = serializers.CharField(source='production_lead_time', required=False)
    contactPerson = serializers.CharField(source='contact_person')
    contactEmail = serializers.EmailField(source='contact_email')
    bankPartner = serializers.CharField(source='bank_partner')
    inspectionAgency = serializers.CharField(source='inspection_agency', required=False)
    factoryAreaSqm = serializers.CharField(source='factory_area_sqm', required=False)
    established = serializers.IntegerField(source='established_year', required=False, allow_null=True)
    historicalExportsCount = serializers.IntegerField(source='historical_exports_count', required=False)

    class Meta:
        model = Exporter
        fields = [
            'id', 'reference_id', 'name', 'country', 'flag', 'tier', 'rating',
            'annualExportCapacityUsd', 'portOfOrigin', 'specialties', 'productLines',
            'complianceCertificates', 'productionLeadTime', 'moq', 'contactPerson',
            'contactEmail', 'bankPartner', 'inspectionAgency', 'status',
            'factoryAreaSqm', 'established', 'historicalExportsCount'
        ]

    def get_annualExportCapacityUsd(self, obj):
        val = obj.annual_export_capacity_usd or Decimal('0.00')
        if val >= 1000000:
            return f"${float(val) / 1000000:.1f}M"
        return f"${float(val):,.2f}"

    def create(self, validated_data):
        initial = self.initial_data
        ref_id = initial.get('id') or initial.get('reference_id') or f"EXP-{random.randint(1000, 9999)}"
        validated_data['reference_id'] = ref_id

        if 'annualExportCapacityUsd' in initial:
            validated_data['annual_export_capacity_usd'] = parse_currency_amount(initial['annualExportCapacityUsd'])

        # Support productLines alias
        if 'productLines' in initial and not validated_data.get('specialties'):
            validated_data['specialties'] = initial['productLines']

        return super().create(validated_data)

    def update(self, instance, validated_data):
        initial = self.initial_data
        if 'annualExportCapacityUsd' in initial:
            validated_data['annual_export_capacity_usd'] = parse_currency_amount(initial['annualExportCapacityUsd'])
        if 'productLines' in initial:
            validated_data['specialties'] = initial['productLines']
        return super().update(instance, validated_data)


# ==============================================================================
# Transaction & Smart Vault Serializers
# ==============================================================================

class VaultSignatureSerializer(serializers.ModelSerializer):
    signerName = serializers.CharField(source='signer_name')

    class Meta:
        model = VaultSignature
        fields = ['role', 'signerName', 'signed', 'timestamp']


class SmartVaultSerializer(serializers.ModelSerializer):
    signatures = VaultSignatureSerializer(many=True, read_only=True)
    contractAddress = serializers.CharField(source='contract_address')
    multiSigRequirement = serializers.CharField(source='multi_sig_requirement')
    collateralRating = serializers.CharField(source='collateral_rating')
    fundsLockedUsd = serializers.DecimalField(source='funds_locked_usd', max_digits=16, decimal_places=2)
    fundsReleasedUsd = serializers.DecimalField(source='funds_released_usd', max_digits=16, decimal_places=2)

    class Meta:
        model = SmartVault
        fields = [
            'contractAddress', 'multiSigRequirement', 'signatures',
            'collateralRating', 'fundsLockedUsd', 'fundsReleasedUsd'
        ]


class AisTelemetrySerializer(serializers.ModelSerializer):
    vesselName = serializers.CharField(source='vessel_name')
    currentSpeedKnots = serializers.CharField(source='current_speed_knots')
    nauticalMilesCovered = serializers.CharField(source='nautical_miles_covered')
    nextWaypoint = serializers.CharField(source='next_waypoint')

    class Meta:
        model = AisTelemetry
        fields = ['vesselName', 'coordinates', 'currentSpeedKnots', 'heading', 'nauticalMilesCovered', 'nextWaypoint']


class ConsignmentDocumentSerializer(serializers.ModelSerializer):
    docType = serializers.CharField(source='doc_type', required=False)

    class Meta:
        model = ConsignmentDocument
        fields = ['doc_type', 'docType', 'name', 'file_url', 'status', 'size']


class TransactionSerializer(ReferenceIdModelSerializerMixin, serializers.ModelSerializer):
    smartVault = SmartVaultSerializer(source='smart_vault', read_only=True)
    aisTelemetry = AisTelemetrySerializer(source='ais_telemetry', read_only=True)
    documents = ConsignmentDocumentSerializer(many=True, read_only=True)
    amountUsd = serializers.DecimalField(source='amount_usd', max_digits=16, decimal_places=2)
    escrowStatus = serializers.CharField(source='escrow_status')
    escrowProgress = serializers.IntegerField(source='escrow_progress')
    stageIndex = serializers.IntegerField(source='stage_index')
    billOfLading = serializers.CharField(source='bill_of_lading')
    shippingLine = serializers.CharField(source='shipping_line')
    portOfLoading = serializers.CharField(source='port_of_loading')
    portOfDischarge = serializers.CharField(source='port_of_discharge')
    currentStage = serializers.CharField(source='current_stage')
    statusBadge = serializers.CharField(source='status_badge')
    lastUpdate = serializers.CharField(source='last_update', required=False, allow_blank=True)
    containerCount = serializers.IntegerField(source='container_count')
    containerType = serializers.CharField(source='container_type')
    hsCode = serializers.CharField(source='hs_code')
    buyerFlag = serializers.CharField(source='buyer_flag', required=False)
    sellerFlag = serializers.CharField(source='seller_flag', required=False)

    class Meta:
        model = Transaction
        fields = [
            'id', 'reference_id', 'title', 'buyer', 'buyer_flag', 'buyerFlag',
            'seller', 'seller_flag', 'sellerFlag', 'amountUsd', 'escrowStatus',
            'escrowProgress', 'stageIndex', 'billOfLading', 'shippingLine',
            'portOfLoading', 'portOfDischarge', 'currentStage', 'eta',
            'statusBadge', 'lastUpdate', 'containerCount', 'containerType',
            'hsCode', 'incoterm', 'smartVault', 'aisTelemetry', 'documents'
        ]

    def create(self, validated_data):
        initial = self.initial_data
        ref_id = initial.get('id') or initial.get('reference_id') or f"TX-{random.randint(90000, 99999)}"
        validated_data['reference_id'] = ref_id

        tx = super().create(validated_data)

        # Handle nested smartVault payload if provided
        sv_data = initial.get('smartVault')
        if sv_data and isinstance(sv_data, dict):
            contract_addr = sv_data.get('contractAddress') or f"0x{hashlib.sha256(f'{ref_id}{time.time()}'.encode()).hexdigest()[:40]}"
            vault = SmartVault.objects.create(
                transaction=tx,
                contract_address=contract_addr,
                multi_sig_requirement=sv_data.get('multiSigRequirement', '3 of 4 Signatures Required'),
                collateral_rating=sv_data.get('collateralRating', 'AAA Backed by Bank Tier 1'),
                funds_locked_usd=Decimal(str(sv_data.get('fundsLockedUsd', tx.amount_usd))),
                funds_released_usd=Decimal(str(sv_data.get('fundsReleasedUsd', 0.0)))
            )
            sigs = sv_data.get('signatures', [])
            if sigs and isinstance(sigs, list):
                for s in sigs:
                    VaultSignature.objects.create(
                        vault=vault,
                        role=s.get('role', 'Signatory'),
                        signer_name=s.get('name') or s.get('signerName', 'Authorized Signer'),
                        signed=s.get('signed', False),
                        timestamp=s.get('timestamp', 'Pending')
                    )

        # Handle nested aisTelemetry if provided
        ais_data = initial.get('aisTelemetry')
        if ais_data and isinstance(ais_data, dict):
            AisTelemetry.objects.create(
                transaction=tx,
                vessel_name=ais_data.get('vesselName', 'Global Cargo Carrier'),
                coordinates=ais_data.get('coordinates', '45.0000° N, 10.0000° E'),
                current_speed_knots=ais_data.get('currentSpeedKnots', '14.0 Knots'),
                heading=ais_data.get('heading', '045° NE'),
                nautical_miles_covered=ais_data.get('nauticalMilesCovered', '1,000 / 3,000 NM'),
                next_waypoint=ais_data.get('nextWaypoint', 'Destination Pilot Station')
            )

        # Handle nested documents if provided
        docs_data = initial.get('documents')
        if docs_data and isinstance(docs_data, list):
            for d in docs_data:
                ConsignmentDocument.objects.create(
                    transaction=tx,
                    doc_type=d.get('type') or d.get('doc_type', 'Consignment Document'),
                    name=d.get('name', 'Document.pdf'),
                    status=d.get('status', 'Verified on Chain'),
                    size=d.get('size', '1.0 MB')
                )

        return tx


# ==============================================================================
# CEO Approval Serializer
# ==============================================================================

class CeoApprovalSerializer(ReferenceIdModelSerializerMixin, serializers.ModelSerializer):
    valueUsd = serializers.DecimalField(source='value_usd', max_digits=16, decimal_places=2)
    riskScore = serializers.CharField(source='risk_score', required=False)
    riskRating = serializers.CharField(source='risk_score', required=False)
    requestedBy = serializers.CharField(source='buyer', required=False)
    counterparty = serializers.CharField(source='seller', required=False)
    notes = serializers.CharField(source='memo', required=False, allow_blank=True)

    class Meta:
        model = CeoApproval
        fields = [
            'id', 'reference_id', 'title', 'buyer', 'seller', 'requestedBy',
            'counterparty', 'valueUsd', 'department', 'riskScore', 'riskRating',
            'urgent', 'notes', 'memo', 'status', 'created_at'
        ]

    def create(self, validated_data):
        initial = self.initial_data
        ref_id = initial.get('id') or initial.get('reference_id') or f"APP-{random.randint(100, 999)}"
        validated_data['reference_id'] = ref_id
        if 'valueUsd' in initial:
            validated_data['value_usd'] = parse_currency_amount(initial['valueUsd'])
        return super().create(validated_data)


# ==============================================================================
# Compliance / Sanctions Serializer
# ==============================================================================

class SanctionsLogSerializer(ReferenceIdModelSerializerMixin, serializers.ModelSerializer):
    entityName = serializers.CharField(source='entity_name')
    entityType = serializers.CharField(source='entity_type', required=False)
    watchlistsChecked = serializers.ListField(source='watchlists_checked', child=serializers.CharField())
    riskScore = serializers.CharField(source='risk_score')
    certificateHash = serializers.CharField(source='certificate_hash')
    timestamp = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = SanctionsLog
        fields = [
            'id', 'reference_id', 'entityName', 'country', 'flag', 'entityType',
            'watchlistsChecked', 'riskScore', 'status', 'certificateHash',
            'timestamp', 'created_at'
        ]

    def create(self, validated_data):
        initial = self.initial_data
        ref_id = initial.get('id') or initial.get('reference_id') or f"SANC-{random.randint(4000, 4999)}"
        validated_data['reference_id'] = ref_id
        return super().create(validated_data)


# ==============================================================================
# HR Serializers
# ==============================================================================

class StaffMemberSerializer(serializers.ModelSerializer):
    employeeId = serializers.CharField(source='employee_id', required=False)
    clearanceLevel = serializers.CharField(source='clearance_level')
    baseSalaryUsd = serializers.DecimalField(source='base_salary_usd', max_digits=12, decimal_places=2)
    monthlyCommissionUsd = serializers.DecimalField(source='monthly_commission_usd', max_digits=12, decimal_places=2, required=False)
    activeCaseload = serializers.IntegerField(source='active_caseload', required=False)
    performanceRating = serializers.CharField(source='performance_rating', required=False)
    avatarBg = serializers.CharField(source='avatar_bg', required=False)

    class Meta:
        model = StaffMember
        fields = [
            'id', 'employeeId', 'name', 'role', 'department', 'location', 'timezone',
            'email', 'clearanceLevel', 'baseSalaryUsd', 'monthlyCommissionUsd',
            'activeCaseload', 'performanceRating', 'status', 'avatarBg'
        ]

    def create(self, validated_data):
        initial = self.initial_data
        if not validated_data.get('employee_id'):
            validated_data['employee_id'] = initial.get('employeeId') or f"EMP-{random.randint(100, 999)}"
        if 'baseSalaryUsd' in initial:
            validated_data['base_salary_usd'] = parse_currency_amount(initial['baseSalaryUsd'])
        return super().create(validated_data)


class JobVacancySerializer(serializers.ModelSerializer):
    jobType = serializers.CharField(source='job_type', required=False)
    applicantsCount = serializers.IntegerField(source='applicants_count', required=False)
    salaryRange = serializers.CharField(source='salary_range')

    class Meta:
        model = JobVacancy
        fields = [
            'id', 'reference_id', 'title', 'department', 'location', 'jobType',
            'applicantsCount', 'urgency', 'salaryRange'
        ]

    def create(self, validated_data):
        initial = self.initial_data
        ref_id = initial.get('id') or initial.get('reference_id') or f"JOB-{random.randint(100, 999)}"
        validated_data['reference_id'] = ref_id
        return super().create(validated_data)


# ==============================================================================
# Accounts / Treasury Serializers
# ==============================================================================

class LedgerEntrySerializer(ReferenceIdModelSerializerMixin, serializers.ModelSerializer):
    txRef = serializers.CharField(source='tx_ref')
    entryType = serializers.CharField(source='entry_type', required=False)
    type = serializers.CharField(source='entry_type', required=False)
    amountUsd = serializers.DecimalField(source='amount_usd', max_digits=16, decimal_places=2)
    feeEarnedUsd = serializers.DecimalField(source='fee_earned_usd', max_digits=16, decimal_places=2, required=False)
    ledgerHash = serializers.CharField(source='ledger_hash', required=False)
    status = serializers.CharField(required=False, default='Settled')
    timestamp = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = LedgerEntry
        fields = [
            'id', 'reference_id', 'txRef', 'description', 'entryType', 'type',
            'category', 'amountUsd', 'feeEarnedUsd', 'status', 'ledgerHash',
            'timestamp', 'created_at'
        ]

    def to_internal_value(self, data):
        data_dict = data.copy() if hasattr(data, 'copy') else dict(data)
        if not data_dict.get('status'):
            data_dict['status'] = 'Settled'
        return super().to_internal_value(data_dict)

    def create(self, validated_data):
        initial = self.initial_data
        ref_id = initial.get('id') or initial.get('reference_id') or f"LEDG-{random.randint(1000, 9999)}"
        validated_data['reference_id'] = ref_id

        tx_ref = validated_data.get('tx_ref', 'TX-REF')
        amount = validated_data.get('amount_usd', 0)

        if not validated_data.get('ledger_hash'):
            validated_data['ledger_hash'] = f"0x{hashlib.sha256(f'{tx_ref}{amount}{time.time()}'.encode()).hexdigest()[:40]}"

        if not validated_data.get('entry_type'):
            validated_data['entry_type'] = initial.get('type') or 'Disbursement (Debit)'

        return super().create(validated_data)


class TreasuryReserveSerializer(serializers.ModelSerializer):
    balanceFormatted = serializers.CharField(source='balance_formatted')
    balanceUsd = serializers.DecimalField(source='balance_usd', max_digits=16, decimal_places=2)
    sharePercent = serializers.CharField(source='share_percent')
    custodianBank = serializers.CharField(source='bank', required=False)

    class Meta:
        model = TreasuryReserve
        fields = [
            'id', 'currency', 'name', 'balanceFormatted', 'balanceUsd',
            'sharePercent', 'bank', 'custodianBank', 'tier'
        ]


# ==============================================================================
# Strategic Tie-ups Serializer
# ==============================================================================

class StrategicTieupSerializer(ReferenceIdModelSerializerMixin, serializers.ModelSerializer):
    partnershipTitle = serializers.CharField(source='partnership_title', required=False, allow_blank=True)
    leadParty = serializers.CharField(source='lead_party', required=False, allow_blank=True)
    counterParty = serializers.CharField(source='counter_party', required=False, allow_blank=True)
    dealType = serializers.CharField(source='deal_type', required=False, allow_blank=True)
    targetAnnualValue = serializers.CharField(source='target_annual_value', required=False, allow_blank=True)
    currentStage = serializers.CharField(source='current_stage', required=False, allow_blank=True)
    slaCompliance = serializers.CharField(source='sla_compliance', required=False, allow_blank=True)
    nextMilestone = serializers.CharField(source='next_milestone', required=False, allow_blank=True)
    assignedDirector = serializers.CharField(source='assigned_director', required=False, allow_blank=True)
    partnerName = serializers.CharField(source='partner_name', required=False, allow_blank=True)
    partnerType = serializers.CharField(source='partner_type', required=False, allow_blank=True)
    signedDate = serializers.CharField(source='signed_date', required=False, allow_blank=True)
    mouDocumentUrl = serializers.URLField(source='mou_document_url', required=False, allow_blank=True)

    class Meta:
        model = StrategicTieup
        fields = [
            'id', 'reference_id', 'partnershipTitle', 'leadParty', 'counterParty',
            'dealType', 'targetAnnualValue', 'currentStage', 'slaCompliance',
            'nextMilestone', 'priority', 'assignedDirector', 'partnerName',
            'partnerType', 'country', 'flag', 'scope', 'signedDate', 'status',
            'mouDocumentUrl'
        ]

    def create(self, validated_data):
        initial = self.initial_data
        ref_id = initial.get('id') or initial.get('reference_id') or f"MOU-{random.randint(500, 999)}"
        validated_data['reference_id'] = ref_id

        # Sync partnerName / partnershipTitle if one is missing
        p_title = initial.get('partnershipTitle')
        lead = initial.get('leadParty')
        counter = initial.get('counterParty')
        if p_title and not validated_data.get('partner_name'):
            validated_data['partner_name'] = f"{lead} & {counter}" if (lead and counter) else p_title

        return super().create(validated_data)


# ==============================================================================
# Portal & Platform Settings Serializers
# ==============================================================================

class ArticleSerializer(serializers.ModelSerializer):
    readTime = serializers.CharField(source='read_time')
    publishedAt = serializers.DateTimeField(source='published_at', read_only=True)
    isFeatured = serializers.BooleanField(source='is_featured')

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'summary', 'content', 'category',
            'author', 'readTime', 'publishedAt', 'isFeatured'
        ]


class DemandItemSerializer(serializers.ModelSerializer):
    hsCode = serializers.CharField(source='hs_code')
    originCountry = serializers.CharField(source='origin_country')
    destinationCountry = serializers.CharField(source='destination_country')
    budgetUsd = serializers.DecimalField(source='budget_usd', max_digits=16, decimal_places=2)

    class Meta:
        model = DemandItem
        fields = [
            'id', 'title', 'hsCode', 'originCountry', 'destinationCountry',
            'volume', 'urgency', 'budgetUsd', 'status'
        ]


class PlatformSettingsSerializer(serializers.ModelSerializer):
    escrowFeePercent = serializers.DecimalField(source='escrow_fee_percent', max_digits=5, decimal_places=2)
    sanctionsAutoScreen = serializers.BooleanField(source='sanctions_auto_screen')
    multiSigQuorum = serializers.CharField(source='multi_sig_quorum')
    oracleInspectionRequired = serializers.BooleanField(source='oracle_inspection_required')
    autoDisbursePayroll = serializers.BooleanField(source='auto_disburse_payroll')
    aisTelemetryTracking = serializers.BooleanField(source='ais_telemetry_tracking')

    class Meta:
        model = PlatformSettings
        fields = [
            'escrowFeePercent', 'sanctionsAutoScreen', 'multiSigQuorum',
            'oracleInspectionRequired', 'autoDisbursePayroll', 'aisTelemetryTracking'
        ]
