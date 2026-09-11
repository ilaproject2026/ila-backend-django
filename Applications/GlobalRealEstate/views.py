import datetime
from decimal import Decimal
from django.utils import timezone
from rest_framework import viewsets, status, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

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
from .serializers import (
    PropertySerializer,
    RoomSerializer,
    MasterLeaseSerializer,
    LandlordSerializer,
    TenantUserSerializer,
    DocumentRecordSerializer,
    PlacedTenantReferralSerializer,
    ProfitShareLedgerEntrySerializer,
    DutyRosterTaskSerializer,
    HygienePenaltySerializer,
    ERPInvoiceSerializer,
    ERPStaffSerializer,
    ERPKanbanTaskSerializer,
    MaintenanceTicketSerializer,
    BrokerRecordSerializer,
    MarketingCampaignSerializer,
    CommercialDealSerializer,
    SupplyProductSerializer,
    ComplianceItemSerializer,
    ExpansionHubKPISerializer,
)


# ==============================================================================
# Health Check View
# ==============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({
        'status': 'healthy',
        'service': 'ila-global-proptech-drf',
        'timestamp': timezone.now().isoformat(),
    })


# ==============================================================================
# 1. Properties ViewSets
# ==============================================================================

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all().prefetch_related('rooms').order_by('-created_at')
    serializer_class = PropertySerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['city', 'city_code', 'featured', 'syndication_active']
    search_fields = ['title', 'city', 'country', 'neighborhood']
    ordering_fields = ['created_at', 'total_valuation', 'projected_roi_pct']

    def get_queryset(self):
        qs = super().get_queryset()
        max_rent = self.request.query_params.get('max_rent')
        room_type = self.request.query_params.get('room_type')
        if max_rent:
            qs = qs.filter(rooms__micro_investor_rent_amount__lte=max_rent).distinct()
        if room_type and room_type != 'All':
            qs = qs.filter(rooms__room_type=room_type).distinct()
        return qs


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['property', 'room_type', 'is_available', 'currency']
    search_fields = ['room_uid', 'room_number']


class MasterLeaseViewSet(viewsets.ModelViewSet):
    queryset = MasterLease.objects.all()
    serializer_class = MasterLeaseSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        data = request.data
        lease_data = data.get('lease_data', data)
        rooms_count = int(data.get('rooms_count', 12))

        city_code = lease_data.get('city_code', 'FFM').upper()
        existing_count = Property.objects.filter(city_code=city_code).count() + 1
        property_uid = f"GLB-{city_code}-BLD{existing_count}"

        # Create Master Lease
        master_rent = Decimal(str(lease_data.get('monthly_master_rent', 4500.00)))
        master_lease = MasterLease.objects.create(
            landlord_name=lease_data.get('landlord_name', 'Global Owner'),
            landlord_email=lease_data.get('landlord_email', 'owner@global.com'),
            landlord_phone=lease_data.get('landlord_phone', '+49 69 000000'),
            building_name=lease_data.get('building_name', 'ILA Residence'),
            city_code=city_code,
            city_name=lease_data.get('city_name', 'Frankfurt'),
            country=lease_data.get('country', 'Germany'),
            address=lease_data.get('address', 'Mainzer Landstraße 100'),
            total_floors=int(lease_data.get('total_floors', 4)),
            total_capacity=int(lease_data.get('total_capacity', rooms_count)),
            monthly_master_rent=master_rent,
            currency=lease_data.get('currency', 'EUR'),
            lease_start_date=lease_data.get('lease_start_date', datetime.date.today()),
            lease_end_date=lease_data.get('lease_end_date', datetime.date.today() + datetime.timedelta(days=365 * 3)),
            generated_property_uid=property_uid,
        )

        # Create Property
        prop = Property.objects.create(
            master_lease=master_lease,
            property_uid=property_uid,
            title=master_lease.building_name,
            city=master_lease.city_name,
            city_code=city_code,
            country=master_lease.country,
            address=master_lease.address,
            image_url="https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=1000&q=80",
            amenities=['Ultra-Fast WiFi', 'Bi-Weekly Cleaning', 'Co-Working Lounge', 'Smart Locks'],
            total_rooms=rooms_count,
            total_valuation=master_rent * Decimal('12') * Decimal('18'),
            co_invest_target=master_rent * Decimal('12') * Decimal('4'),
            co_invest_raised=Decimal('0.00'),
            projected_roi_pct=Decimal('16.20'),
            description=f"Master lease structured property in {master_lease.city_name}.",
        )

        # Auto-generate individual rooms
        for idx in range(rooms_count):
            Room.objects.create(
                property=prop,
                room_uid=f"{property_uid}-RM{idx + 1}",
                room_number=str(101 + idx),
                room_type='Co-Living Studio' if idx % 2 == 0 else 'Private Ensuite',
                sqm=Decimal(str(18 + (idx % 3) * 4)),
                regular_rent_amount=Decimal(str(420 + (idx % 3) * 60)),
                micro_investor_rent_amount=Decimal(str(310 + (idx % 3) * 50)),
                security_deposit_amount=Decimal(str(420 + (idx % 3) * 60)),
                currency=master_lease.currency,
                floor=(idx // 4) + 1,
                features=['High-speed WiFi', 'Wardrobe', 'Desk', 'Keycard Access'],
            )

        return Response({
            'master_lease': MasterLeaseSerializer(master_lease).data,
            'property': PropertySerializer(prop).data,
        }, status=status.HTTP_201_CREATED)


# ==============================================================================
# 2. Tenants & Growth Loop ViewSet
# ==============================================================================

class TenantViewSet(viewsets.ModelViewSet):
    queryset = TenantUser.objects.all().prefetch_related('documents', 'referrals', 'profit_ledger')
    serializer_class = TenantUserSerializer
    permission_classes = [AllowAny]

    def _get_current_tenant(self, request):
        if request.user.is_authenticated:
            tenant = TenantUser.objects.filter(django_user=request.user).first()
            if tenant:
                return tenant
        return TenantUser.objects.first()

    @action(detail=False, methods=['get'])
    def me(self, request):
        tenant = self._get_current_tenant(request)
        if not tenant:
            return Response({'detail': 'No active tenant found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(tenant)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='me/update_option')
    def update_option(self, request):
        tenant = self._get_current_tenant(request)
        if not tenant:
            return Response({'detail': 'Tenant not found'}, status=status.HTTP_404_NOT_FOUND)

        option_type = request.data.get('option_type', 'OPTION_B')
        tenant.option_type = option_type
        tenant.monthly_rent_charged = Decimal('330.00') if option_type == 'OPTION_B' else Decimal('450.00')
        tenant.active_commission_pct = Decimal('25.00') if option_type == 'OPTION_B' else Decimal('0.00')
        tenant.save()
        return Response(self.get_serializer(tenant).data)

    @action(detail=False, methods=['post'], url_path='me/relocation_loop')
    def relocation_loop(self, request):
        tenant = self._get_current_tenant(request)
        if not tenant:
            return Response({'detail': 'Tenant not found'}, status=status.HTTP_404_NOT_FOUND)

        new_prop_id = request.data.get('new_property_id')
        new_room_id = request.data.get('new_room_id')
        placed_name = request.data.get('placed_tenant_name', 'New Resident')

        bonus = Decimal('250.00')
        tenant.wallet_balance += bonus

        # Record placement referral
        PlacedTenantReferral.objects.create(
            referring_tenant=tenant,
            placed_tenant_name=placed_name,
            placed_property_title=tenant.property_title,
            placed_room_uid=tenant.assigned_room_uid,
            monthly_rent=Decimal('440.00'),
            commission_tier_pct=Decimal('25.00'),
            monthly_profit_share_earned=Decimal('110.00'),
            placed_date=datetime.date.today(),
        )

        # Record ledger
        ProfitShareLedgerEntry.objects.create(
            tenant=tenant,
            date=datetime.date.today(),
            transaction_type='GROWTH_LOOP_BONUS',
            amount=bonus,
            currency='EUR',
            description=f"Growth Loop Execution: Successfully placed {placed_name}",
            status='COMPLETED',
        )

        tenant.save()
        return Response(self.get_serializer(tenant).data)

    @action(detail=False, methods=['post'], url_path='me/withdraw')
    def withdraw(self, request):
        tenant = self._get_current_tenant(request)
        if not tenant:
            return Response({'detail': 'Tenant not found'}, status=status.HTTP_404_NOT_FOUND)

        amount = Decimal(str(request.data.get('amount', 0)))
        if tenant.wallet_balance < amount:
            return Response({'detail': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

        tenant.wallet_balance -= amount
        ProfitShareLedgerEntry.objects.create(
            tenant=tenant,
            date=datetime.date.today(),
            transaction_type='WITHDRAWAL',
            amount=-amount,
            currency='EUR',
            description="SEPA/SWIFT Transfer to linked bank account",
            status='COMPLETED',
        )
        tenant.save()
        return Response({'success': True, 'new_balance': float(tenant.wallet_balance)})

    @action(detail=False, methods=['post'], url_path='me/reinvest')
    def reinvest(self, request):
        tenant = self._get_current_tenant(request)
        if not tenant:
            return Response({'detail': 'Tenant not found'}, status=status.HTTP_404_NOT_FOUND)

        amount = Decimal(str(request.data.get('amount', 0)))
        if tenant.wallet_balance < amount:
            return Response({'detail': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

        tenant.wallet_balance -= amount
        tenant.total_micro_invested += amount
        ProfitShareLedgerEntry.objects.create(
            tenant=tenant,
            date=datetime.date.today(),
            transaction_type='REINVESTMENT',
            amount=amount,
            currency='EUR',
            description="Reinvestment into Global Real Estate Pool",
            status='COMPLETED',
        )
        tenant.save()
        return Response({
            'success': True,
            'new_balance': float(tenant.wallet_balance),
            'new_total_invested': float(tenant.total_micro_invested),
        })


# ==============================================================================
# 3. Hygiene & Duty Rosters
# ==============================================================================

class DutyRosterViewSet(viewsets.ModelViewSet):
    queryset = DutyRosterTask.objects.all().order_by('scheduled_date')
    serializer_class = DutyRosterTaskSerializer
    permission_classes = [AllowAny]

    @action(detail=True, methods=['post'])
    def submit_proof(self, request, pk=None):
        task = self.get_object()
        task.photo_proof_url = request.data.get('photo_proof_url')
        task.status = 'SUBMITTED_FOR_REVIEW'
        task.submitted_at = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        task.save()
        return Response(self.get_serializer(task).data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        task = self.get_object()
        task.status = 'APPROVED'
        task.reviewed_by = request.data.get('reviewer_name', 'Roommate')
        task.review_notes = request.data.get('review_notes', 'Verified and approved.')
        task.save()
        return Response(self.get_serializer(task).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        task = self.get_object()
        reviewer = request.data.get('reviewer_name', 'Roommate')
        reason = request.data.get('reason', 'Failed cleanliness standard.')

        task.status = 'REJECTED_PENALIZED'
        task.reviewed_by = reviewer
        task.review_notes = reason
        task.penalty_amount = Decimal('35.00')
        task.save()

        # Deduct penalty
        penalty = HygienePenalty.objects.create(
            duty_roster=task,
            tenant=task.tenant,
            tenant_name=task.tenant_name,
            property_uid=task.property.property_uid,
            penalty_amount=Decimal('35.00'),
            currency='EUR',
            reason=f"Cleaning rejected by {reviewer}: {reason}",
            deducted_from='DEPOSIT_LEDGER',
            status='DEDUCTED',
            logged_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        )

        task.tenant.deposit_held = max(Decimal('0.00'), task.tenant.deposit_held - Decimal('35.00'))
        task.tenant.hygiene_score = max(50, task.tenant.hygiene_score - 8)
        task.tenant.save()

        return Response({
            'task': self.get_serializer(task).data,
            'penalty': HygienePenaltySerializer(penalty).data,
        })


class HygienePenaltyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HygienePenalty.objects.all().order_by('-logged_at')
    serializer_class = HygienePenaltySerializer
    permission_classes = [AllowAny]


# ==============================================================================
# 4. 12-Module Enterprise ERP ViewSets
# ==============================================================================

class ERPInvoiceViewSet(viewsets.ModelViewSet):
    queryset = ERPInvoice.objects.all().order_by('-issue_date')
    serializer_class = ERPInvoiceSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'category']
    search_fields = ['invoice_number', 'recipient_name', 'property_uid']


class ERPStaffViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ERPStaff.objects.all()
    serializer_class = ERPStaffSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['department', 'hub']
    search_fields = ['name', 'role', 'email']


class ERPKanbanTaskViewSet(viewsets.ModelViewSet):
    queryset = ERPKanbanTask.objects.all().order_by('due_date')
    serializer_class = ERPKanbanTaskSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'priority', 'department']
    search_fields = ['title', 'assigned_to_name', 'property_uid']


class MaintenanceTicketViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceTicket.objects.all().order_by('-logged_date')
    serializer_class = MaintenanceTicketSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'priority', 'category']
    search_fields = ['ticket_code', 'title', 'tenant_name', 'property_uid']


class BrokerRecordViewSet(viewsets.ModelViewSet):
    queryset = BrokerRecord.objects.all()
    serializer_class = BrokerRecordSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status']
    search_fields = ['name', 'agency', 'referral_code']

    @action(detail=True, methods=['post'])
    def pay_commission(self, request, pk=None):
        broker = self.get_object()
        broker.total_commission_paid += broker.pending_payout
        broker.pending_payout = Decimal('0.00')
        broker.save()
        return Response(self.get_serializer(broker).data)


class MarketingCampaignViewSet(viewsets.ModelViewSet):
    queryset = MarketingCampaign.objects.all()
    serializer_class = MarketingCampaignSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'channel', 'target_city']
    search_fields = ['title', 'target_segment']

    @action(detail=True, methods=['post'])
    def broadcast(self, request, pk=None):
        campaign = self.get_object()
        campaign.leads_generated += 15
        campaign.conversions += 3
        campaign.save()
        return Response(self.get_serializer(campaign).data)


class CommercialDealViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CommercialDeal.objects.all()
    serializer_class = CommercialDealSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'city', 'country']
    search_fields = ['deal_code', 'title']


class SupplyProductViewSet(viewsets.ModelViewSet):
    queryset = SupplyProduct.objects.all()
    serializer_class = SupplyProductSerializer
    permission_classes = [AllowAny]
    lookup_field = 'sku'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'category']
    search_fields = ['sku', 'name']

    @action(detail=True, methods=['post'])
    def restock(self, request, sku=None):
        product = self.get_object()
        qty = int(request.data.get('quantity', 20))
        product.in_stock += qty
        product.status = 'IN_STOCK'
        product.save()
        return Response(self.get_serializer(product).data)


class ComplianceItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ComplianceItem.objects.all()
    serializer_class = ComplianceItemSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'jurisdiction']
    search_fields = ['property_uid', 'regulation_type', 'legal_counsel']


class ExpansionHubKPIViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ExpansionHubKPI.objects.all()
    serializer_class = ExpansionHubKPISerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['country', 'region', 'growth_potential']
    search_fields = ['city', 'country']
