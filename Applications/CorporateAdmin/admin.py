from django.contrib import admin
from .models import (
    Organization, Branch, Department, Team, Profile, Role, Permission, RolePermission,
    Employee, Inquiry, Lead, Opportunity, Candidate, Onboarding,
    Task, TaskComment, Approval, Expense, Campaign, Notification, AuditLog
)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'status', 'created_at']
    search_fields = ['name', 'code']
    list_filter = ['status']


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'location', 'organization', 'status']
    search_fields = ['name', 'code', 'location']
    list_filter = ['status', 'organization']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'organization', 'department_head', 'budget', 'status']
    search_fields = ['name', 'code']
    list_filter = ['status', 'organization']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'team_lead', 'status']
    search_fields = ['name']
    list_filter = ['status', 'department']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'phone', 'status', 'created_at']
    search_fields = ['full_name', 'email', 'phone']
    list_filter = ['status']


class RolePermissionInline(admin.TabularInline):
    model = RolePermission
    extra = 1


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'level']
    search_fields = ['name', 'display_name']
    inlines = [RolePermissionInline]


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['module', 'action', 'description']
    search_fields = ['module', 'action']
    list_filter = ['module']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_code', 'profile', 'designation', 'department', 'role', 'employment_status']
    search_fields = ['employee_code', 'profile__full_name', 'profile__email', 'designation']
    list_filter = ['employment_status', 'employment_type', 'department', 'organization']


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'source', 'department', 'status', 'priority', 'created_at']
    search_fields = ['name', 'email', 'phone']
    list_filter = ['status', 'priority', 'source', 'department']


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'estimated_value', 'department', 'status', 'priority', 'created_at']
    search_fields = ['name', 'company', 'email', 'phone']
    list_filter = ['status', 'priority', 'department']


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ['title', 'lead', 'value', 'stage', 'assigned_to', 'close_date']
    search_fields = ['title', 'lead__name', 'lead__company']
    list_filter = ['stage']


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'position', 'department', 'stage', 'interview_status', 'application_date']
    search_fields = ['full_name', 'email', 'phone', 'position']
    list_filter = ['stage', 'department']


@admin.register(Onboarding)
class OnboardingAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'department', 'progress', 'status', 'current_step', 'created_at']
    search_fields = ['candidate__full_name']
    list_filter = ['status', 'department']


class TaskCommentInline(admin.TabularInline):
    model = TaskComment
    extra = 1


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'department', 'assigned_to', 'priority', 'status', 'due_date']
    search_fields = ['title', 'description']
    list_filter = ['status', 'priority', 'department']
    inlines = [TaskCommentInline]


@admin.register(Approval)
class ApprovalAdmin(admin.ModelAdmin):
    list_display = ['request_type', 'requester', 'approver', 'amount', 'status', 'created_at']
    search_fields = ['requester__profile__full_name', 'approver__profile__full_name']
    list_filter = ['status', 'request_type']


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'amount', 'department', 'status', 'date']
    search_fields = ['title', 'category']
    list_filter = ['status', 'category', 'department']


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'budget', 'spent', 'leads_generated', 'start_date']
    search_fields = ['name', 'description']
    list_filter = ['status']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'user__full_name']
    list_filter = ['type', 'is_read']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'module', 'entity_type', 'entity_id', 'user_name', 'created_at']
    search_fields = ['action', 'module', 'entity_type', 'user_name']
    list_filter = ['module', 'action']
