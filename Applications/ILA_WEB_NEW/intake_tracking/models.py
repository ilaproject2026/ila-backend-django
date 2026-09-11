from django.db import models


class DepartmentInquiry(models.Model):
    # Department & Categories
    department = models.CharField(
        max_length=100,
        default="Education",
    )
    category = models.CharField(
        max_length=100,
        default="General Front Office",
        blank=True
    )
    form_type = models.CharField(
        max_length=100,
        default="visa",
        blank=True,
        help_text="Originating form type (e.g. visa, course, job, earn-learn, walkin)"
    )
    inquiry_type = models.CharField(
        max_length=50,
        default="Online Funnel",
        blank=True
    )
    source = models.CharField(
        max_length=255,
        default="Website Unified Intake",
        blank=True
    )

    # Core Contact Information
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=50)

    # Program & Routing
    program_of_interest = models.CharField(max_length=255, blank=True)
    course = models.CharField(max_length=255, blank=True)
    path = models.CharField(max_length=255, blank=True)
    price = models.CharField(max_length=100, default="Complimentary Intake", blank=True)
    payment_status = models.CharField(max_length=50, default="Pending", blank=True)

    # AI Assessment Results
    ai_score = models.IntegerField(null=True, blank=True)
    ai_path = models.CharField(max_length=255, blank=True)
    ai_action_plan = models.JSONField(default=list, blank=True)

    # Processing & Lifecycle Status
    status = models.CharField(
        max_length=50,
        default="New",
    )
    crm_status = models.CharField(max_length=50, default="New Lead", blank=True)
    pipeline_stage = models.CharField(max_length=50, default="Intake", blank=True)
    doc_status = models.CharField(max_length=50, default="Pending", blank=True)
    counselor_assigned = models.CharField(max_length=150, default="Front Office Lead", blank=True)
    notes = models.TextField(blank=True)

    # Schema-flexible dynamic payload for any page/form
    dynamic_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Stores arbitrary dynamic key-values from any source page/form (e.g. educationLevel, languageSkills, visaHistory, hasBlockedAccount, workExpYears, preferredSalary, etc.)"
    )

    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_contacted_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.category or self.department} ({self.form_type or 'General'})"


class FollowUpAutoTriggerRule(models.Model):
    department = models.CharField(max_length=100, default="Education")
    trigger_name = models.CharField(max_length=255)
    event_type = models.CharField(
        max_length=100,
        choices=[
            ("incomplete_enrollment", "Incomplete Registration"),
            ("pending_payment", "Pending Payment / Stipend Sign-off"),
            ("document_pending", "Missing Documents"),
            ("profile_dropoff", "Profile Inactivity"),
        ],
        default="incomplete_enrollment",
    )
    channel = models.CharField(
        max_length=50,
        choices=[("Both", "WhatsApp + Email"), ("WhatsApp", "WhatsApp Only"), ("Email", "Email Only")],
        default="Both",
    )
    delay_hours = models.IntegerField(default=2)
    message_template = models.TextField(help_text="Dynamic template with {name} and {program}")
    is_active = models.BooleanField(default=True)
    execution_count = models.IntegerField(default=0)
    last_triggered = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"[{self.department}] {self.trigger_name} ({self.channel})"


class SocialMediaCampaign(models.Model):
    department = models.CharField(max_length=100, default="Education")
    title = models.CharField(max_length=255)
    content = models.TextField()
    channels = models.JSONField(default=list, help_text="e.g. ['Meta Ads', 'LinkedIn', 'Instagram']")
    target_audience = models.CharField(max_length=255, default="All Aspirants in India & Europe")
    status = models.CharField(
        max_length=50,
        choices=[("Draft", "Draft"), ("Published", "Published"), ("Scheduled", "Scheduled")],
        default="Draft",
    )
    scheduled_at = models.DateField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)
    reach_count = models.IntegerField(default=0)
    clicks_count = models.IntegerField(default=0)

    def __str__(self):
        return f"[{self.department}] {self.title} ({self.status})"
