from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .rewards_models import ReferralRecord, TierRule
from .rewards_serializers import ReferralRecordSerializer, TierRuleSerializer


class ReferralRecordViewSet(viewsets.ModelViewSet):
    queryset = ReferralRecord.objects.all().select_related('referrer')
    serializer_class = ReferralRecordSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        status_val = self.request.query_params.get('status')
        vertical = self.request.query_params.get('vertical')
        if status_val:
            queryset = queryset.filter(status__iexact=status_val)
        if vertical:
            queryset = queryset.filter(vertical__iexact=vertical)
        return queryset

    @action(detail=True, methods=['patch'], url_path='approve')
    def approve_referral(self, request, pk=None):
        ref = self.get_object()
        action_type = request.data.get('action') # 'marketing_approve', 'accounts_approve', 'payout', 'reject'

        if action_type == 'marketing_approve':
            ref.status = 'Approved by Marketing'
        elif action_type == 'accounts_approve':
            ref.status = 'Approved by Accounts'
        elif action_type == 'payout':
            ref.status = 'Paid Out'
            # Record expense in Financial Ledger
            try:
                from Applications.ILA_WEB.Finance.finance_models import FinancialLedger
                FinancialLedger.objects.create(
                    transaction_type='expense',
                    category='Referral Payout',
                    description=f"Referral reward to {ref.referrer_name} for candidate {ref.candidate_name}",
                    amount=ref.commission_amount,
                    reference_id=ref.id,
                    created_by=request.user if request.user and request.user.is_authenticated else None
                )
            except Exception:
                pass
        elif action_type == 'reject':
            ref.status = 'Rejected'
        else:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

        ref.save()
        return Response({'message': f'Referral updated to {ref.status}', 'referral': ReferralRecordSerializer(ref).data})


class TierRuleViewSet(viewsets.ModelViewSet):
    queryset = TierRule.objects.all()
    serializer_class = TierRuleSerializer
    permission_classes = [AllowAny]
