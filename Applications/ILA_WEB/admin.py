from django.contrib import admin
from .models import (
    FranchisePartner,
    Inquiry,
    FollowUpRecord,
    PartnerInstitution,
    TieUpOutreachLog,
    MarketingCampaign,
    FieldVisitLog,
    DepartmentMeeting,
    RewardProfile,
    RewardTransaction,
    WorkStudyApplication,
    VisaRequirementRule,
    SettlementServiceRequest,
    EnterpriseTask,
    AttendanceLog,
    ApprovalRequest,
    ConsultantSession,
    ConsultantChatMessage,
)

from .IlaConsultant.admin import AITokenUsageLogAdmin  # noqa: F401

@admin.register(FranchisePartner)
class FranchisePartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'region', 'franchise_token', 'is_active', 'created_at')
    list_filter = ('region', 'is_active')
    search_fields = ('name', 'email', 'franchise_token')


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'category', 'department', 'target_keyword', 'target_country', 'payment_status', 'crm_status', 'pipeline_stage', 'created_at')
    list_filter = ('category', 'department', 'type', 'payment_status', 'crm_status', 'pipeline_stage', 'target_country')
    search_fields = ('name', 'email', 'phone', 'course', 'target_keyword', 'token_number')


@admin.register(FollowUpRecord)
class FollowUpRecordAdmin(admin.ModelAdmin):
    list_display = ('inquiry', 'staff_name', 'channel', 'outcome', 'date', 'created_at')
    list_filter = ('channel', 'outcome')
    search_fields = ('staff_name', 'notes', 'inquiry__name')


@admin.register(PartnerInstitution)
class PartnerInstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'country', 'city', 'contact_person', 'email', 'status', 'last_updated')
    list_filter = ('category', 'country', 'status')
    search_fields = ('name', 'city', 'contact_person', 'email')


@admin.register(TieUpOutreachLog)
class TieUpOutreachLogAdmin(admin.ModelAdmin):
    list_display = ('partner', 'subject', 'dispatched_by', 'is_dispatched', 'dispatched_at')
    list_filter = ('is_dispatched',)
    search_fields = ('subject', 'partner__name', 'response_notes')


@admin.register(MarketingCampaign)
class MarketingCampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'channel', 'budget', 'spent', 'target_geography', 'status', 'leads_count', 'conversions_count', 'created_at')
    list_filter = ('channel', 'status', 'target_geography')
    search_fields = ('name',)


@admin.register(FieldVisitLog)
class FieldVisitLogAdmin(admin.ModelAdmin):
    list_display = ('institution_visited', 'contact_person', 'location', 'visit_date', 'logged_by')
    search_fields = ('institution_visited', 'contact_person', 'summary')


@admin.register(DepartmentMeeting)
class DepartmentMeetingAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'date', 'time', 'status')
    list_filter = ('department', 'status')
    search_fields = ('title', 'attendees', 'agenda')


@admin.register(RewardProfile)
class RewardProfileAdmin(admin.ModelAdmin):
    list_display = ('consultant_id', 'user', 'tier', 'active_points', 'lifetime_points', 'monthly_points', 'cash_earned', 'work_certificate_issued')
    list_filter = ('tier', 'work_certificate_issued')
    search_fields = ('consultant_id', 'user__username', 'user__email')


@admin.register(RewardTransaction)
class RewardTransactionAdmin(admin.ModelAdmin):
    list_display = ('profile', 'points', 'milestone_type', 'timestamp')
    list_filter = ('milestone_type',)
    search_fields = ('description', 'reference_inquiry_id')


@admin.register(WorkStudyApplication)
class WorkStudyApplicationAdmin(admin.ModelAdmin):
    list_display = ('candidate_name', 'email', 'track', 'sub_domain', 'ai_interview_score', 'ai_interview_status', 'is_onboarded_to_dept', 'created_at')
    list_filter = ('track', 'ai_interview_status', 'is_onboarded_to_dept')
    search_fields = ('candidate_name', 'email', 'phone', 'sub_domain')


@admin.register(VisaRequirementRule)
class VisaRequirementRuleAdmin(admin.ModelAdmin):
    list_display = ('country', 'visa_type', 'blocked_funds_amount', 'embassy_queue_days', 'primary_authority', 'last_monitored_update')
    list_filter = ('country', 'visa_type')
    search_fields = ('country', 'visa_type', 'primary_authority')


@admin.register(SettlementServiceRequest)
class SettlementServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('candidate_name', 'email', 'target_country', 'arrival_date', 'status', 'assigned_coordinator')
    list_filter = ('target_country', 'status')
    search_fields = ('candidate_name', 'email')


@admin.register(EnterpriseTask)
class EnterpriseTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'assigned_to_dept', 'status', 'priority', 'created_at', 'updated_at')
    list_filter = ('assigned_to_dept', 'status', 'priority')
    search_fields = ('title', 'description')


@admin.register(AttendanceLog)
class AttendanceLogAdmin(admin.ModelAdmin):
    list_display = ('staff_id', 'staff_name', 'check_in_time', 'status', 'date')
    list_filter = ('status', 'date')
    search_fields = ('staff_id', 'staff_name')


@admin.register(ApprovalRequest)
class ApprovalRequestAdmin(admin.ModelAdmin):
    list_display = ('type', 'requested_by', 'department', 'status', 'date')
    list_filter = ('department', 'status', 'type')
    search_fields = ('requested_by', 'description')


class ConsultantChatMessageInline(admin.TabularInline):
    model = ConsultantChatMessage
    extra = 0
    readonly_fields = ('role', 'content', 'suggested_actions', 'prompt_tokens', 'completion_tokens', 'total_tokens', 'timestamp')
    can_delete = False


@admin.register(ConsultantSession)
class ConsultantSessionAdmin(admin.ModelAdmin):
    list_display = ('session_key', 'user_email', 'user_name', 'current_topic', 'status', 'total_messages', 'total_tokens_used', 'last_activity', 'created_at')
    list_filter = ('status', 'current_topic', 'created_at')
    search_fields = ('session_key', 'user_email', 'user_name', 'user_phone')
    readonly_fields = ('id', 'created_at', 'last_activity', 'total_messages', 'total_tokens_used')
    inlines = [ConsultantChatMessageInline]


@admin.register(ConsultantChatMessage)
class ConsultantChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'role', 'short_content', 'total_tokens', 'timestamp')
    list_filter = ('role', 'timestamp')
    search_fields = ('content', 'session__session_key')
    readonly_fields = ('id', 'timestamp')

    def short_content(self, obj):
        return obj.content[:60] + ('...' if len(obj.content) > 60 else '')
    short_content.short_description = 'Content'

