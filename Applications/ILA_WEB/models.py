from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

# Export AI Consultant Token Usage Log
from .IlaConsultant.models import AITokenUsageLog  # noqa: E402


# ==============================================================================
# 1. USER & MULTI-TIER ROLE-BASED ACCESS CONTROL (RBAC) - PART 7
# ==============================================================================
class FranchisePartner(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    region = models.CharField(max_length=150, default='Germany / EU')
    franchise_token = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='franchises_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} [{self.region}] - {self.franchise_token}"


# ==============================================================================
# 2. OMNICHANNEL INQUIRY & INTAKE DESK (FRONT OFFICE & CRM) - PART 1 & 3
# ==============================================================================
class Inquiry(models.Model):
    CATEGORY_CHOICES = [
        ('Education', 'Education & All Courses'),
        ('Study Abroad', 'Study Abroad Hub'),
        ('Visa', 'Visa and Services Hub'),
        ('Jobs', 'Job and Career Hub'),
        ('Work While You Study', 'Work While You Study Track'),
        ('Rewards', 'Rewards Program & Consultant'),
        ('General Front Office', 'General Front Office Reception'),
    ]

    # Core Lead & Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    type = models.CharField(
        max_length=50,
        default='Online',
        choices=[('Walk-in', 'Walk-in'), ('Online', 'Online'), ('Referral', 'Referral'), ('Phone', 'Phone')]
    )
    token_number = models.CharField(max_length=50, blank=True, null=True, unique=True)

    # Section & Routing
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='General Front Office')
    department = models.CharField(max_length=100, blank=True, null=True)

    # Contextual Keyword & Section Tracking
    target_keyword = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="Primary keyword/title (e.g., 'Opportunity Card', 'Senior React Dev')"
    )
    keywords = models.JSONField(
        default=list, blank=True,
        help_text="Searchable tag list extracted from incoming redirection"
    )
    source_page = models.CharField(
        max_length=150, blank=True, null=True,
        help_text="Page from which applicant arrived (e.g., 'VisaPage', 'JobsPage')"
    )
    source_url = models.CharField(
        max_length=500, blank=True, null=True,
        help_text="Full origin URL/hash including query parameters"
    )

    # Structured Section Data (Complete snapshot of form state)
    section_data = models.JSONField(
        default=dict, blank=True,
        help_text="All section-specific form fields (batches, tracks, tiers, etc.)"
    )

    # Normalized Quick-Filter Columns
    course = models.CharField(max_length=255, blank=True, null=True)
    path = models.CharField(max_length=255, blank=True, null=True)
    batch = models.CharField(max_length=255, blank=True, null=True)
    slot = models.CharField(max_length=255, blank=True, null=True)
    target_country = models.CharField(max_length=100, blank=True, null=True)
    visa_type = models.CharField(max_length=150, blank=True, null=True)
    job_role = models.CharField(max_length=150, blank=True, null=True)
    resume_url = models.URLField(max_length=500, blank=True, null=True)
    reward_tier = models.CharField(max_length=100, blank=True, null=True)
    referral_code = models.CharField(max_length=100, blank=True, null=True)

    # CRM Pipeline & Operational Fields
    payment_status = models.CharField(max_length=50, default='Pending')
    crm_status = models.CharField(max_length=50, default='New Lead')
    pipeline_stage = models.CharField(max_length=50, default='Intake')
    price = models.CharField(max_length=50, default='Pending Consultation')
    ai_score = models.IntegerField(null=True, blank=True)
    ai_path = models.CharField(max_length=255, blank=True, null=True)

    # Operational/Staff Tracking
    assigned_staff_id = models.CharField(max_length=50, blank=True, null=True)
    assigned_staff_name = models.CharField(max_length=255, blank=True, null=True)
    follow_up_date = models.CharField(max_length=50, blank=True, null=True)
    follow_up_status = models.CharField(max_length=50, blank=True, null=True)
    visa_processing_stage = models.CharField(max_length=100, blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'crm_status']),
            models.Index(fields=['target_keyword']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return f"{self.name} - {self.category} ({self.payment_status})"

    def save(self, *args, **kwargs):
        if not self.token_number:
            self.token_number = f"INQ-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class FollowUpRecord(models.Model):
    inquiry = models.ForeignKey(Inquiry, related_name='follow_ups', on_delete=models.CASCADE)
    date = models.CharField(max_length=50, default='2026-09-09')
    staff_name = models.CharField(max_length=255, default='Staff')
    channel = models.CharField(
        max_length=50,
        choices=[('Phone Call', 'Phone Call'), ('WhatsApp', 'WhatsApp'), ('In-Person', 'In-Person'), ('Email', 'Email')],
        default='Phone Call'
    )
    notes = models.TextField(blank=True, default='')
    outcome = models.CharField(max_length=100, default='Interested')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"Follow-up on {self.inquiry.name} by {self.staff_name} ({self.date})"




# ==============================================================================
# 3. AI TIE-UP ENGINE & PARTNER REGISTRY - PART 2, 3 & 5
# ==============================================================================
class PartnerInstitution(models.Model):
    CATEGORY_CHOICES = [
        ('University', 'Public / Private University'),
        ('Corporate Employer', 'Corporate Employer / Placement'),
        ('Hospital / Healthcare', 'Hospital / Healthcare'),
        ('Vocational School (Ausbildung)', 'Vocational School (Ausbildung)'),
    ]
    STATUS_CHOICES = [
        ('Target Identified', '1. Target Identified'),
        ('Outreach Drafted', '2. Outreach Drafted'),
        ('Proposal Dispatched', '3. Proposal Dispatched'),
        ('In Discussion', '4. In Discussion'),
        ('MOU Signed', '5. MOU Signed'),
        ('Active Tie-up Partner', '6. Active Tie-up Partner'),
    ]

    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    country = models.CharField(max_length=100, default='Germany')
    city = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=255)
    email = models.EmailField()
    target_criteria = models.TextField(help_text="Matching qualifications criteria for Indian student corridor")
    commission_ratio = models.CharField(max_length=150, help_text="Profit/Commission or institutional terms")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Target Identified')
    synced_departments = models.JSONField(default=list, help_text="e.g. ['Study Abroad', 'HR', 'Finance']")
    last_updated = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.country}) - {self.status}"


class TieUpOutreachLog(models.Model):
    partner = models.ForeignKey(PartnerInstitution, related_name='outreach_logs', on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    generated_proposal_text = models.TextField()
    dispatched_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    is_dispatched = models.BooleanField(default=False)
    dispatched_at = models.DateTimeField(blank=True, null=True)
    response_notes = models.TextField(blank=True)

    def __str__(self):
        return f"Outreach: {self.subject} -> {self.partner.name}"


# ==============================================================================
# 4. MARKETING STUDIO & CAMPAIGN MANAGEMENT - PART 2 & 7
# ==============================================================================
class MarketingCampaign(models.Model):
    name = models.CharField(max_length=255)
    channel = models.CharField(
        max_length=100,
        choices=[
            ('Meta Ads', 'Meta Ads'),
            ('Google PPC', 'Google PPC'),
            ('WhatsApp', 'WhatsApp'),
            ('Field Visits', 'Field Visits'),
            ('SEO Organic', 'SEO Organic')
        ]
    )
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    spent = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    target_geography = models.CharField(max_length=200, default='Pan India')
    status = models.CharField(
        max_length=50,
        default='Active',
        choices=[('Active', 'Active'), ('Completed', 'Completed'), ('Paused', 'Paused')]
    )
    leads_count = models.IntegerField(default=0)
    conversions_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} [{self.channel}] - {self.status}"


class FieldVisitLog(models.Model):
    institution_visited = models.CharField(max_length=255)
    location = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=255)
    summary = models.TextField()
    next_action = models.CharField(max_length=255)
    visit_date = models.DateField()
    logged_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.institution_visited} on {self.visit_date}"


class DepartmentMeeting(models.Model):
    department = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    agenda = models.TextField()
    attendees = models.CharField(max_length=255)
    date = models.DateField()
    time = models.CharField(max_length=50, default='10:00 AM')
    status = models.CharField(
        max_length=50,
        default='Scheduled',
        choices=[('Scheduled', 'Scheduled'), ('Completed', 'Completed')]
    )

    def __str__(self):
        return f"{self.title} ({self.department}) - {self.date}"


# ==============================================================================
# 5. REWARDS PROGRAM & JUNIOR CONSULTANT NETWORK - PART 2 & 6
# ==============================================================================
class RewardProfile(models.Model):
    TIER_CHOICES = [
        ('Junior Consultant', 'Junior Consultant'),
        ('Senior Executive Consultant', 'Senior Executive Consultant'),
        ('Global Venture Partner', 'Global Venture Partner')
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reward_profile')
    consultant_id = models.CharField(max_length=50, unique=True)
    tier = models.CharField(max_length=50, default='Junior Consultant', choices=TIER_CHOICES)
    active_points = models.IntegerField(default=0)
    lifetime_points = models.IntegerField(default=0)
    monthly_points = models.IntegerField(default=0)
    cash_earned = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    promoted_categories = models.JSONField(default=list, help_text="Categories chosen to promote")
    work_certificate_issued = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def add_points(self, points, reason="Milestone"):
        self.active_points += points
        self.lifetime_points += points
        self.monthly_points += points
        if self.monthly_points >= 1000:
            self.work_certificate_issued = True
        self.save()

    def __str__(self):
        return f"{self.consultant_id} ({self.tier}) - Points: {self.active_points}"


class RewardTransaction(models.Model):
    MILESTONE_CHOICES = [
        ('Inquiry Generated (10 pts)', 'Inquiry Generated'),
        ('Successful Enrollment (50 pts)', 'Enrollment Conversion'),
        ('Monthly Payout Unlock (1000 pts)', 'Monthly Payout')
    ]

    profile = models.ForeignKey(RewardProfile, related_name='transactions', on_delete=models.CASCADE)
    points = models.IntegerField()
    description = models.CharField(max_length=255)
    milestone_type = models.CharField(max_length=50, choices=MILESTONE_CHOICES)
    reference_inquiry_id = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.profile.consultant_id}: {self.points} pts ({self.description})"


# ==============================================================================
# 6. WORK WHILE STUDY & AI PRELIMINARY INTERVIEWS - PART 2
# ==============================================================================
class WorkStudyApplication(models.Model):
    TRACK_CHOICES = [
        ('Work While You Learn in India', 'Work While You Learn in India'),
        ('Part time While You Study Abroad', 'Part time While You Study Abroad'),
        ('German Project Onboarding Pathway', 'German Project Onboarding Pathway'),
        ('Junior Consultant Track', 'Rewards Plans & Junior Consultant Track'),
    ]

    candidate_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    track = models.CharField(max_length=100, choices=TRACK_CHOICES)
    sub_domain = models.CharField(max_length=150)
    resume_file = models.FileField(upload_to='resumes/', blank=True, null=True)
    
    # AI Interview Details
    ai_preliminary_interview_link = models.CharField(max_length=255, blank=True, null=True)
    ai_interview_score = models.IntegerField(default=0)
    ai_interview_status = models.CharField(
        max_length=50,
        default='Pending AI Link',
        choices=[
            ('Pending AI Link', 'Pending AI Link'),
            ('Completed', 'Completed'),
            ('Scheduled for HR Round 2', 'Scheduled for HR Round 2')
        ]
    )
    ai_interview_transcript = models.TextField(blank=True)
    
    is_onboarded_to_dept = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidate_name} [{self.track}] - Score: {self.ai_interview_score}"


# ==============================================================================
# 7. DYNAMIC VISA REQUIREMENTS & SETTLEMENT SUPPORT - PART 3 & 4
# ==============================================================================
class VisaRequirementRule(models.Model):
    country = models.CharField(max_length=100)
    visa_type = models.CharField(max_length=100)
    blocked_funds_amount = models.CharField(max_length=100, help_text="e.g. €11,900 / yr")
    embassy_queue_days = models.CharField(max_length=50, default="15-28 Days")
    primary_authority = models.CharField(max_length=200)
    mandatory_checklists = models.JSONField(default=list)
    last_monitored_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.country} - {self.visa_type}"


class SettlementServiceRequest(models.Model):
    SERVICE_CHOICES = [
        ('Airport Pickup & Reception', 'Airport Pickup & Reception'),
        ('Accommodation & Room Arrangement (WG)', 'Accommodation & Room Arrangement (WG)'),
        ('Documentation & Bank Account (Anmeldung/Expatrio)', 'Documentation & Bank Account (Anmeldung/Expatrio)'),
        ('Part-time Job Placement Assistance', 'Part-time Job Placement Assistance'),
    ]

    candidate_name = models.CharField(max_length=255)
    email = models.EmailField()
    target_country = models.CharField(max_length=100, default='Germany')
    arrival_date = models.DateField(blank=True, null=True)
    services_requested = models.JSONField(default=list)
    status = models.CharField(max_length=50, default='Pending Coordinator Assignment')
    assigned_coordinator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Settlement: {self.candidate_name} ({self.target_country}) - {self.status}"


# ==============================================================================
# 8. CORE ENTERPRISE OPERATIONS (TASKS, ATTENDANCE, APPROVALS) - PART 7
# ==============================================================================
class EnterpriseTask(models.Model):
    title = models.CharField(max_length=255, default='Enterprise Task')
    description = models.TextField(blank=True)
    assigned_to_dept = models.CharField(max_length=100, default='General')
    status = models.CharField(
        max_length=50,
        choices=[
            ('Pending', 'Pending'),
            ('In Progress', 'In Progress'),
            ('Success', 'Success'),
            ('Negative', 'Negative')
        ],
        default='Pending'
    )
    priority = models.CharField(
        max_length=50,
        choices=[('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low')],
        default='Medium'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} [{self.assigned_to_dept}] ({self.status})"


class AttendanceLog(models.Model):
    staff_id = models.CharField(max_length=50, default='EMP-001')
    staff_name = models.CharField(max_length=255, default='Staff Member')
    check_in_time = models.CharField(max_length=50, default='09:00 AM')
    status = models.CharField(max_length=50, default='Present')
    date = models.CharField(max_length=50, default='2026-09-09')

    def __str__(self):
        return f"{self.staff_name} ({self.staff_id}) - {self.date}: {self.status}"


class ApprovalRequest(models.Model):
    type = models.CharField(max_length=100, default='General')
    description = models.TextField(blank=True, default='')
    requested_by = models.CharField(max_length=255, default='Staff')
    department = models.CharField(max_length=100, default='Operations')
    status = models.CharField(
        max_length=50,
        choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')],
        default='Pending'
    )
    date = models.CharField(max_length=50, default='2026-09-09')

    def __str__(self):
        return f"{self.type} by {self.requested_by} ({self.status})"


# ==============================================================================
# 9. LIVE CONSULTANT & CHAT SESSION TRACKING
# ==============================================================================
class ConsultantSession(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active Session'),
        ('resolved', 'Resolved / Closed'),
        ('converted_to_lead', 'Converted to CRM Inquiry'),
        ('abandoned', 'Abandoned'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_key = models.CharField(max_length=128, unique=True, db_index=True, help_text="Client session token or UUID")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='consultant_sessions')
    user_email = models.EmailField(blank=True, null=True)
    user_phone = models.CharField(max_length=50, blank=True, null=True)
    user_name = models.CharField(max_length=150, blank=True, null=True)
    
    initial_topic = models.CharField(max_length=50, default='general')
    current_topic = models.CharField(max_length=50, default='general')
    
    # Metadata & Tracking
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    source_url = models.URLField(blank=True, null=True)
    
    # CRM Integration Link
    inquiry = models.ForeignKey('Inquiry', on_delete=models.SET_NULL, null=True, blank=True, related_name='consultant_sessions')
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='active')
    total_messages = models.PositiveIntegerField(default=0)
    total_tokens_used = models.PositiveIntegerField(default=0)
    
    last_activity = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-last_activity']

    def __str__(self):
        user_identifier = self.user_email or (self.user.username if self.user else 'Guest')
        return f"Session {self.session_key[:8]} ({user_identifier}) - {self.current_topic}"


class ConsultantChatMessage(models.Model):
    ROLE_CHOICES = [
        ('user', 'User / Visitor'),
        ('assistant', 'Ilas AI Consultant'),
        ('system', 'System Prompt / Note'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ConsultantSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    suggested_actions = models.JSONField(default=list, blank=True)
    
    # AI Token Telemetry
    prompt_tokens = models.PositiveIntegerField(default=0)
    completion_tokens = models.PositiveIntegerField(default=0)
    total_tokens = models.PositiveIntegerField(default=0)
    
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"[{self.role}] {self.content[:40]} ({self.timestamp:%H:%M:%S})"

