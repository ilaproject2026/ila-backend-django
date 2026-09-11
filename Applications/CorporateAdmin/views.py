import uuid
from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken

from .models import (
    Organization, Branch, Department, Team, Profile, Role, Permission,
    Employee, Inquiry, Lead, Opportunity, Candidate, Onboarding,
    Task, TaskComment, Approval, Expense, Campaign, Notification, AuditLog,
    EntityStatus, BranchStatus, RoleCode, InquiryStatus, LeadStatus,
    CandidateStage, OnboardingStatus, ApprovalStatus, TaskStatus,
    ExpenseStatus, NotificationType, OpportunityStage, DocumentationStatus
)
from .serializers import (
    OrganizationSerializer, BranchSerializer, DepartmentReadSerializer,
    DepartmentWriteSerializer, TeamReadSerializer, TeamWriteSerializer,
    ProfileSerializer, RoleSerializer, PermissionSerializer,
    EmployeeReadSerializer, EmployeeWriteSerializer, EmployeeCompactSerializer,
    InquiryReadSerializer, InquiryWriteSerializer,
    LeadReadSerializer, LeadWriteSerializer,
    OpportunityReadSerializer, OpportunityWriteSerializer,
    CandidateReadSerializer, CandidateWriteSerializer,
    OnboardingReadSerializer, OnboardingWriteSerializer,
    TaskReadSerializer, TaskWriteSerializer, TaskCommentSerializer,
    ApprovalReadSerializer, ApprovalWriteSerializer,
    ExpenseReadSerializer, ExpenseWriteSerializer, CampaignSerializer,
    NotificationSerializer, AuditLogSerializer
)


# ============================================================================
# MULTI-TENANCY SCOPING HELPER
# ============================================================================

def get_current_organization(request):
    """Resolve the active organization from authenticated user or fallback to primary."""
    if request.user.is_authenticated:
        profile = getattr(request.user, 'central_profile', None)
        if profile and hasattr(profile, 'employee') and profile.employee.organization:
            return profile.employee.organization
    org = Organization.objects.first()
    if not org:
        org = Organization.objects.create(
            name="GEG Global Command Center",
            code="GEG-HQ",
            description="Default Central Enterprise Command Center Organization",
            status=EntityStatus.ACTIVE
        )
    return org


class TenantScopedViewSetMixin:
    """Multi-tenant isolation queryset filter with seamless fallback."""
    def get_queryset(self):
        qs = super().get_queryset()
        org = get_current_organization(self.request)
        if hasattr(qs.model, 'organization'):
            return qs.filter(organization=org)
        return qs

    def perform_create(self, serializer):
        org = get_current_organization(self.request)
        if hasattr(serializer.Meta.model, 'organization'):
            serializer.save(organization=org)
        else:
            serializer.save()


# ============================================================================
# AUTHENTICATION & CURRENT USER VIEWS
# ============================================================================

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip()
        password = request.data.get('password', '').strip()

        if not email or not password:
            return Response(
                {"error": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Authenticate via Django Auth
        user = authenticate(request, username=email, password=password)
        if not user:
            # Fallback to direct email match if username differs
            from django.contrib.auth import get_user_model
            UserModel = get_user_model()
            try:
                candidate_user = UserModel.objects.get(email__iexact=email)
                if candidate_user.check_password(password):
                    user = candidate_user
            except (UserModel.DoesNotExist, UserModel.MultipleObjectsReturned):
                user = None

        if not user:
            return Response(
                {"error": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)
        profile, _ = Profile.objects.get_or_create(
            user=user,
            defaults={'email': user.email, 'full_name': getattr(user, 'get_full_name', lambda: '')() or user.username}
        )

        employee = getattr(profile, 'employee', None)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": str(user.id),
                "email": user.email,
                "profile": ProfileSerializer(profile).data,
                "employee": EmployeeCompactSerializer(employee).data if employee else None,
                "role": employee.role.name if employee and employee.role else "STAFF",
            }
        })


class CurrentUserView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        user = request.user
        profile = None
        employee = None

        if user.is_authenticated:
            profile = getattr(user, 'central_profile', None) or getattr(user, 'profile', None)
            if not profile:
                profile, _ = Profile.objects.get_or_create(
                    user=user,
                    defaults={'email': user.email, 'full_name': getattr(user, 'get_full_name', lambda: '')() or user.username}
                )
            employee = getattr(profile, 'employee', None)
        else:
            employee = Employee.objects.select_related('profile', 'role', 'department', 'organization').first()
            if employee:
                profile = employee.profile

        role_name = employee.role.name if employee and employee.role else ('SUPER_ADMIN' if not user.is_authenticated else 'EMPLOYEE')
        role_display = employee.role.display_name if employee and employee.role else ('Super Administrator' if not user.is_authenticated else 'Employee')
        dept_name = employee.department.name if employee and employee.department else None
        emp_code = employee.employee_code if employee else None

        return Response({
            'authenticated': bool(user.is_authenticated),
            'id': str(profile.id) if profile else (str(user.id) if user.is_authenticated else None),
            'email': profile.email if profile else (user.email if user.is_authenticated else 'admin@geg-enterprise.com'),
            'full_name': profile.full_name if profile else (user.get_full_name() if user.is_authenticated else 'Command Center Admin'),
            'avatar_url': profile.avatar_url if profile else None,
            'role': role_name,
            'role_display': role_display,
            'department_name': dept_name,
            'employee_code': emp_code,
            'profile': ProfileSerializer(profile).data if profile else None,
            'employee': EmployeeReadSerializer(employee).data if employee else None,
            'permissions': [f"{p.module}:{p.action}" for p in (employee.role.permissions.all() if employee and employee.role else [])],
        })


class SwitchRoleView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        role_code = request.data.get('role')
        if not role_code:
            return Response({"error": "Role code is required."}, status=status.HTTP_400_BAD_REQUEST)
        role = Role.objects.filter(name=role_code).first()
        if not role:
            return Response({"error": f"Role '{role_code}' not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "message": f"Acting role switched to {role.display_name or role.name}",
            "role": RoleSerializer(role).data
        })


# ============================================================================
# ORGANIZATION VIEWSETS
# ============================================================================

class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['get'])
    def current(self, request):
        org = get_current_organization(request)
        return Response(OrganizationSerializer(org).data)


class BranchViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):
    queryset = Branch.objects.select_related('organization').all()
    serializer_class = BranchSerializer
    permission_classes = [permissions.AllowAny]


class DepartmentViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):
    queryset = Department.objects.select_related('organization', 'department_head__profile').annotate(
        employee_count=models.Count('employees')
    ).order_by('name')
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return DepartmentReadSerializer
        return DepartmentWriteSerializer


class TeamViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):
    queryset = Team.objects.select_related('department', 'team_lead__profile').all()
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TeamReadSerializer
        return TeamWriteSerializer


# ============================================================================
# EMPLOYEES VIEWSET
# ============================================================================

class EmployeeViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):
    queryset = Employee.objects.select_related(
        'profile', 'organization', 'department', 'team', 'role', 'manager__profile'
    ).all()
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return EmployeeReadSerializer
        return EmployeeWriteSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        dept = self.request.query_params.get('department')
        role = self.request.query_params.get('role')
        emp_status = self.request.query_params.get('status')
        if dept:
            qs = qs.filter(department_id=dept)
        if role:
            qs = qs.filter(role__name=role)
        if emp_status:
            qs = qs.filter(employment_status=emp_status)
        return qs

    @action(detail=True, methods=['get'])
    def hierarchy(self, request, pk=None):
        employee = self.get_object()
        reports = Employee.objects.filter(manager=employee).select_related('profile', 'role')
        return Response({
            "employee": EmployeeCompactSerializer(employee).data,
            "manager": EmployeeCompactSerializer(employee.manager).data if employee.manager else None,
            "direct_reports_count": reports.count(),
            "direct_reports": EmployeeCompactSerializer(reports, many=True).data
        })


# ============================================================================
# CRM & FRONT OFFICE VIEWSETS
# ============================================================================

class InquiryViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):
    queryset = Inquiry.objects.select_related('assigned_to__profile', 'department', 'organization').all()
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return InquiryReadSerializer
        return InquiryWriteSerializer

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        inquiry = self.get_object()
        employee_id = request.data.get('employee_id')
        if not employee_id:
            return Response({"error": "employee_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        employee = get_object_or_404(Employee, id=employee_id)
        inquiry.assigned_to = employee
        inquiry.status = InquiryStatus.ASSIGNED
        inquiry.save()
        return Response(InquiryReadSerializer(inquiry).data)


class LeadViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):
    queryset = Lead.objects.select_related('assigned_to__profile', 'department', 'organization').all()
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return LeadReadSerializer
        return LeadWriteSerializer

    @action(detail=True, methods=['post'])
    def convert(self, request, pk=None):
        lead = self.get_object()
        lead.status = LeadStatus.QUALIFIED
        lead.save()

        # Create Opportunity
        opp_title = request.data.get('title') or f"Deal: {lead.name} ({lead.company or 'Prospect'})"
        opp_value = request.data.get('value') or lead.estimated_value
        opportunity = Opportunity.objects.create(
            organization=lead.organization,
            lead=lead,
            title=opp_title,
            value=opp_value,
            stage=OpportunityStage.QUALIFICATION,
            assigned_to=lead.assigned_to
        )
        return Response({
            "message": "Lead converted successfully.",
            "lead": LeadReadSerializer(lead).data,
            "opportunity": OpportunityReadSerializer(opportunity).data
        }, status=status.HTTP_201_CREATED)


class OpportunityViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):
    queryset = Opportunity.objects.select_related('lead', 'assigned_to__profile', 'organization').all()
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return OpportunityReadSerializer
        return OpportunityWriteSerializer

    @action(detail=True, methods=['patch', 'post'])
    def stage(self, request, pk=None):
        opportunity = self.get_object()
        new_stage = request.data.get('stage')
        if not new_stage:
            return Response({"error": "stage is required."}, status=status.HTTP_400_BAD_REQUEST)
        opportunity.stage = new_stage
        opportunity.save()
        return Response(OpportunityReadSerializer(opportunity).data)


# ============================================================================
# RECRUITMENT & ONBOARDING VIEWSETS
# ============================================================================

class CandidateViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):
    queryset = Candidate.objects.select_related('department', 'assigned_recruiter__profile', 'organization').all()
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CandidateReadSerializer
        return CandidateWriteSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        stage = self.request.query_params.get('stage')
        if stage:
            qs = qs.filter(stage=stage)
        return qs

    @action(detail=True, methods=['patch', 'post'])
    def stage(self, request, pk=None):
        candidate = self.get_object()
        new_stage = request.data.get('stage')
        if not new_stage:
            return Response({"error": "stage is required."}, status=status.HTTP_400_BAD_REQUEST)
        candidate.stage = new_stage
        candidate.save()

        # If transitioned to ONBOARDING, create Onboarding record if not exists
        if new_stage == CandidateStage.ONBOARDING and not candidate.onboardings.exists():
            Onboarding.objects.create(
                organization=candidate.organization,
                candidate=candidate,
                department=candidate.department,
                status=OnboardingStatus.IN_PROGRESS,
                progress=20,
                checklist=[
                    {"id": "c1", "title": "Documentation submission", "completed": False},
                    {"id": "c2", "title": "Equipment allocation", "completed": False},
                    {"id": "c3", "title": "Corporate accounts setup", "completed": False},
                    {"id": "c4", "title": "Manager 1-on-1 scheduled", "completed": False}
                ]
            )

        return Response(CandidateReadSerializer(candidate).data)


class OnboardingViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):
    queryset = Onboarding.objects.select_related(
        'candidate', 'employee__profile', 'department', 'manager__profile', 'organization'
    ).all()
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return OnboardingReadSerializer
        return OnboardingWriteSerializer

    @action(detail=True, methods=['patch', 'post'])
    def step(self, request, pk=None):
        onboarding = self.get_object()
        step = request.data.get('current_step')
        progress = request.data.get('progress')
        checklist = request.data.get('checklist')
        if step:
            onboarding.current_step = step
        if progress is not None:
            onboarding.progress = int(progress)
        if checklist is not None:
            onboarding.checklist = checklist
        onboarding.save()
        return Response(OnboardingReadSerializer(onboarding).data)

    @action(detail=True, methods=['post'], url_path='sign-off')
    def sign_off(self, request, pk=None):
        onboarding = self.get_object()
        onboarding.status = OnboardingStatus.COMPLETED
        onboarding.progress = 100
        onboarding.approval_status = ApprovalStatus.APPROVED
        onboarding.documentation_status = DocumentationStatus.VERIFIED
        onboarding.checklist = [
            {'id': item.get('id', str(idx)), 'title': item.get('title', ''), 'completed': True}
            for idx, item in enumerate(onboarding.checklist or [])
        ]
        onboarding.save()

        # Automatically create active Profile and Employee if candidate exists and no employee linked
        if onboarding.candidate and not onboarding.employee:
            cand = onboarding.candidate
            cand.stage = CandidateStage.EMPLOYEE
            cand.save()

            prof, _ = Profile.objects.get_or_create(
                email=cand.email,
                defaults={
                    'full_name': cand.full_name,
                    'phone': cand.phone,
                    'status': EntityStatus.ACTIVE
                }
            )
            role = Role.objects.filter(name=RoleCode.EMPLOYEE).first() or Role.objects.first()
            emp = Employee.objects.create(
                profile=prof,
                organization=onboarding.organization,
                department=onboarding.department,
                role=role,
                employee_code=f"EMP-{Employee.objects.count() + 1001}",
                designation=cand.position,
                joining_date=timezone.now().date(),
                salary=cand.expected_salary or Decimal('85000.00')
            )
            onboarding.employee = emp
            onboarding.save(update_fields=['employee'])

        return Response({
            "status": "ONBOARDING_COMPLETED",
            "message": "Onboarding completed and signed off.",
            "employee_id": str(onboarding.employee_id) if onboarding.employee_id else None,
            "onboarding": OnboardingReadSerializer(onboarding).data
        })


# ============================================================================
# TASKS VIEWSET
# ============================================================================

class TaskViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):
    queryset = Task.objects.select_related(
        'created_by__profile', 'assigned_to__profile', 'department', 'team', 'organization'
    ).prefetch_related('comments__author__profile').all()
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TaskReadSerializer
        return TaskWriteSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        assigned_to = self.request.query_params.get('assigned_to')
        department = self.request.query_params.get('department')
        if status_filter:
            qs = qs.filter(status=status_filter)
        if assigned_to:
            qs = qs.filter(assigned_to_id=assigned_to)
        if department:
            qs = qs.filter(department_id=department)
        return qs

    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        task = self.get_object()
        if request.method == 'GET':
            comments = task.comments.select_related('author__profile').all()
            return Response(TaskCommentSerializer(comments, many=True).data)

        # POST comment
        comment_text = request.data.get('comment')
        if not comment_text:
            return Response({"error": "Comment text is required."}, status=status.HTTP_400_BAD_REQUEST)

        author = None
        if request.user.is_authenticated and hasattr(request.user, 'central_profile'):
            author = getattr(request.user.central_profile, 'employee', None)
        if not author:
            author = Employee.objects.first()

        comment = TaskComment.objects.create(task=task, author=author, comment=comment_text)
        return Response(TaskCommentSerializer(comment).data, status=status.HTTP_201_CREATED)


# ============================================================================
# APPROVALS VIEWSET
# ============================================================================

class ApprovalViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):
    queryset = Approval.objects.select_related(
        'requester__profile', 'approver__profile', 'organization'
    ).all()
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ApprovalReadSerializer
        return ApprovalWriteSerializer

    @action(detail=True, methods=['post'])
    def action(self, request, pk=None):
        approval = self.get_object()
        action_decision = request.data.get('action', '').upper()
        comment = request.data.get('comment', '')

        if action_decision == 'APPROVE':
            approval.status = ApprovalStatus.APPROVED
        elif action_decision == 'REJECT':
            approval.status = ApprovalStatus.REJECTED
        elif action_decision == 'CANCEL':
            approval.status = ApprovalStatus.CANCELLED
        else:
            return Response(
                {"error": "Invalid action. Supported: APPROVE, REJECT, CANCEL."},
                status=status.HTTP_400_BAD_REQUEST
            )

        approval.comment = comment
        approval.decided_at = timezone.now()
        approval.save()
        return Response(ApprovalReadSerializer(approval).data)


# ============================================================================
# FINANCE & MARKETING VIEWSETS
# ============================================================================

class ExpenseViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):
    queryset = Expense.objects.select_related(
        'department', 'requester__profile', 'approval', 'organization'
    ).all()
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ExpenseReadSerializer
        return ExpenseWriteSerializer

    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        org = get_current_organization(request)
        total_budget = Department.objects.filter(organization=org).aggregate(b=models.Sum('budget'))['b'] or Decimal('0.00')
        total_spent = Expense.objects.filter(organization=org, status__in=[ExpenseStatus.APPROVED, ExpenseStatus.PAID]).aggregate(s=models.Sum('amount'))['s'] or Decimal('0.00')
        pending = Expense.objects.filter(organization=org, status=ExpenseStatus.PENDING).aggregate(p=models.Sum('amount'))['p'] or Decimal('0.00')
        return Response({
            'total_budget': float(total_budget),
            'total_spent': float(total_spent),
            'pending_amount': float(pending),
            'utilization_pct': round((float(total_spent) / float(total_budget) * 100), 2) if total_budget > 0 else 0
        })


class FinanceSummaryView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        org = get_current_organization(request)
        departments = Department.objects.filter(organization=org)
        total_budget = sum(d.budget for d in departments)
        total_spent = Expense.objects.filter(organization=org, status=ExpenseStatus.PAID).aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

        dept_spent_map = {
            row['department']: row['total'] or Decimal('0.00')
            for row in Expense.objects.filter(organization=org, status=ExpenseStatus.PAID)
            .values('department')
            .annotate(total=models.Sum('amount'))
        }

        dept_summaries = []
        for d in departments:
            spent = dept_spent_map.get(d.id, Decimal('0.00'))
            dept_summaries.append({
                "department_id": str(d.id),
                "department_name": d.name,
                "budget": float(d.budget),
                "spent": float(spent),
                "remaining": float(d.budget - spent)
            })

        return Response({
            "total_budget": float(total_budget),
            "total_spent": float(total_spent),
            "utilization_percentage": round((float(total_spent) / float(total_budget) * 100) if total_budget else 0, 2),
            "departments": dept_summaries
        })


class CampaignViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=True, methods=['patch', 'post'])
    def metrics(self, request, pk=None):
        campaign = self.get_object()
        spent = request.data.get('spent')
        leads_generated = request.data.get('leads_generated')
        if spent is not None:
            campaign.spent = Decimal(str(spent))
        if leads_generated is not None:
            campaign.leads_generated = int(leads_generated)
        campaign.save()
        return Response(CampaignSerializer(campaign).data)


# ============================================================================
# NOTIFICATIONS & AUDIT VIEWSETS
# ============================================================================

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.select_related('user').all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=True, methods=['patch', 'post'])
    def read(self, request, pk=None):
        notif = self.get_object()
        notif.is_read = True
        notif.save()
        return Response(NotificationSerializer(notif).data)

    @action(detail=False, methods=['post'], url_path='mark-all-read')
    def mark_all_read(self, request):
        Notification.objects.filter(is_read=False).update(is_read=True)
        return Response({"message": "All notifications marked as read."})


class AuditLogViewSet(TenantScopedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.select_related('user').all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.AllowAny]


# ============================================================================
# EXECUTIVE ANALYTICS & DASHBOARD AGGREGATIONS
# ============================================================================

class AnalyticsDashboardView(APIView):
    """
    Consolidated single-request endpoint returning all executive KPI cards,
    task breakdowns, pipeline progression, and recent activities.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        org = get_current_organization(request)

        # Core Metrics
        total_employees = Employee.objects.filter(organization=org).count()
        active_leads = Lead.objects.filter(
            organization=org
        ).exclude(status__in=[LeadStatus.LOST, LeadStatus.WON]).count()

        pipeline_valuation = Opportunity.objects.filter(
            organization=org
        ).exclude(stage=OpportunityStage.CLOSED_LOST).aggregate(
            total=models.Sum('value')
        )['total'] or Decimal('0.00')

        pending_approvals = Approval.objects.filter(
            organization=org, status=ApprovalStatus.PENDING
        ).count()

        open_tasks = Task.objects.filter(
            organization=org
        ).exclude(status__in=[TaskStatus.COMPLETED, TaskStatus.CANCELLED]).count()

        monthly_burn = Expense.objects.filter(
            organization=org
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')

        # Tasks by status (single aggregation query)
        task_counts = Task.objects.filter(organization=org).aggregate(
            pending=models.Count('id', filter=models.Q(status=TaskStatus.PENDING)),
            in_progress=models.Count('id', filter=models.Q(status=TaskStatus.IN_PROGRESS)),
            completed=models.Count('id', filter=models.Q(status=TaskStatus.COMPLETED)),
            overdue=models.Count('id', filter=models.Q(status=TaskStatus.OVERDUE))
        )
        tasks_by_status = {
            "pending": task_counts['pending'] or 0,
            "in_progress": task_counts['in_progress'] or 0,
            "completed": task_counts['completed'] or 0,
            "overdue": task_counts['overdue'] or 0
        }

        # Leads pipeline breakdown (single grouped query)
        opp_stage_map = {
            row['stage']: (row['count'], row['total'] or Decimal('0.00'))
            for row in Opportunity.objects.filter(organization=org)
            .values('stage')
            .annotate(count=models.Count('id'), total=models.Sum('value'))
        }
        leads_pipeline = []
        for stage_code, stage_label in OpportunityStage.choices:
            cnt, stage_val = opp_stage_map.get(stage_code, (0, Decimal('0.00')))
            leads_pipeline.append({
                "stage": stage_code,
                "label": stage_label,
                "count": cnt,
                "value": float(stage_val)
            })

        # Recent activities (from AuditLog + Notifications)
        recent_activities = []
        logs = AuditLog.objects.filter(organization=org).select_related('user').order_by('-created_at')[:10]
        for log in logs:
            recent_activities.append({
                "id": str(log.id),
                "type": log.module or "SYSTEM",
                "title": log.action.replace('_', ' ').title(),
                "description": f"{log.entity_type} event recorded",
                "timestamp": log.created_at.isoformat(),
                "user": log.user_name or (log.user.full_name if log.user else "System")
            })

        # If logs empty, generate informative placeholder activities
        if not recent_activities:
            recent_activities = [
                {
                    "id": "act-init-1",
                    "type": "APPROVAL",
                    "title": "Expense Approval Processed",
                    "description": "Marketing ad spend reimbursement reviewed",
                    "timestamp": timezone.now().isoformat(),
                    "user": "System Admin"
                },
                {
                    "id": "act-init-2",
                    "type": "RECRUITMENT",
                    "title": "Candidate Shortlisted",
                    "description": "Senior Operations Executive application progressed",
                    "timestamp": timezone.now().isoformat(),
                    "user": "HR Manager"
                }
            ]

        return Response({
            "metrics": {
                "total_employees": total_employees,
                "active_leads": active_leads,
                "pipeline_valuation": float(pipeline_valuation),
                "pending_approvals": pending_approvals,
                "open_tasks": open_tasks,
                "monthly_burn": float(monthly_burn)
            },
            "tasks_by_status": tasks_by_status,
            "leads_pipeline": leads_pipeline,
            "recent_activities": recent_activities
        })


class AnalyticsActivityStreamView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        org = get_current_organization(request)
        logs = AuditLog.objects.filter(organization=org).select_related('user').order_by('-created_at')[:50]
        stream = [
            {
                "id": str(l.id),
                "module": l.module,
                "action": l.action,
                "entity_type": l.entity_type,
                "entity_id": str(l.entity_id) if l.entity_id else None,
                "user_name": l.user_name or (l.user.full_name if l.user else "System"),
                "timestamp": l.created_at.isoformat()
            }
            for l in logs
        ]
        return Response({"activities": stream, "count": len(stream)})


class AnalyticsReportsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        org = get_current_organization(request)
        return Response({
            "hr": {
                "total_headcount": Employee.objects.filter(organization=org).count(),
                "active_candidates": Candidate.objects.filter(organization=org).exclude(stage=CandidateStage.REJECTED).count(),
                "onboarding_in_progress": Onboarding.objects.filter(organization=org, status=OnboardingStatus.IN_PROGRESS).count()
            },
            "finance": {
                "total_budget": float(Department.objects.filter(organization=org).aggregate(t=models.Sum('budget'))['t'] or 0),
                "total_expenses": float(Expense.objects.filter(organization=org).aggregate(t=models.Sum('amount'))['t'] or 0)
            },
            "sales": {
                "total_leads": Lead.objects.filter(organization=org).count(),
                "won_opportunities": Opportunity.objects.filter(organization=org, stage=OpportunityStage.CLOSED_WON).count(),
                "total_deal_value": float(Opportunity.objects.filter(organization=org).aggregate(t=models.Sum('value'))['t'] or 0)
            }
        })


# Alias matching Blueprint 2.0.0 section 4.12 naming
ExecutiveDashboardAnalyticsView = AnalyticsDashboardView

