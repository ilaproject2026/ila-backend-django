import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

class WorkStudyCategoryChoices(models.TextChoices):
    WORK_IN_INDIA = 'work-in-india', _('Work & Study in India')
    WORK_IN_ABROAD = 'work-in-abroad', _('Work & Study in Abroad')
    GERMAN_PROJECTS = 'german-projects', _('German Onboarding Projects')
    REWARD_STUDY_PLATFORM = 'reward-study-platform', _('Reward & Study Platform')

class PackageStatusChoices(models.TextChoices):
    ACTIVE = 'Active', _('Active')
    DRAFT = 'Draft', _('Draft')
    ARCHIVED = 'Archived', _('Archived')

class CandidateStageChoices(models.TextChoices):
    INTAKE_ASSESSMENT = 'Intake Assessment', _('Intake Assessment')
    AI_SKILL_TRAINING = 'AI & Skill Training', _('AI & Skill Training')
    ACTIVE_PILOT = 'Active Internship / Pilot', _('Active Internship / Pilot')
    GERMAN_SPONSOR_MATCH = 'German Sponsor Match', _('German Sponsor Match')
    GRADUATED_RELOCATED = 'Graduated & Relocated', _('Graduated & Relocated')

class WorkStudyPackage(models.Model):
    """
    Dynamic Work & Study Package Master Model (Office Admin, Software, Trade, Engineering, etc.)
    """
    id = models.CharField(primary_key=True, max_length=64, default=uuid.uuid4, editable=False)
    category = models.CharField(max_length=64, choices=WorkStudyCategoryChoices.choices, default=WorkStudyCategoryChoices.WORK_IN_INDIA)
    category_label = models.CharField(max_length=128, default='Work & Study in India')
    title = models.CharField(max_length=255, help_text="e.g. Office Admin & Accounts, Software Engineer")
    badge = models.CharField(max_length=64, default='Operations', help_text="e.g. Operations, Tech & AI, Global Logistics")
    stipend = models.CharField(max_length=128, default='₹15,000 - ₹25,000 / mo')
    
    # Key Training Parameters
    training_duration = models.CharField(max_length=128, default='6 Months Initial Training Session')
    internship_duration = models.CharField(max_length=128, default='6 Months Corporate Pilot')
    certification = models.CharField(max_length=255, default='1-Year Verified Corporate Certificate')
    
    # Showcase details & Compliance
    action_text = models.CharField(max_length=64, default='Apply Now')
    description = models.TextField(blank=True, default='')
    terms_and_conditions = models.TextField(blank=True, default='', help_text="Detailed modal policy and candidate guidelines")
    
    # Marketing Studio Integration Fields
    status = models.CharField(max_length=32, choices=PackageStatusChoices.choices, default=PackageStatusChoices.ACTIVE)
    promoted_to_marketing = models.BooleanField(default=False)
    marketing_campaign_id = models.CharField(max_length=64, blank=True, null=True)
    last_promoted_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Work & Study Package')
        verbose_name_plural = _('Work & Study Packages')

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title} ({self.stipend})"


class WorkStudyRoleFeature(models.Model):
    """
    Sub-features and roles for each package (e.g. 6 Months Initial Training, Assigned Accounting, Billing, etc.)
    """
    package = models.ForeignKey(WorkStudyPackage, related_name='roles', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    is_milestone = models.BooleanField(default=False, help_text="True for top 3 mandatory training milestone highlights")

    class Meta:
        ordering = ['order']
        verbose_name = _('Package Feature / Role')
        verbose_name_plural = _('Package Features & Roles')

    def __str__(self):
        return f"{self.package.title} - {self.title}"


class WorkStudyStream(models.Model):
    """
    Selectable Streams available in the frontend dropdown right above 'Apply Now'
    """
    package = models.ForeignKey(WorkStudyPackage, related_name='streams', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        verbose_name = _('Selectable Course Stream')
        verbose_name_plural = _('Selectable Course Streams')

    def __str__(self):
        return f"{self.package.title} -> {self.name}"


class WorkStudyCandidate(models.Model):
    """
    HOD Candidate Intake & Progression Model
    """
    id = models.CharField(primary_key=True, max_length=64, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)
    email = models.EmailField()
    phone = models.CharField(max_length=32)
    package = models.ForeignKey(WorkStudyPackage, related_name='candidates', on_delete=models.SET_NULL, null=True, blank=True)
    selected_stream = models.CharField(max_length=128, blank=True, default='')
    
    stage = models.CharField(max_length=64, choices=CandidateStageChoices.choices, default=CandidateStageChoices.INTAKE_ASSESSMENT)
    stipend_status = models.CharField(max_length=32, default='Active')
    current_stipend = models.CharField(max_length=64, default='₹18,000 / mo')
    progress_pct = models.PositiveIntegerField(default=10)
    
    mentor_hod = models.CharField(max_length=128, default='Vikramaditya Roy (Head of IT)')
    attendance_pct = models.PositiveIntegerField(default=95)
    performance_rating = models.FloatField(default=4.8)
    corporate_project = models.CharField(max_length=255, default='ILA Multi-Channel CRM & Automation')
    notes = models.TextField(blank=True, default='')
    
    applied_date = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-applied_date']
        verbose_name = _('Work & Study Candidate')
        verbose_name_plural = _('Work & Study Candidates')

    def __str__(self):
        return f"{self.name} - {self.stage} ({self.selected_stream})"
