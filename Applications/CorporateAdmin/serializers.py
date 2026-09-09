from rest_framework import serializers
from django.db import models
from .models import (
    Organization, Branch, Department, Team, Profile, Role, Permission, RolePermission,
    Employee, Inquiry, Lead, Opportunity, Candidate, Onboarding,
    Task, TaskComment, Approval, Expense, Campaign, Notification, AuditLog
)


# ============================================================================
# FLEXIBLE RELATION FIELDS (MOCK ID & RESILIENT RESOLUTION)
# ============================================================================

class FlexibleDepartmentField(serializers.PrimaryKeyRelatedField):
    """
    Resolves real UUIDs, mock UUIDs ('d0000000-0000-0000-0000-000000000003'),
    department codes ('DEP-FIN'), or names to a valid Department instance.
    """
    def to_internal_value(self, data):
        if not data:
            return None
        if isinstance(data, Department):
            return data

        data_str = str(data).strip()
        # 1. Direct PK lookup
        try:
            return self.get_queryset().get(pk=data_str)
        except Exception:
            pass

        # 2. Mock UUID mapping from frontend seeds
        mock_map = {
            'd0000000-0000-0000-0000-000000000001': 'DEP-EXEC',
            'd0000000-0000-0000-0000-000000000002': 'DEP-HR',
            'd0000000-0000-0000-0000-000000000003': 'DEP-FIN',
            'd0000000-0000-0000-0000-000000000004': 'DEP-SALES',
            'd0000000-0000-0000-0000-000000000005': 'DEP-OPS',
            'd0000000-0000-0000-0000-000000000006': 'DEP-ENG',
        }
        target_code = mock_map.get(data_str.lower())
        if target_code:
            dept = self.get_queryset().filter(code=target_code).first()
            if dept:
                return dept

        # 3. Lookup by code or name
        dept = self.get_queryset().filter(models.Q(code__iexact=data_str) | models.Q(name__icontains=data_str)).first()
        if dept:
            return dept

        # 4. Fallback to first department
        fallback = self.get_queryset().first()
        if fallback:
            return fallback

        raise serializers.ValidationError(f"Invalid department: '{data}'.")


class FlexibleEmployeeField(serializers.PrimaryKeyRelatedField):
    """
    Resolves real UUIDs, mock UUIDs ('e0000000-0000-0000-0000-000000000001'),
    employee codes ('EMP-001'), emails, or names to a valid Employee instance.
    """
    def to_internal_value(self, data):
        if not data:
            return None
        if isinstance(data, Employee):
            return data

        data_str = str(data).strip()
        # 1. Direct PK lookup
        try:
            return self.get_queryset().get(pk=data_str)
        except Exception:
            pass

        # 2. Mock UUID mapping from frontend seeds
        mock_map = {
            'e0000000-0000-0000-0000-000000000001': 'EMP-001',
            'e0000000-0000-0000-0000-000000000002': 'EMP-002',
            'e0000000-0000-0000-0000-000000000003': 'EMP-003',
            'e0000000-0000-0000-0000-000000000004': 'EMP-004',
            'e0000000-0000-0000-0000-000000000005': 'EMP-005',
            'e0000000-0000-0000-0000-000000000006': 'EMP-006',
        }
        target_code = mock_map.get(data_str.lower())
        if target_code:
            emp = self.get_queryset().filter(employee_code=target_code).first()
            if emp:
                return emp

        # 3. Lookup by code, email, or name
        emp = self.get_queryset().filter(
            models.Q(employee_code__iexact=data_str) |
            models.Q(profile__email__iexact=data_str) |
            models.Q(profile__full_name__icontains=data_str)
        ).first()
        if emp:
            return emp

        # 4. Fallback to first employee
        fallback = self.get_queryset().first()
        if fallback:
            return fallback

        raise serializers.ValidationError(f"Invalid employee: '{data}'.")


def get_default_organization():
    org = Organization.objects.first()
    if not org:
        org = Organization.objects.create(
            name="Global Enterprise Group (GEG)",
            code="GEG-CORP",
            status='ACTIVE'
        )
    return org


class FlexibleOrganizationField(serializers.PrimaryKeyRelatedField):
    """
    Resolves real UUIDs, mock UUIDs ('o0000000-0000-0000-0000-000000000001'),
    organization codes ('GEG-CORP'), or falls back to the default active organization.
    """
    def __init__(self, **kwargs):
        kwargs.setdefault('queryset', Organization.objects.all())
        kwargs.setdefault('required', False)
        kwargs.setdefault('default', get_default_organization)
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        if not data:
            return get_default_organization()
        if isinstance(data, Organization):
            return data

        data_str = str(data).strip()
        try:
            return self.get_queryset().get(pk=data_str)
        except Exception:
            pass

        org = self.get_queryset().filter(models.Q(code__iexact=data_str) | models.Q(name__icontains=data_str)).first()
        if org:
            return org

        return get_default_organization()


# ============================================================================
# ORGANIZATION & STRUCTURE SERIALIZERS
# ============================================================================

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'


class BranchSerializer(serializers.ModelSerializer):
    organization = FlexibleOrganizationField()
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model = Branch
        fields = '__all__'
        extra_kwargs = {'organization': {'required': False}, 'code': {'required': False}}

    def to_internal_value(self, data):
        data = data.copy() if hasattr(data, 'copy') else dict(data)
        if not data.get('code') and data.get('name'):
            words = str(data['name']).strip().split()
            code = (''.join([w[0].upper() for w in words[:4]]) if len(words) > 1 else data['name'][:4].upper())
            data['code'] = code or 'BRN'
        elif data.get('code'):
            data['code'] = str(data['code']).strip().upper()
        return super().to_internal_value(data)




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
    organization = FlexibleOrganizationField()
    department_head = FlexibleEmployeeField(queryset=Employee.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Department
        fields = ['organization', 'name', 'code', 'description', 'department_head', 'budget', 'status']
        extra_kwargs = {
            'organization': {'required': False},
            'department_head': {'required': False},
            'code': {'required': False},
            'budget': {'required': False},
            'status': {'required': False},
            'description': {'required': False, 'allow_blank': True},
        }

    def to_internal_value(self, data):
        data = data.copy() if hasattr(data, 'copy') else dict(data)
        if not data.get('code') and data.get('name'):
            words = str(data['name']).strip().split()
            code = (''.join([w[0].upper() for w in words[:4]]) if len(words) > 1 else data['name'][:4].upper())
            data['code'] = code or 'DEPT'
        elif data.get('code'):
            data['code'] = str(data['code']).strip().upper()
        return super().to_internal_value(data)



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
    team_lead = FlexibleEmployeeField(queryset=Employee.objects.all(), required=False, allow_null=True)
    department = FlexibleDepartmentField(queryset=Department.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Team
        fields = ['department', 'name', 'description', 'team_lead', 'status']
        extra_kwargs = {
            'team_lead': {'required': False},
            'department': {'required': False},
        }


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
    organization = FlexibleOrganizationField()
    department = FlexibleDepartmentField(queryset=Department.objects.all(), required=False, allow_null=True)
    manager = FlexibleEmployeeField(queryset=Employee.objects.all(), required=False, allow_null=True)
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
            'profile': {'required': False},
            'organization': {'required': False},
            'department': {'required': False},
            'manager': {'required': False},
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
    organization = FlexibleOrganizationField()
    department = FlexibleDepartmentField(queryset=Department.objects.all(), required=False, allow_null=True)
    assigned_to = FlexibleEmployeeField(queryset=Employee.objects.all(), required=False, allow_null=True)

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
    organization = FlexibleOrganizationField()
    department = FlexibleDepartmentField(queryset=Department.objects.all(), required=False, allow_null=True)
    assigned_to = FlexibleEmployeeField(queryset=Employee.objects.all(), required=False, allow_null=True)

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
    organization = FlexibleOrganizationField()

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
    organization = FlexibleOrganizationField()
    department = FlexibleDepartmentField(queryset=Department.objects.all(), required=False, allow_null=True)
    assigned_recruiter = FlexibleEmployeeField(queryset=Employee.objects.all(), required=False, allow_null=True)

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
    organization = FlexibleOrganizationField()

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
    organization = FlexibleOrganizationField()
    department = FlexibleDepartmentField(queryset=Department.objects.all(), required=False, allow_null=True)
    assigned_to = FlexibleEmployeeField(queryset=Employee.objects.all(), required=False, allow_null=True)
    created_by = FlexibleEmployeeField(queryset=Employee.objects.all(), required=False, allow_null=True)

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
    organization = FlexibleOrganizationField()
    requester = FlexibleEmployeeField(queryset=Employee.objects.all(), required=False, allow_null=True)
    approver = FlexibleEmployeeField(queryset=Employee.objects.all(), required=False, allow_null=True)

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
    organization = FlexibleOrganizationField()
    department = FlexibleDepartmentField(queryset=Department.objects.all(), required=False, allow_null=True)
    requester = FlexibleEmployeeField(queryset=Employee.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Expense
        fields = '__all__'
        extra_kwargs = {
            'organization': {'required': False},
            'department': {'required': False},
            'requester': {'required': False},
        }


class CampaignSerializer(serializers.ModelSerializer):
    organization = FlexibleOrganizationField()

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
    organization = FlexibleOrganizationField()

    class Meta:
        model = AuditLog
        fields = '__all__'
        extra_kwargs = {'organization': {'required': False}}
