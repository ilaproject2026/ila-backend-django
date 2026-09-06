from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .finance_views import (
    FinancialLedgerViewSet,
    SalesRecordViewSet,
    FundPoolViewSet,
    CommissionItemViewSet,
)

router = DefaultRouter()
router.register(r'ledger', FinancialLedgerViewSet, basename='ledger')
router.register(r'sales', SalesRecordViewSet, basename='sales')
router.register(r'funds', FundPoolViewSet, basename='fund')
router.register(r'commissions', CommissionItemViewSet, basename='commission')

urlpatterns = [
    path('', include(router.urls)),
]
