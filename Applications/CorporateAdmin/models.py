import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


# ============================================================================
# ENUMS & CHOICES
# ============================================================================

class EntityStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Active'
    INACTIVE = 'INACTIVE', 'Inactive'
    SUSPENDED = 'SUSPENDED', 'Suspended'


class BranchStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Active'
    INACTIVE = 'INACTIVE', 'Inactive'


class RoleCode(models.TextChoices):
    SUPER_ADMIN = 'SUPER_ADMIN', 'Super Admin'
    CEO = 'CEO', 'Chief Executive Officer'
    GENERAL_MANAGER = 'GENERAL_MANAGER', 'General Manager'
    HR_ADMIN = 'HR_ADMIN', 'HR Admin'
    HR_MANAGER = 'HR_MANAGER', 'HR Manager'
    HR_EXECUTIVE = 'HR_EXECUTIVE', 'HR Executive'
    OPERATIONS_MANAGER = 'OPERATIONS_MANAGER', 'Operations Manager'
    OPERATIONS_EXECUTIVE = 'OPERATIONS_EXECUTIVE', 'Operations Executive'
    FINANCE_MANAGER = 'FINANCE_MANAGER', 'Finance Manager'
    FINANCE_EXECUTIVE = 'FINANCE_EXECUTIVE', 'Finance Executive'
    MARKETING_MANAGER = 'MARKETING_MANAGER', 'Marketing Manager'
    MARKETING_EXECUTIVE = 'MARKETING_EXECUTIVE', 'Marketing Executive'
    SALES_MANAGER = 'SALES_MANAGER', 'Sales Manager'
    SALES_EXECUTIVE = 'SALES_EXECUTIVE', 'Sales Executive'
    TEAM_LEAD = 'TEAM_LEAD', 'Team Lead'
    STAFF = 'STAFF', 'Staff'
    EMPLOYEE = 'EMPLOYEE', 'Employee'


class EmploymentType(models.TextChoices):
    FULL_TIME = 'FULL_TIME', 'Full Time'
    PART_TIME = 'PART_TIME', 'Part Time'
    CONTRACT = 'CONTRACT', 'Contract'
    INTERN = 'INTERN', 'Intern'


class EmploymentStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Active'
    ON_LEAVE = 'ON_LEAVE', 'On Leave'
    PROBATION = 'PROBATION', 'Probation'
    TERMINATED = 'TERMINATED', 'Terminated'


class InquirySource(models.TextChoices):
    WALK_IN = 'WALK_IN', 'Walk In'
    WEBSITE = 'WEBSITE', 'Website'
    PHONE = 'PHONE', 'Phone'
    REFERRAL = 'REFERRAL', 'Referral'
    CAMPAIGN = 'CAMPAIGN', 'Campaign'
    SOCIAL_MEDIA = 'SOCIAL_MEDIA', 'Social Media'


class InquiryPriority(models.TextChoices):
    LOW = 'LOW', 'Low'
    MEDIUM = 'MEDIUM', 'Medium'
    HIGH = 'HIGH', 'High'
    URGENT = 'URGENT', 'Urgent'


class InquiryStatus(models.TextChoices):
    NEW = 'NEW', 'New'
    CONTACTED = 'CONTACTED', 'Contacted'
    QUALIFIED = 'QUALIFIED', 'Qualified'
    ASSIGNED = 'ASSIGNED', 'Assigned'
    IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
    FOLLOW_UP = 'FOLLOW_UP', 'Follow Up'
    CONVERTED = 'CONVERTED', 'Converted'
    LOST = 'LOST', 'Lost'
    REJECTED = 'REJECTED', 'Rejected'
    CANCELLED = 'CANCELLED', 'Cancelled'


class LeadStatus(models.TextChoices):
    NEW = 'NEW', 'New'
    CONTACTED = 'CONTACTED', 'Contacted'
    QUALIFIED = 'QUALIFIED', 'Qualified'
    PROPOSAL = 'PROPOSAL', 'Proposal'
    NEGOTIATION = 'NEGOTIATION', 'Negotiation'
    WON = 'WON', 'Won'
    LOST = 'LOST', 'Lost'


class CandidateStage(models.TextChoices):
    APPLICATION = 'APPLICATION', 'Application'
    SCREENING = 'SCREENING', 'Screening'
    INTERVIEW = 'INTERVIEW', 'Interview'
    SELECTED = 'SELECTED', 'Selected'
    OFFER = 'OFFER', 'Offer'
    APPROVED = 'APPROVED', 'Approved'
    ONBOARDING = 'ONBOARDING', 'Onboarding'
    EMPLOYEE = 'EMPLOYEE', 'Employee'
    REJECTED = 'REJECTED', 'Rejected'


class OnboardingStatus(models.TextChoices):
    NOT_STARTED = 'NOT_STARTED', 'Not Started'
    IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
    PENDING_APPROVAL = 'PENDING_APPROVAL', 'Pending Approval'
    COMPLETED = 'COMPLETED', 'Completed'
    BLOCKED = 'BLOCKED', 'Blocked'


class DocumentationStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    SUBMITTED = 'SUBMITTED', 'Submitted'
    VERIFIED = 'VERIFIED', 'Verified'
    REJECTED = 'REJECTED', 'Rejected'


class ApprovalStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    APPROVED = 'APPROVED', 'Approved'
    REJECTED = 'REJECTED', 'Rejected'
    CANCELLED = 'CANCELLED', 'Cancelled'


class TaskPriority(models.TextChoices):
    LOW = 'LOW', 'Low'
    MEDIUM = 'MEDIUM', 'Medium'
    HIGH = 'HIGH', 'High'
    URGENT = 'URGENT', 'Urgent'


class TaskStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    ASSIGNED = 'ASSIGNED', 'Assigned'
    IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
    WAITING = 'WAITING', 'Waiting'
    COMPLETED = 'COMPLETED', 'Completed'
    OVERDUE = 'OVERDUE', 'Overdue'
    CANCELLED = 'CANCELLED', 'Cancelled'


class ApprovalType(models.TextChoices):
    LEAVE = 'LEAVE', 'Leave Request'
    EXPENSE = 'EXPENSE', 'Expense Reimbursement'
    ONBOARDING = 'ONBOARDING', 'Onboarding Sign-off'
    RECRUITMENT = 'RECRUITMENT', 'Job Offer / Hiring'
    EQUIPMENT = 'EQUIPMENT', 'Asset / Equipment'
    DEPARTMENT_REQUEST = 'DEPARTMENT_REQUEST', 'Department Request'
    OPERATIONAL = 'OPERATIONAL', 'Operational Approval'


class CampaignStatus(models.TextChoices):
    DRAFT = 'DRAFT', 'Draft'
    PLANNED = 'PLANNED', 'Planned'
    ACTIVE = 'ACTIVE', 'Active'
    PAUSED = 'PAUSED', 'Paused'
    COMPLETED = 'COMPLETED', 'Completed'
    CANCELLED = 'CANCELLED', 'Cancelled'


class OpportunityStage(models.TextChoices):
    QUALIFICATION = 'QUALIFICATION', 'Qualification'
    PROPOSAL = 'PROPOSAL', 'Proposal'
    NEGOTIATION = 'NEGOTIATION', 'Negotiation'
    CLOSED_WON = 'CLOSED_WON', 'Closed Won'
    CLOSED_LOST = 'CLOSED_LOST', 'Closed Lost'


class ExpenseStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    APPROVED = 'APPROVED', 'Approved'
    REJECTED = 'REJECTED', 'Rejected'
    PAID = 'PAID', 'Paid'


class NotificationType(models.TextChoices):
    INFO = 'INFO', 'Info'
    SUCCESS = 'SUCCESS', 'Success'
    WARNING = 'WARNING', 'Warning'
    URGENT = 'URGENT', 'Urgent'
    TASK = 'TASK', 'Task'
    APPROVAL = 'APPROVAL', 'Approval'
    LEAD = 'LEAD', 'Lead'


# ============================================================================
# CORE ABSTRACT MODELS
# ============================================================================

class TimeStampedUUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TenantScopedModel(TimeStampedUUIDModel):
    organization = models.ForeignKey(
        'Organization',
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)ss",
        db_index=True
    )

    class Meta:
        abstract = True


# ============================================================================
# ORGANIZATION & STRUCTURE
# ============================================================================

class Organization(TimeStampedUUIDModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    logo_url = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=EntityStatus.choices, default=EntityStatus.ACTIVE)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class Branch(TimeStampedUUIDModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='branches')
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    location = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=BranchStatus.choices, default=BranchStatus.ACTIVE)

    class Meta:
        verbose_name_plural = 'Branches'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.location}"


class Department(TimeStampedUUIDModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    department_head = models.ForeignKey(
        'Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='heading_departments'
    )
    budget = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=BranchStatus.choices, default=BranchStatus.ACTIVE)

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['organization', 'code'], name='unique_org_department_code')
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Team(TimeStampedUUIDModel):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='teams')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    team_lead = models.ForeignKey(
        'Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leading_teams'
    )
    status = models.CharField(max_length=20, choices=BranchStatus.choices, default=BranchStatus.ACTIVE)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.department.name})"


# ============================================================================
# IAM, PROFILE, ROLES & PERMISSIONS
# ============================================================================

class Profile(TimeStampedUUIDModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='central_profile',
        null=True,
        blank=True
    )
    auth_user_id = models.UUIDField(unique=True, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    avatar_url = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=EntityStatus.choices, default=EntityStatus.ACTIVE)

    class Meta:
        ordering = ['full_name']

    def __str__(self):
        return f"{self.full_name} <{self.email}>"


class Permission(TimeStampedUUIDModel):
    module = models.CharField(max_length=100)
    action = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['module', 'action'], name='unique_central_perm_module_action')
        ]
        ordering = ['module', 'action']

    def __str__(self):
        return f"{self.module}:{self.action}"


class Role(TimeStampedUUIDModel):
    name = models.CharField(max_length=100, choices=RoleCode.choices, unique=True)
    display_name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    level = models.IntegerField(default=10)
    permissions = models.ManyToManyField(Permission, through='RolePermission', related_name='roles', blank=True)

    class Meta:
        ordering = ['level', 'name']

    def __str__(self):
        return self.display_name or self.name


class RolePermission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['role', 'permission'], name='unique_central_role_permission')
        ]


# ============================================================================
# EMPLOYEES
# ============================================================================

class Employee(TimeStampedUUIDModel):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='employee')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='employees')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='direct_reports')
    employee_code = models.CharField(max_length=50, unique=True)
    designation = models.CharField(max_length=150)
    joining_date = models.DateField(default=timezone.now)
    employment_type = models.CharField(max_length=30, choices=EmploymentType.choices, default=EmploymentType.FULL_TIME)
    employment_status = models.CharField(max_length=30, choices=EmploymentStatus.choices, default=EmploymentStatus.ACTIVE)
    salary = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    class Meta:
        ordering = ['employee_code']

    def __str__(self):
        return f"{self.employee_code} - {self.profile.full_name} ({self.designation})"


# ============================================================================
# CRM & FRONT OFFICE
# ============================================================================

class Inquiry(TenantScopedModel):
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50)
    source = models.CharField(max_length=50, choices=InquirySource.choices, default=InquirySource.WALK_IN)
    assigned_to = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_inquiries'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inquiries'
    )
    priority = models.CharField(max_length=20, choices=InquiryPriority.choices, default=InquiryPriority.MEDIUM)
    status = models.CharField(max_length=30, choices=InquiryStatus.choices, default=InquiryStatus.NEW)
    notes = models.TextField(blank=True, null=True)
    follow_up_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Inquiries'
        ordering = ['-created_at']

    def __str__(self):
        return f"Inquiry: {self.name} ({self.status})"


class Lead(TenantScopedModel):
    name = models.CharField(max_length=255)
    company = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    source = models.CharField(max_length=100, default='ONLINE')
    assigned_to = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_leads'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leads'
    )
    interested_product = models.CharField(max_length=255, blank=True, null=True)
    estimated_value = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    priority = models.CharField(max_length=20, choices=InquiryPriority.choices, default=InquiryPriority.MEDIUM)
    status = models.CharField(max_length=30, choices=LeadStatus.choices, default=LeadStatus.NEW)
    notes = models.TextField(blank=True, null=True)
    follow_up_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Lead: {self.name} - {self.company or 'Individual'} (${self.estimated_value})"


class Opportunity(TenantScopedModel):
    lead = models.ForeignKey(
        Lead,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='opportunities'
    )
    title = models.CharField(max_length=255)
    value = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    stage = models.CharField(max_length=30, choices=OpportunityStage.choices, default=OpportunityStage.PROPOSAL)
    assigned_to = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_opportunities'
    )
    close_date = models.DateField(null=True, blank=True)
    probability = models.IntegerField(default=50)

    class Meta:
        verbose_name_plural = 'Opportunities'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - ${self.value} ({self.stage})"


# ============================================================================
# RECRUITMENT & ONBOARDING
# ============================================================================

class Candidate(TenantScopedModel):
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    position = models.CharField(max_length=255)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='candidates'
    )
    resume_url = models.URLField(blank=True, null=True)
    source = models.CharField(max_length=100, default='LINKEDIN')
    assigned_recruiter = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recruited_candidates'
    )
    stage = models.CharField(max_length=30, choices=CandidateStage.choices, default=CandidateStage.APPLICATION)
    interview_status = models.CharField(max_length=50, default='SCHEDULED')
    interview_date = models.DateTimeField(null=True, blank=True)
    evaluation = models.JSONField(default=dict, blank=True)
    expected_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    application_date = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} ({self.position} - {self.stage})"


class Onboarding(TenantScopedModel):
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='onboardings'
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='onboardings'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='onboardings'
    )
    manager = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+'
    )
    status = models.CharField(max_length=30, choices=OnboardingStatus.choices, default=OnboardingStatus.IN_PROGRESS)
    current_step = models.CharField(max_length=100, default='DOCUMENTATION')
    progress = models.IntegerField(default=25)
    documentation_status = models.CharField(
        max_length=30,
        choices=DocumentationStatus.choices,
        default=DocumentationStatus.PENDING
    )
    approval_status = models.CharField(
        max_length=30,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.PENDING
    )
    checklist = models.JSONField(default=list, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        target = self.candidate.full_name if self.candidate else (self.employee.profile.full_name if self.employee else 'Unknown')
        return f"Onboarding: {target} ({self.progress}%)"


# ============================================================================
# TASKS & OPERATIONS
# ============================================================================

class Task(TenantScopedModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_tasks'
    )
    assigned_to = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks'
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks'
    )
    priority = models.CharField(max_length=20, choices=TaskPriority.choices, default=TaskPriority.MEDIUM)
    status = models.CharField(max_length=30, choices=TaskStatus.choices, default=TaskStatus.PENDING)
    due_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    related_entity = models.CharField(max_length=100, blank=True, null=True)
    related_entity_id = models.UUIDField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} [{self.priority} - {self.status}]"


class TaskComment(TimeStampedUUIDModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='task_comments')
    comment = models.TextField()

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author} on {self.task.title}"


# ============================================================================
# APPROVALS ENGINE
# ============================================================================

class Approval(TenantScopedModel):
    requester = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='requested_approvals'
    )
    approver = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_approvals'
    )
    request_type = models.CharField(max_length=50, choices=ApprovalType.choices)
    related_entity = models.CharField(max_length=100, blank=True, null=True)
    related_entity_id = models.UUIDField(null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(max_length=30, choices=ApprovalStatus.choices, default=ApprovalStatus.PENDING)
    comment = models.TextField(blank=True, null=True)
    justification = models.TextField(blank=True, null=True)
    decided_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.request_type} approval by {self.requester} ({self.status})"


# ============================================================================
# FINANCE & MARKETING
# ============================================================================

class Expense(TenantScopedModel):
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses'
    )
    requester = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses'
    )
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=30, choices=ExpenseStatus.choices, default=ExpenseStatus.PENDING)
    approval = models.ForeignKey(
        Approval,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses'
    )

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.title}: ${self.amount} ({self.status})"


class Campaign(TenantScopedModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=30, choices=CampaignStatus.choices, default=CampaignStatus.ACTIVE)
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    spent = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    leads_generated = models.IntegerField(default=0)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Campaign: {self.name} (${self.spent}/${self.budget})"


# ============================================================================
# NOTIFICATIONS & AUDIT
# ============================================================================

class Notification(TimeStampedUUIDModel):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=30, choices=NotificationType.choices, default=NotificationType.INFO)
    priority = models.CharField(max_length=20, default='NORMAL')
    related_entity = models.CharField(max_length=100, blank=True, null=True)
    related_entity_id = models.UUIDField(null=True, blank=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.full_name}: {self.title}"


class AuditLog(TenantScopedModel):
    user = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    user_name = models.CharField(max_length=255, blank=True, null=True)
    action = models.CharField(max_length=100)
    module = models.CharField(max_length=100)
    entity_type = models.CharField(max_length=100)
    entity_id = models.UUIDField(null=True, blank=True)
    old_data = models.JSONField(null=True, blank=True)
    new_data = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.module}] {self.action} on {self.entity_type}:{self.entity_id} by {self.user_name or 'System'}"
