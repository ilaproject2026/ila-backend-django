from rest_framework import serializers
from .models import (
    Organization, Branch, Department, Team, Profile, Role, Permission, RolePermission,
    Employee, Inquiry, Lead, Opportunity, Candidate, Onboarding,
    Task, TaskComment, Approval, Expense, Campaign, Notification, AuditLog
)


# ============================================================================
# ORGANIZATION & STRUCTURE SERIALIZERS
# ============================================================================

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'


class BranchSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model = Branch
        fields = '__all__'


# ============================================================================
# IAM & PROFILE SERIALIZERS
# ============================================================================

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'module', 'action', 'description', 'created_at']


class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source='permissions'
    )

    class Meta:
        model = Role
        fields = ['id', 'name', 'display_name', 'description', 'level', 'permissions', 'permission_ids', 'created_at']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'user', 'auth_user_id', 'full_name', 'email', 'phone', 'avatar_url', 'status', 'created_at', 'updated_at']


# ============================================================================
# EMPLOYEE COMPACT & DETAIL SERIALIZERS
# ============================================================================

class EmployeeCompactSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='profile.full_name', read_only=True)
    email = serializers.CharField(source='profile.email', read_only=True)
    avatar_url = serializers.CharField(source='profile.avatar_url', read_only=True)
    role_name = serializers.CharField(source='role.display_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'employee_code', 'full_name', 'email', 'avatar_url',
            'designation', 'role_name', 'department_name'
        ]


class DepartmentReadSerializer(serializers.ModelSerializer):
    department_head = EmployeeCompactSerializer(read_only=True)
    employee_count = serializers.SerializerMethodField()
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model = Department
        fields = [
            'id', 'organization', 'organization_name', 'name', 'code', 'description',
            'department_head', 'budget', 'status', 'employee_count', 'created_at', 'updated_at'
        ]

    def get_employee_count(self, obj):
        if hasattr(obj, 'employee_count'):
            return obj.employee_count
        return obj.employees.count()


class DepartmentWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['organization', 'name', 'code', 'description', 'department_head', 'budget', 'status']


class TeamReadSerializer(serializers.ModelSerializer):
    team_lead = EmployeeCompactSerializer(read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    members_count = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = [
            'id', 'department', 'department_name', 'name', 'description',
            'team_lead', 'status', 'members_count', 'created_at', 'updated_at'
        ]

    def get_members_count(self, obj):
        return obj.members.count()


class TeamWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['department', 'name', 'description', 'team_lead', 'status']


class EmployeeReadSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    department = DepartmentReadSerializer(read_only=True)
    team = TeamReadSerializer(read_only=True)
    role = RoleSerializer(read_only=True)
    manager = EmployeeCompactSerializer(read_only=True)
    full_name = serializers.CharField(source='profile.full_name', read_only=True)
    email = serializers.CharField(source='profile.email', read_only=True)
    avatar_url = serializers.CharField(source='profile.avatar_url', read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'profile', 'full_name', 'email', 'avatar_url', 'organization',
            'organization_name', 'department', 'team', 'role', 'manager',
            'employee_code', 'designation', 'joining_date', 'employment_type',
            'employment_status', 'salary', 'created_at', 'updated_at'
        ]


class EmployeeWriteSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(write_only=True, required=False)
    email = serializers.EmailField(write_only=True, required=False)
    phone = serializers.CharField(write_only=True, required=False, allow_blank=True)
    avatar_url = serializers.URLField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'organization', 'profile', 'full_name', 'email', 'phone', 'avatar_url',
            'department', 'team', 'role', 'manager', 'employee_code',
            'designation', 'joining_date', 'employment_type', 'employment_status', 'salary'
        ]
        extra_kwargs = {
            'profile': {'required': False}
        }

    def create(self, validated_data):
        full_name = validated_data.pop('full_name', None)
        email = validated_data.pop('email', None)
        phone = validated_data.pop('phone', '')
        avatar_url = validated_data.pop('avatar_url', None)
        profile = validated_data.get('profile', None)

        if not profile and email:
            profile, _ = Profile.objects.get_or_create(
                email=email,
                defaults={'full_name': full_name or email.split('@')[0], 'phone': phone, 'avatar_url': avatar_url}
            )
            validated_data['profile'] = profile

        return super().create(validated_data)


# ============================================================================
# CRM & FRONT OFFICE SERIALIZERS
# ============================================================================

class InquiryReadSerializer(serializers.ModelSerializer):
    assigned_to_detail = EmployeeCompactSerializer(source='assigned_to', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Inquiry
        fields = '__all__'


class InquiryWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        fields = '__all__'
        extra_kwargs = {'organization': {'required': False}}


class LeadReadSerializer(serializers.ModelSerializer):
    assigned_to_detail = EmployeeCompactSerializer(source='assigned_to', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Lead
        fields = '__all__'


class LeadWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = '__all__'
        extra_kwargs = {'organization': {'required': False}}


class OpportunityReadSerializer(serializers.ModelSerializer):
    lead_name = serializers.CharField(source='lead.name', read_only=True)
    lead_company = serializers.CharField(source='lead.company', read_only=True)
    assigned_to_detail = EmployeeCompactSerializer(source='assigned_to', read_only=True)

    class Meta:
        model = Opportunity
        fields = '__all__'


class OpportunityWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity
        fields = '__all__'
        extra_kwargs = {'organization': {'required': False}}


# ============================================================================
# RECRUITMENT & ONBOARDING SERIALIZERS
# ============================================================================

class CandidateReadSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    recruiter_detail = EmployeeCompactSerializer(source='assigned_recruiter', read_only=True)

    class Meta:
        model = Candidate
        fields = '__all__'


class CandidateWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = '__all__'
        extra_kwargs = {'organization': {'required': False}}


class OnboardingReadSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='candidate.full_name', read_only=True)
    employee_name = serializers.CharField(source='employee.profile.full_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    manager_detail = EmployeeCompactSerializer(source='manager', read_only=True)

    class Meta:
        model = Onboarding
        fields = '__all__'


class OnboardingWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Onboarding
        fields = '__all__'
        extra_kwargs = {'organization': {'required': False}}


# ============================================================================
# TASKS & COMMENTS SERIALIZERS
# ============================================================================

class TaskCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.profile.full_name', read_only=True)
    author_avatar = serializers.CharField(source='author.profile.avatar_url', read_only=True)

    class Meta:
        model = TaskComment
        fields = ['id', 'task', 'author', 'author_name', 'author_avatar', 'comment', 'created_at']
        extra_kwargs = {'task': {'required': False}, 'author': {'required': False}}


class TaskReadSerializer(serializers.ModelSerializer):
    created_by_detail = EmployeeCompactSerializer(source='created_by', read_only=True)
    assigned_to_detail = EmployeeCompactSerializer(source='assigned_to', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    comments = TaskCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = '__all__'


class TaskWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        extra_kwargs = {'organization': {'required': False}}


# ============================================================================
# APPROVALS SERIALIZERS
# ============================================================================

class ApprovalReadSerializer(serializers.ModelSerializer):
    requester_detail = EmployeeCompactSerializer(source='requester', read_only=True)
    approver_detail = EmployeeCompactSerializer(source='approver', read_only=True)

    class Meta:
        model = Approval
        fields = '__all__'


class ApprovalWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Approval
        fields = '__all__'
        extra_kwargs = {'organization': {'required': False}}


# ============================================================================
# FINANCE & MARKETING SERIALIZERS
# ============================================================================

class ExpenseReadSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    requester_detail = EmployeeCompactSerializer(source='requester', read_only=True)
    approval_detail = ApprovalReadSerializer(source='approval', read_only=True)

    class Meta:
        model = Expense
        fields = '__all__'


class ExpenseWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'
        extra_kwargs = {'organization': {'required': False}}


class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = '__all__'
        extra_kwargs = {'organization': {'required': False}}


# ============================================================================
# NOTIFICATIONS & AUDIT SERIALIZERS
# ============================================================================

class NotificationSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = Notification
        fields = '__all__'


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = '__all__'
        extra_kwargs = {'organization': {'required': False}}
