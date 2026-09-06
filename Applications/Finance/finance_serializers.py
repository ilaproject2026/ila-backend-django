from rest_framework import serializers
from .finance_models import FinancialLedger, SalesRecord, FundPool, CommissionItem


class FinancialLedgerSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.fullname', read_only=True)

    class Meta:
        model = FinancialLedger
        fields = '__all__'


class SalesRecordSerializer(serializers.ModelSerializer):
    inquiry_token = serializers.CharField(source='inquiry.token_number', read_only=True)

    class Meta:
        model = SalesRecord
        fields = '__all__'


class FundPoolSerializer(serializers.ModelSerializer):
    remaining_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = FundPool
        fields = '__all__'


class CommissionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommissionItem
        fields = '__all__'
