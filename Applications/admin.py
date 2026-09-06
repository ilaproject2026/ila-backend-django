from django.contrib import admin
from Applications.Authentication.auth_admin import *
from Applications.Authentication.auth_models import FranchisePartner, AuditLog
from Applications.FrontOffice.frontoffice_models import Inquiry, FollowUpRecord, VisitorLog
from Applications.Academics.academics_models import (
    GlobalCategory,
    GlobalSubCategory,
    TeachingStrategy,
    StudentAnalyzingStrategy,
    GlobalCourse,
    GlobalPath,
    GlobalBatch,
    ClassScheduleSession,
    CourseMaterial,
    StudentEnrollment,
)
from Applications.HRMS.hrms_models import (
    StaffProfile,
    AttendanceLog,
    HRCandidate,
    EnterpriseTask,
    ApprovalRequest,
)
from Applications.Finance.finance_models import (
    FinancialLedger,
    SalesRecord,
    FundPool,
    CommissionItem,
)
from Applications.Rewards.rewards_models import ReferralRecord, TierRule


# --- Authentication Extras ---
@admin.register(FranchisePartner)
class FranchisePartnerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'region', 'partner_token', 'created_at')
    search_fields = ('name', 'email', 'region', 'partner_token')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'department', 'category', 'action', 'timestamp')
    list_filter = ('category', 'department')
    search_fields = ('action', 'details', 'ip_address')


# --- FrontOffice ---
@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('token_number', 'name', 'lead_type', 'category', 'crm_status', 'pipeline_stage', 'payment_status', 'total_amount', 'amount_paid', 'created_at')
    list_filter = ('lead_type', 'category', 'crm_status', 'pipeline_stage', 'payment_status', 'follow_up_status')
    search_fields = ('token_number', 'name', 'email', 'phone')


@admin.register(FollowUpRecord)
class FollowUpRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'inquiry', 'staff', 'channel', 'outcome', 'date', 'next_follow_up_date')
    list_filter = ('channel', 'outcome')
    search_fields = ('notes', 'inquiry__token_number')


@admin.register(VisitorLog)
class VisitorLogAdmin(admin.ModelAdmin):
    list_display = ('page', 'time_spent_seconds', 'ip_address', 'timestamp')


# --- Academics ---
@admin.register(GlobalCategory)
class GlobalCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code')
    search_fields = ('name', 'code')


@admin.register(GlobalSubCategory)
class GlobalSubCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'category')
    list_filter = ('category',)


@admin.register(TeachingStrategy)
class TeachingStrategyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'default_active')
    list_filter = ('category', 'default_active')


@admin.register(StudentAnalyzingStrategy)
class StudentAnalyzingStrategyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'target_metric', 'active')
    list_filter = ('active',)


@admin.register(GlobalCourse)
class GlobalCourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'library_type', 'fee', 'enrolled_count', 'display_position')
    list_filter = ('category', 'library_type', 'view_type')
    search_fields = ('name', 'subtitle')


@admin.register(GlobalPath)
class GlobalPathAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'course', 'position')
    list_filter = ('course',)


@admin.register(GlobalBatch)
class GlobalBatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'course', 'path')
    list_filter = ('course',)


@admin.register(ClassScheduleSession)
class ClassScheduleSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'time_slot', 'course', 'batch', 'instructor', 'status')
    list_filter = ('date', 'status', 'course')


@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'course', 'material_type', 'created_at')
    list_filter = ('material_type', 'course')


@admin.register(StudentEnrollment)
class StudentEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'course', 'batch', 'status', 'attendance_score', 'joined_at')
    list_filter = ('status', 'course')


# --- HRMS ---
@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'user', 'department', 'status', 'monthly_salary', 'joining_date')
    list_filter = ('department', 'status')
    search_fields = ('employee_id', 'user__username', 'user__fullname')


@admin.register(AttendanceLog)
class AttendanceLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'staff', 'date', 'check_in_time', 'check_out_time', 'status')
    list_filter = ('date', 'status')


@admin.register(HRCandidate)
class HRCandidateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'position', 'department', 'stage', 'status', 'created_at')
    list_filter = ('stage', 'status', 'department')
    search_fields = ('name', 'email', 'phone', 'position')


@admin.register(EnterpriseTask)
class EnterpriseTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'assigned_to_dept', 'assigned_staff', 'priority', 'status', 'created_at')
    list_filter = ('priority', 'status', 'assigned_to_dept')
    search_fields = ('title', 'description')


@admin.register(ApprovalRequest)
class ApprovalRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'request_type', 'department', 'requested_by', 'status', 'date')
    list_filter = ('request_type', 'status', 'department')


# --- Finance ---
@admin.register(FinancialLedger)
class FinancialLedgerAdmin(admin.ModelAdmin):
    list_display = ('id', 'transaction_type', 'category', 'amount', 'date', 'reference_id')
    list_filter = ('transaction_type', 'category', 'date')
    search_fields = ('description', 'reference_id')


@admin.register(SalesRecord)
class SalesRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'client_name', 'program_name', 'total_amount', 'paid_amount', 'status', 'flag')
    list_filter = ('status', 'flag')
    search_fields = ('client_name', 'program_name')


@admin.register(FundPool)
class FundPoolAdmin(admin.ModelAdmin):
    list_display = ('id', 'fund_name', 'category', 'allocated_amount', 'utilized_amount')
    list_filter = ('category',)


@admin.register(CommissionItem)
class CommissionItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'consultant_name', 'referral_code', 'lead_name', 'amount', 'status', 'date')
    list_filter = ('status', 'date')
    search_fields = ('consultant_name', 'referral_code', 'lead_name')


# --- Rewards ---
@admin.register(ReferralRecord)
class ReferralRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'referrer_name', 'candidate_name', 'vertical', 'commission_amount', 'status', 'date')
    list_filter = ('vertical', 'status', 'referrer_role')
    search_fields = ('referrer_name', 'candidate_name', 'referrer_email')


@admin.register(TierRule)
class TierRuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'tier_name', 'min_referrals', 'bonus_multiplier', 'base_reward', 'color')
