from django.db import models


class Application(models.Model):
    STATUS_CHOICES = [
        ('received', 'Received'),
        ('under_review', 'Under Review'),
        ('accepted', 'Accepted'),
        ('contacted', 'Contacted'),
        ('archived', 'Archived'),
    ]

    PACKAGE_CHOICES = [
        ('standard', 'The Co-Founder Syndicate'),
        ('partnership', 'The Enterprise Alliance (Partner)'),
        ('candidate', 'The Enterprise Alliance (Candidate)'),
        ('remote', 'ILA Ent Pilot Mode (Remote)'),
    ]

    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    business_name = models.CharField(max_length=255)
    industry = models.CharField(max_length=100)
    package_option = models.CharField(max_length=50, choices=PACKAGE_CHOICES, default='standard')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='received')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} ({self.business_name}) - {self.package_option}"


class PackageTier(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200)
    share_capital = models.CharField(max_length=100, default='€25,000')
    setup_fee = models.CharField(max_length=100)
    ownership = models.CharField(max_length=150)
    monthly_fee = models.CharField(max_length=100, blank=True, null=True)
    features = models.JSONField(default=list, help_text="List of feature bullet points")
    highlight = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return self.name


class ChatMessageLog(models.Model):
    session_id = models.CharField(max_length=120, db_index=True, default="default-session", blank=True, help_text="Frontend session UUID")
    prompt = models.TextField()
    response = models.TextField()
    model_used = models.CharField(max_length=100, default="gemini-2.5-flash")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"[{self.created_at.strftime('%Y-%m-%d %H:%M')}] Session: {self.session_id[:8]}..."
