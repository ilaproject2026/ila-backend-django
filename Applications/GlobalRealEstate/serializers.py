from rest_framework import serializers
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


# ==============================================================================
# 1. Properties Serializers
# ==============================================================================

class LandlordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Landlord
        fields = '__all__'


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'


class PropertySerializer(serializers.ModelSerializer):
    rooms = RoomSerializer(many=True, read_only=True)

    class Meta:
        model = Property
        fields = '__all__'


class MasterLeaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = MasterLease
        fields = '__all__'


# ==============================================================================
# 2. Tenants Serializers
# ==============================================================================

class DocumentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentRecord
        fields = '__all__'


class PlacedTenantReferralSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlacedTenantReferral
        fields = '__all__'


class ProfitShareLedgerEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfitShareLedgerEntry
        fields = '__all__'


class TenantUserSerializer(serializers.ModelSerializer):
    documents = DocumentRecordSerializer(many=True, read_only=True)
    referrals = PlacedTenantReferralSerializer(many=True, read_only=True)
    profit_ledger = ProfitShareLedgerEntrySerializer(many=True, read_only=True)

    class Meta:
        model = TenantUser
        fields = '__all__'


# ==============================================================================
# 3. Hygiene Serializers
# ==============================================================================

class DutyRosterTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = DutyRosterTask
        fields = '__all__'


class HygienePenaltySerializer(serializers.ModelSerializer):
    class Meta:
        model = HygienePenalty
        fields = '__all__'


# ==============================================================================
# 4. 12-Module Enterprise ERP Serializers
# ==============================================================================

class ERPInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ERPInvoice
        fields = '__all__'


class ERPStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = ERPStaff
        fields = '__all__'


class ERPKanbanTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = ERPKanbanTask
        fields = '__all__'


class MaintenanceTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceTicket
        fields = '__all__'


class BrokerRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrokerRecord
        fields = '__all__'


class MarketingCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketingCampaign
        fields = '__all__'


class CommercialDealSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommercialDeal
        fields = '__all__'


class SupplyProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplyProduct
        fields = '__all__'


class ComplianceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplianceItem
        fields = '__all__'


class ExpansionHubKPISerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpansionHubKPI
        fields = '__all__'
