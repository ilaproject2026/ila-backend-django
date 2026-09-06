from django.db import models
from django.conf import settings
import uuid


def generate_led_id():
    return f"LED-{uuid.uuid4().hex[:6]}"


def generate_sales_id():
    return f"S-{uuid.uuid4().hex[:6]}"


def generate_fund_id():
    return f"FUND-{uuid.uuid4().hex[:6]}"


def generate_comm_id():
    return f"COMM-{uuid.uuid4().hex[:6]}"


class FinancialLedger(models.Model):
    TRANSACTION_CHOICES = [
        ('income', 'income'),
        ('expense', 'expense'),
    ]

    id = models.CharField(max_length=50, primary_key=True, default=generate_led_id)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_CHOICES)
    category = models.CharField(max_length=100)
    description = models.TextField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(auto_now_add=True, db_index=True)
    reference_id = models.CharField(max_length=100, null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        return f"[{self.transaction_type.upper()}] {self.category}: €{self.amount} ({self.id})"


class SalesRecord(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Partially Paid', 'Partially Paid'),
    ]

    FLAG_CHOICES = [
        ('Pending', 'Pending'),
        ('On Time', 'On Time'),
        ('Delayed ⚠️', 'Delayed ⚠️'),
    ]

    id = models.CharField(max_length=50, primary_key=True, default=generate_sales_id)
    client_name = models.CharField(max_length=255)
    inquiry = models.ForeignKey('ILA_WEB.Inquiry', on_delete=models.SET_NULL, null=True, blank=True, related_name='sales_records')
    program_name = models.CharField(max_length=255)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    flag = models.CharField(max_length=50, choices=FLAG_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.client_name} - {self.program_name}: {self.status}"


class FundPool(models.Model):
    CATEGORY_CHOICES = [
        ('Operations', 'Operations'),
        ('Marketing', 'Marketing'),
        ('Reserve', 'Reserve'),
        ('Emergency', 'Emergency'),
    ]

    id = models.CharField(max_length=50, primary_key=True, default=generate_fund_id)
    fund_name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Operations')
    allocated_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    utilized_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    @property
    def remaining_amount(self):
        return self.allocated_amount - self.utilized_amount

    def __str__(self):
        return f"{self.fund_name} ({self.category}): €{self.remaining_amount} left"


class CommissionItem(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
    ]

    id = models.CharField(max_length=50, primary_key=True, default=generate_comm_id)
    consultant_name = models.CharField(max_length=255)
    referral_code = models.CharField(max_length=50, db_index=True)
    lead_name = models.CharField(max_length=255)
    program = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.consultant_name} ({self.referral_code}) - €{self.amount} [{self.status}]"
