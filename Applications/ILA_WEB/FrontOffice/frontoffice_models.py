from django.db import models
from django.conf import settings
import uuid


def generate_inquiry_id():
    return f"inq-{uuid.uuid4().hex[:8]}"


def generate_followup_id():
    return f"FL-{uuid.uuid4().hex[:6]}"


class Inquiry(models.Model):
    LEAD_TYPE_CHOICES = [
        ('Walk-in', 'Walk-in'),
        ('Online', 'Online'),
        ('Referral', 'Referral'),
        ('Phone', 'Phone'),
    ]

    CATEGORY_CHOICES = [
        ('Education', 'Education'),
        ('Study Abroad', 'Study Abroad'),
        ('Visa', 'Visa'),
        ('Jobs', 'Jobs'),
        ('Work While You Study', 'Work While You Study'),
        ('General Front Office', 'General Front Office'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Contacted', 'Contacted'),
        ('Partially Paid', 'Partially Paid'),
        ('Paid', 'Paid'),
        ('Link Sent', 'Link Sent'),
        ('Refunded', 'Refunded'),
    ]

    CRM_STATUS_CHOICES = [
        ('New Lead', 'New Lead'),
        ('In Progress', 'In Progress'),
        ('Closed Won', 'Closed Won'),
        ('Closed Lost', 'Closed Lost'),
    ]

    PIPELINE_STAGE_CHOICES = [
        ('Intake', 'Intake'),
        ('Assessment', 'Assessment'),
        ('Documentation', 'Documentation'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
    ]

    VISA_STAGE_CHOICES = [
        ('Not Applicable', 'Not Applicable'),
        ('Profile Assessment', 'Profile Assessment'),
        ('APS Certificate', 'APS Certificate'),
        ('Blocked Account', 'Blocked Account'),
        ('Embassy Appointment', 'Embassy Appointment'),
        ('Visa Approved', 'Visa Approved'),
        ('Visa Rejected', 'Visa Rejected'),
    ]

    FOLLOW_UP_STATUS_CHOICES = [
        ('Due Today', 'Due Today'),
        ('Overdue', 'Overdue'),
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
        ('Pending', 'Pending'),
    ]

    id = models.CharField(max_length=50, primary_key=True, default=generate_inquiry_id)
    token_number = models.CharField(max_length=50, unique=True, db_index=True)
    lead_type = models.CharField(max_length=50, choices=LEAD_TYPE_CHOICES, default='Walk-in')
    name = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    category = models.CharField(max_length=100, default='Education')
    department = models.CharField(max_length=100, null=True, blank=True)
    course_name = models.CharField(max_length=255, null=True, blank=True)
    path_name = models.CharField(max_length=255, null=True, blank=True)
    batch_name = models.CharField(max_length=255, null=True, blank=True)
    slot = models.CharField(max_length=100, null=True, blank=True)

    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    payment_status = models.CharField(max_length=50, choices=PAYMENT_STATUS_CHOICES, default='Pending')

    class_link = models.URLField(null=True, blank=True)
    source = models.CharField(max_length=255, default='Front-Desk Reception')

    crm_status = models.CharField(max_length=50, choices=CRM_STATUS_CHOICES, default='New Lead')
    pipeline_stage = models.CharField(max_length=50, choices=PIPELINE_STAGE_CHOICES, default='Intake')
    visa_stage = models.CharField(max_length=50, choices=VISA_STAGE_CHOICES, default='Not Applicable')

    assigned_staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_inquiries'
    )

    intake_notes = models.TextField(null=True, blank=True)
    ai_score = models.IntegerField(default=0)
    ai_path = models.CharField(max_length=255, null=True, blank=True)
    ai_action_plan = models.JSONField(default=dict, blank=True)

    # Walk-in Terminal Info
    visitor_purpose = models.CharField(max_length=255, null=True, blank=True)
    accompanied_by = models.CharField(max_length=255, null=True, blank=True)
    id_proof_verified = models.BooleanField(default=False)
    check_in_time = models.CharField(max_length=50, null=True, blank=True)
    receptionist_name = models.CharField(max_length=255, null=True, blank=True)

    follow_up_date = models.DateField(null=True, blank=True, db_index=True)
    follow_up_status = models.CharField(max_length=50, choices=FOLLOW_UP_STATUS_CHOICES, default='Pending')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.token_number}] {self.name} - {self.category}"

    def save(self, *args, **kwargs):
        if not self.token_number:
            prefix = "ILA-WALK" if self.lead_type == "Walk-in" else "ILA-ONL"
            count = Inquiry.objects.filter(lead_type=self.lead_type).count() + 101
            self.token_number = f"{prefix}-{count}"
        super().save(*args, **kwargs)


class FollowUpRecord(models.Model):
    CHANNEL_CHOICES = [
        ('Phone Call', 'Phone Call'),
        ('WhatsApp', 'WhatsApp'),
        ('In-Person', 'In-Person'),
        ('Email', 'Email'),
    ]

    OUTCOME_CHOICES = [
        ('Interested - Callback', 'Interested - Callback'),
        ('Docs Pending', 'Docs Pending'),
        ('Fee Paid', 'Fee Paid'),
        ('Not Interested', 'Not Interested'),
        ('Appointment Booked', 'Appointment Booked'),
    ]

    id = models.CharField(max_length=50, primary_key=True, default=generate_followup_id)
    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE, related_name='follow_up_history')
    staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    channel = models.CharField(max_length=50, choices=CHANNEL_CHOICES, default='Phone Call')
    notes = models.TextField()
    outcome = models.CharField(max_length=50, choices=OUTCOME_CHOICES, default='Interested - Callback')
    next_follow_up_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Follow-up on {self.inquiry.token_number} - {self.outcome}"


class VisitorLog(models.Model):
    page = models.CharField(max_length=255)
    time_spent_seconds = models.IntegerField(default=0)
    ip_address = models.CharField(max_length=50, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.page} ({self.time_spent_seconds}s) at {self.timestamp}"
