import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

class TriggerEventChoices(models.TextChoices):
    STUDENT_REGISTRATION = 'student_registration', _('Step 1: Student Registration Intake')
    COURSE_ENROLLMENT = 'course_enrollment', _('Step 2: Course Enrolled & Active')
    PAYMENT_REMINDER = 'payment_reminder', _('Step 3: Fee Payment / Deposit Alert')
    CLASS_START_24H = 'class_start_24h', _('Step 4: Class 24h Countdown Alert')
    CLASS_START_1H = 'class_start_1h', _('Step 5: Class 1h Emergency Alert')
    PENDING_ENROLLMENT_24H = 'pending_enrollment_24h', _('Drop-off: Incomplete Intake (24h Recovery Nudge)')
    INCOMPLETE_REGISTRATION_48H = 'incomplete_registration_48h', _('Drop-off: Incomplete Registration (48h Recovery)')

class CommChannelChoices(models.TextChoices):
    WHATSAPP = 'WhatsApp', _('WhatsApp Gateway')
    EMAIL = 'Email', _('Email (SMTP / SendGrid)')
    SMS = 'SMS', _('SMS Gateway')
    MULTI_CHANNEL = 'Multi-Channel', _('Multi-Channel (Omni-channel)')

class CommCategoryChoices(models.TextChoices):
    WELCOME = 'Welcome & Onboarding', _('Welcome & Onboarding')
    ALERTS = 'Class & Schedule Alerts', _('Class & Schedule Alerts')
    FOLLOWUPS = 'Enrollment Follow-ups', _('Enrollment Follow-ups')
    RETENTION = 'Payment & Retention', _('Payment & Retention')

class CommunicationWorkflowRule(models.Model):
    """
    Admin-configurable automated lifecycle communication trigger rule
    """
    id = models.CharField(primary_key=True, max_length=64, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, help_text="e.g. Instant Welcome & Portal Access on Registration")
    trigger_event = models.CharField(max_length=64, choices=TriggerEventChoices.choices, default=TriggerEventChoices.STUDENT_REGISTRATION)
    category = models.CharField(max_length=64, choices=CommCategoryChoices.choices, default=CommCategoryChoices.WELCOME)
    channel = models.CharField(max_length=32, choices=CommChannelChoices.choices, default=CommChannelChoices.WHATSAPP)
    
    subject = models.CharField(max_length=255, help_text="Notification subject line or email subject")
    message_template = models.TextField(help_text="Supports {{name}}, {{course}}, {{time}}, {{tutor}}, {{portal_link}}")
    
    is_active = models.BooleanField(default=True)
    delay_minutes = models.PositiveIntegerField(default=0, help_text="0 for instant dispatch, 15, 60, 1440 mins")
    badge = models.CharField(max_length=64, default='Instant Zero-Latency')
    
    total_dispatched = models.PositiveIntegerField(default=0)
    delivered_count = models.PositiveIntegerField(default=0)
    opened_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)
    last_triggered = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Communication Workflow Rule')
        verbose_name_plural = _('Communication Workflow Rules')

    def __str__(self):
        return f"[{self.channel}] {self.name} ({self.get_trigger_event_display()})"


class DispatchLog(models.Model):
    """
    Real-time multi-channel communication dispatch log
    """
    id = models.CharField(primary_key=True, max_length=64, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(CommunicationWorkflowRule, related_name='logs', on_delete=models.CASCADE)
    recipient_name = models.CharField(max_length=128)
    recipient_email = models.EmailField(blank=True, default='')
    recipient_phone = models.CharField(max_length=32, blank=True, default='')
    course_or_batch = models.CharField(max_length=255, default='General Track')
    
    channel = models.CharField(max_length=32, choices=CommChannelChoices.choices, default=CommChannelChoices.WHATSAPP)
    status = models.CharField(max_length=32, default='Delivered')
    message_preview = models.TextField()
    latency_ms = models.PositiveIntegerField(default=350)
    
    dispatched_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    read_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-dispatched_at']
        verbose_name = _('Dispatch Log')
        verbose_name_plural = _('Dispatch Logs')

    def __str__(self):
        return f"{self.recipient_name} - {self.channel} ({self.status})"


class ConsultantChatSession(models.Model):
    session_id = models.CharField(max_length=64, unique=True, db_index=True)
    user_name = models.CharField(max_length=150, default="Guest Aspirant", blank=True)
    user_email = models.EmailField(blank=True, default="")
    user_phone = models.CharField(max_length=50, blank=True, default="")
    topic = models.CharField(max_length=50, default="general")
    status = models.CharField(
        max_length=32,
        choices=[
            ('active', 'Active Chatting'),
            ('resolved', 'Resolved by AI'),
            ('escalated', 'Escalated to Human Counselor'),
            ('closed', 'Closed Session'),
        ],
        default='active'
    )
    message_count = models.PositiveIntegerField(default=0)
    messages_history = models.JSONField(
        default=list,
        blank=True,
        help_text="Chronological conversation record [{id, role, content, timestamp, topic}]"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Contextual client parameters (e.g. current page, referral, device info)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = _('Consultant Chat Session')
        verbose_name_plural = _('Consultant Chat Sessions')

    def __str__(self):
        return f"Chat [{self.session_id[:8]}] - {self.user_name} ({self.topic})"


class ConsultantChatMessage(models.Model):
    id = models.CharField(primary_key=True, max_length=64, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        ConsultantChatSession,
        related_name='chat_messages',
        on_delete=models.CASCADE
    )
    sender = models.CharField(
        max_length=20,
        choices=[('user', 'User / Applicant'), ('assistant', 'Ilas AI Consultant')],
        default='user'
    )
    content = models.TextField()
    topic = models.CharField(max_length=50, default='general')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
        verbose_name = _('Consultant Chat Message')
        verbose_name_plural = _('Consultant Chat Messages')

    def __str__(self):
        return f"[{self.sender}] {self.content[:40]}..."
