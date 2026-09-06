from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .finance_models import FinancialLedger, SalesRecord, FundPool, CommissionItem
from .finance_serializers import (
    FinancialLedgerSerializer,
    SalesRecordSerializer,
    FundPoolSerializer,
    CommissionItemSerializer,
)


class FinancialLedgerViewSet(viewsets.ModelViewSet):
    queryset = FinancialLedger.objects.all().select_related('created_by')
    serializer_class = FinancialLedgerSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        t_type = self.request.query_params.get('type')
        category = self.request.query_params.get('category')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if t_type:
            queryset = queryset.filter(transaction_type__iexact=t_type)
        if category:
            queryset = queryset.filter(category__icontains=category)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        return queryset

    @action(detail=False, methods=['post'], url_path='entry')
    def manual_entry(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user if request.user.is_authenticated else None)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SalesRecordViewSet(viewsets.ModelViewSet):
    queryset = SalesRecord.objects.all().select_related('inquiry')
    serializer_class = SalesRecordSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        status_val = self.request.query_params.get('status')
        flag = self.request.query_params.get('flag')
        if status_val:
            queryset = queryset.filter(status__iexact=status_val)
        if flag:
            queryset = queryset.filter(flag__iexact=flag)
        return queryset


class FundPoolViewSet(viewsets.ModelViewSet):
    queryset = FundPool.objects.all()
    serializer_class = FundPoolSerializer
    permission_classes = [AllowAny]


class CommissionItemViewSet(viewsets.ModelViewSet):
    queryset = CommissionItem.objects.all()
    serializer_class = CommissionItemSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        code = self.request.query_params.get('referral_code')
        status_val = self.request.query_params.get('status')
        if code:
            queryset = queryset.filter(referral_code__iexact=code)
        if status_val:
            queryset = queryset.filter(status__iexact=status_val)
        return queryset

    @action(detail=True, methods=['patch'], url_path='pay')
    def mark_paid(self, request, pk=None):
        comm = self.get_object()
        comm.status = 'Paid'
        comm.save()

        # Record expense in Financial Ledger
        FinancialLedger.objects.create(
            transaction_type='expense',
            category='Commission Payout',
            description=f"Commission payout to {comm.consultant_name} ({comm.referral_code}) for {comm.lead_name}",
            amount=comm.amount,
            reference_id=comm.id,
            created_by=request.user if request.user.is_authenticated else None
        )

        return Response({'message': 'Commission marked as Paid and logged to ledger', 'commission': CommissionItemSerializer(comm).data})
