import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


# ---------------------------------------------------------------------------
# 1. Courses & Permanent Curriculum Models
# ---------------------------------------------------------------------------

class CourseCategory(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    department = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=30, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ai_hub_course_categories'
        verbose_name = 'Course Category'
        verbose_name_plural = 'Course Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class LibraryCourse(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='authored_ai_courses'
    )
    title = models.CharField(max_length=500, db_index=True)
    subtitle = models.CharField(max_length=500, blank=True, default="")
    category = models.CharField(max_length=150, blank=True, default="General")
    sub_category = models.CharField(max_length=150, blank=True, default="")
    delivery_path = models.CharField(max_length=100, blank=True, default="home")
    batch_slot = models.CharField(max_length=100, blank=True, default="")
    overview = models.TextField(blank=True, default="")
    total_chapters = models.PositiveIntegerField(default=0)
    source_session_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    tags = models.JSONField(default=list, blank=True)
    is_favorite = models.BooleanField(default=False, db_index=True)
    studied_by = models.CharField(max_length=255, blank=True, default="")
    target_audience = models.CharField(max_length=255, blank=True, default="")

    # Locked & Permanent Store Fields
    is_permanent = models.BooleanField(default=False, db_index=True)
    locked = models.BooleanField(default=False)
    download_count = models.PositiveIntegerField(default=0)
    last_downloaded_at = models.DateTimeField(null=True, blank=True)

    # Structured Payloads (JSONB in PostgreSQL / JSON in SQLite)
    admin_course_data = models.JSONField(default=dict, blank=True)
    slide_ai_course_data = models.JSONField(default=dict, blank=True)
    intelli_coach_course_data = models.JSONField(default=dict, blank=True)
    authorized_structure = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        db_table = 'ai_hub_courses'
        verbose_name = 'Library Course'
        verbose_name_plural = 'Library Courses'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} ({self.id})"


class CourseChapter(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    course = models.ForeignKey(LibraryCourse, on_delete=models.CASCADE, related_name='chapters')
    chapter_number = models.PositiveIntegerField()
    title = models.CharField(max_length=500)
    summary = models.TextField(blank=True, default="")
    content = models.TextField(blank=True, default="")
    is_completed = models.BooleanField(default=False)
    sub_topics = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = 'ai_hub_course_chapters'
        ordering = ['chapter_number']
        unique_together = ('course', 'chapter_number')

    def __str__(self):
        return f"Ch {self.chapter_number}: {self.title}"


class CourseVersionSnapshot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(LibraryCourse, on_delete=models.CASCADE, related_name='version_snapshots')
    version_number = models.CharField(max_length=30)  # e.g., 'v1.0', 'v1.1'
    label = models.CharField(max_length=255, blank=True, default="")
    chapters_snapshot = models.JSONField(default=list)
    auto_saved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_hub_course_versions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.course_id} - {self.version_number}"


# ---------------------------------------------------------------------------
# 2. Universal AI Chat & Sessions Models
# ---------------------------------------------------------------------------

class ChatSession(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ai_hub_chat_sessions'
    )
    title = models.CharField(max_length=500, db_index=True)
    is_pinned = models.BooleanField(default=False, db_index=True)
    product_type = models.CharField(max_length=80, default='ila_chat', db_index=True)
    product_params = models.JSONField(default=dict, blank=True)
    course_plan = models.JSONField(default=dict, blank=True, null=True)
    autonomous_plan = models.JSONField(default=dict, blank=True, null=True)
    studied_by = models.CharField(max_length=255, blank=True, default="")
    target_audience = models.CharField(max_length=255, blank=True, default="")
    is_permanent = models.BooleanField(default=False)
    locked = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        db_table = 'ai_hub_chat_sessions'
        ordering = ['-is_pinned', '-updated_at']

    def __str__(self):
        return f"{self.title} [{self.product_type}]"


class ChatMessage(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=[('user', 'User'), ('assistant', 'Assistant'), ('system', 'System')])
    content = models.TextField()
    model = models.CharField(max_length=100, blank=True, default="")
    model_display_name = models.CharField(max_length=100, blank=True, default="")
    response_time_ms = models.PositiveIntegerField(null=True, blank=True)
    documents = models.JSONField(default=list, blank=True)
    grounding_sources = models.JSONField(default=list, blank=True)
    next_module_info = models.JSONField(default=dict, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_hub_chat_messages'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role}: {self.content[:40]}..."


class LegacyChatHistory(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    query = models.TextField()
    response = models.TextField()
    model = models.CharField(max_length=100)
    model_display_name = models.CharField(max_length=100)
    response_time_ms = models.PositiveIntegerField(null=True, blank=True)
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'ai_hub_legacy_chat_history'
        ordering = ['-created_at']

    def __str__(self):
        return f"Query: {self.query[:40]}"


# ---------------------------------------------------------------------------
# 3. University Tie-Up CRM & Outreach Models
# ---------------------------------------------------------------------------

class AntiSpamStatus(models.TextChoices):
    VERIFIED = 'verified', 'Verified'
    FLAGGED_GENERIC = 'flagged_generic', 'Flagged Generic'
    BOUNCED = 'bounced', 'Bounced'
    BLOCKED = 'blocked', 'Blocked'


class TieupLead(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    session_id = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    name = models.CharField(max_length=300, db_index=True)
    category = models.CharField(max_length=150)
    sub_category = models.CharField(max_length=150, blank=True, default="")
    country = models.CharField(max_length=100, db_index=True)
    region = models.CharField(max_length=100, blank=True, default="")
    location_main = models.CharField(max_length=255)
    location_sub = models.CharField(max_length=255, blank=True, default="")
    contact_person = models.CharField(max_length=200)
    contact_title = models.CharField(max_length=200)
    contact_email = models.EmailField(db_index=True)
    contact_phone = models.CharField(max_length=50, blank=True, default="")
    website_url = models.URLField(max_length=500, blank=True, default="")

    # Partnership Status & Scoring
    is_partner = models.BooleanField(default=False, db_index=True)
    compatibility_score = models.IntegerField(default=88)
    commission_percent = models.FloatField(default=15.0)
    matching_criteria = models.JSONField(default=list, blank=True)
    direct_source_page_url = models.URLField(max_length=500, blank=True, default="")

    # Institutional & Academic Criteria
    student_requirements = models.TextField(blank=True, default="")
    institution_criteria = models.TextField(blank=True, default="")
    terms_of_partnership = models.TextField(blank=True, default="")
    terms_summary = models.TextField(blank=True, default="")
    partnership_terms = models.JSONField(default=dict, blank=True)
    min_ielts_score = models.FloatField(default=6.0)
    german_level_required = models.CharField(max_length=100, default="None (English Only)")
    tuition_fee_yearly = models.CharField(max_length=100, default="€0 (Public)")
    tuition_amount_eur = models.FloatField(default=0.0)
    scholarship_available = models.BooleanField(default=False)
    scholarship_details = models.TextField(blank=True, default="")
    course_list = models.JSONField(default=list, blank=True)
    mou_document_url = models.URLField(max_length=500, blank=True, default="")

    # Anti-Spam & Health
    anti_spam_status = models.CharField(max_length=30, choices=AntiSpamStatus.choices, default=AntiSpamStatus.VERIFIED)
    anti_spam_notes = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ai_hub_tieup_leads'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.name} ({self.country})"


class TieupPolicy(models.Model):
    id = models.CharField(max_length=100, primary_key=True, default='global_policy')
    min_commission_percent = models.FloatField(default=15.0)
    target_commission_percent = models.FloatField(default=20.0)
    partnership_criteria = models.TextField(default="")
    student_requirements_guidelines = models.TextField(default="")
    terms_expectations = models.TextField(default="")
    preferred_payment_terms = models.CharField(max_length=255, default="Net 30 on student semester enrollment")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ai_hub_tieup_policies'

    def __str__(self):
        return f"Policy {self.id} ({self.min_commission_percent}% - {self.target_commission_percent}%)"


class OutreachLogStatus(models.TextChoices):
    DELIVERED = 'delivered', 'Delivered'
    OPENED = 'opened', 'Opened'
    REPLIED = 'replied', 'Replied'
    FLAGGED = 'flagged_generic', 'Flagged Generic'
    BOUNCED = 'bounced', 'Bounced'
    BLOCKED = 'blocked', 'Blocked'


class OutreachStatusLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lead = models.ForeignKey(TieupLead, on_delete=models.SET_NULL, null=True, blank=True, related_name='outreach_logs')
    institution_name = models.CharField(max_length=300)
    recipient_email = models.EmailField(db_index=True)
    recipient_name = models.CharField(max_length=200, blank=True, default="")
    sender_email = models.EmailField(blank=True, default="")
    subject = models.CharField(max_length=500)
    status = models.CharField(max_length=30, choices=OutreachLogStatus.choices, default=OutreachLogStatus.DELIVERED)
    flag_reason = models.TextField(blank=True, default="")
    spam_score = models.IntegerField(default=0)
    phase = models.CharField(max_length=50, default='outreach')
    followup_count = models.IntegerField(default=0)
    last_followup_at = models.DateTimeField(null=True, blank=True)
    meeting_scheduled_at = models.DateTimeField(null=True, blank=True)
    meeting_link = models.URLField(blank=True, default="")
    meeting_agenda = models.TextField(blank=True, default="")
    response_excerpt = models.TextField(blank=True, default="")
    response_sentiment = models.CharField(max_length=50, blank=True, default="")
    ai_suggested_reply = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    last_checked = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ai_hub_outreach_status_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.institution_name} ({self.status})"


class SmtpConfiguration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, default="Default SMTP")
    host = models.CharField(max_length=255, default="smtp.gmail.com")
    port = models.IntegerField(default=587)
    sender_email = models.EmailField()
    sender_name = models.CharField(max_length=200, blank=True, default="")
    app_password = models.CharField(max_length=255)
    is_secure = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    daily_limit = models.IntegerField(default=500)
    sent_today = models.IntegerField(default=0)
    last_used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ai_hub_smtp_configurations'

    def __str__(self):
        return f"{self.name} ({self.sender_email})"


# ---------------------------------------------------------------------------
# 4. AI Hub 17-Product Presets & Async Jobs
# ---------------------------------------------------------------------------

class AIProductPreset(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=255)
    icon = models.CharField(max_length=100, blank=True, default="Brain")
    description = models.TextField(blank=True, default="")
    system_prompt = models.TextField(blank=True, default="")
    default_model = models.CharField(max_length=100, default="gemini-2.5-flash")
    temperature = models.FloatField(default=0.7)
    tags = models.JSONField(default=list, blank=True)
    input_schema = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ai_hub_product_presets'
        ordering = ['name']

    def __str__(self):
        return self.name


class GenerationJob(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job_type = models.CharField(max_length=100)  # e.g., 'autonomous_course', 'bulk_outreach', 'docx_export'
    status = models.CharField(max_length=50, default='pending')  # 'pending', 'processing', 'completed', 'failed'
    progress = models.IntegerField(default=0)
    payload = models.JSONField(default=dict, blank=True)
    result = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'ai_hub_generation_jobs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.job_type} - {self.id} ({self.status})"


# ---------------------------------------------------------------------------
# 5. Central Telemetry, Logs & Metric Snapshots
# ---------------------------------------------------------------------------

class SystemActivityLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    action_type = models.CharField(max_length=100)
    module = models.CharField(max_length=100)
    description = models.TextField()
    user_identifier = models.CharField(max_length=255, blank=True, default="system")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'ai_hub_activity_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.module}] {self.action_type} - {self.created_at}"


class MetricSnapshot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    metric_key = models.CharField(max_length=100, db_index=True)
    metric_value = models.FloatField()
    dimensions = models.JSONField(default=dict, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'ai_hub_metric_snapshots'
        ordering = ['-recorded_at']

    def __str__(self):
        return f"{self.metric_key}: {self.metric_value}"
