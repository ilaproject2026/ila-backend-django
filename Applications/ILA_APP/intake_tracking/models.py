from django.db import models


class DepartmentInquiry(models.Model):
    department = models.CharField(
        max_length=100,
        choices=[
            ("Education", "All Course Hub / Education"),
            ("Work While You Study", "Work While You Study Hub"),
            ("Study Abroad", "Study Abroad Hub"),
            ("Jobs", "Job & Career Hub"),
            ("Rewards", "Rewards Plan Hub"),
            ("Visa", "Visa & Service Hub"),
        ],
        default="Education",
    )
    inquiry_type = models.CharField(
        max_length=50,
        choices=[
            ("Walk-in", "Walk-in Reception"),
            ("Online Funnel", "Online Funnel"),
            ("WhatsApp Direct", "WhatsApp Direct"),
            ("Referral", "Referral"),
        ],
        default="Walk-in",
    )
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    program_of_interest = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ("New", "New"),
            ("Contacted", "Contacted"),
            ("In-Review", "In-Review"),
            ("Enrolled", "Enrolled"),
            ("Dropped", "Dropped"),
        ],
        default="New",
    )
    counselor_assigned = models.CharField(max_length=150, default="Front Office Lead")
    created_at = models.DateField(auto_now_add=True)
    last_contacted_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.department} ({self.status})"


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
