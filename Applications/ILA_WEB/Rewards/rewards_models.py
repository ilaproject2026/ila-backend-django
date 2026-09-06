from django.db import models
from django.conf import settings
import uuid


def generate_ref_id():
    return f"REF-{uuid.uuid4().hex[:6]}"


class ReferralRecord(models.Model):
    ROLE_CHOICES = [
        ('Student', 'Student'),
        ('Partner', 'Partner'),
        ('Consultant', 'Consultant'),
        ('Employee', 'Employee'),
    ]

    VERTICAL_CHOICES = [
        ('Education Hub', 'Education Hub'),
        ('Study Abroad', 'Study Abroad'),
        ('Work and Study', 'Work and Study'),
        ('Visa and Services', 'Visa and Services'),
        ('Jobs and Career', 'Jobs and Career'),
    ]

    STATUS_CHOICES = [
        ('Pending Verification', 'Pending Verification'),
        ('Approved by Marketing', 'Approved by Marketing'),
        ('Approved by Accounts', 'Approved by Accounts'),
        ('Paid Out', 'Paid Out'),
        ('Rejected', 'Rejected'),
    ]

    id = models.CharField(max_length=50, primary_key=True, default=generate_ref_id)
    referrer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='submitted_referrals')
    referrer_name = models.CharField(max_length=255)
    referrer_email = models.EmailField()
    referrer_role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='Student')
    candidate_name = models.CharField(max_length=255)
    vertical = models.CharField(max_length=50, choices=VERTICAL_CHOICES, default='Education Hub')
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    points_earned = models.IntegerField(default=0)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending Verification')
    date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.referrer_name} -> {self.candidate_name} ({self.status})"


class TierRule(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    tier_name = models.CharField(max_length=50)
    min_referrals = models.IntegerField(default=0)
    bonus_multiplier = models.DecimalField(max_digits=5, decimal_places=2, default=1.00)
    base_reward = models.DecimalField(max_digits=12, decimal_places=2, default=50.00)
    color = models.CharField(max_length=50, default='#CD7F32')

    class Meta:
        ordering = ['min_referrals']

    def __str__(self):
        return f"{self.tier_name} Tier (Min: {self.min_referrals}, Multiplier: {self.bonus_multiplier}x)"
