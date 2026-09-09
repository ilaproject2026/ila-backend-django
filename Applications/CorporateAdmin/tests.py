from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from .models import (
    Organization, Department, Employee, Profile, Role, RoleCode,
    Task, Approval, ApprovalType, ApprovalStatus, TaskPriority, TaskStatus
)


class CorporateAdminTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create Organization
        self.org = Organization.objects.create(
            name="GEG Test Enterprise",
            code="GEG-TEST",
            description="Test Organization for Command Center"
        )

        # Create Role
        self.role = Role.objects.create(
            name=RoleCode.CEO,
            display_name="Chief Executive Officer",
            level=1
        )

        # Create Profile
        self.profile = Profile.objects.create(
            full_name="Alexander Hunt",
            email="alexander.hunt@test-geg.com"
        )

        # Create Department
        self.dept = Department.objects.create(
            organization=self.org,
            name="Executive Operations",
            code="DEP-EXEC-TEST",
            budget=Decimal("500000.00")
        )

        # Create Employee
        self.employee = Employee.objects.create(
            organization=self.org,
            profile=self.profile,
            department=self.dept,
            role=self.role,
            employee_code="EMP-TEST-001",
            designation="Chief Executive Officer",
            salary=Decimal("30000.00")
        )
        self.dept.department_head = self.employee
        self.dept.save()

    def test_current_organization_endpoint(self):
        url = reverse('organization-current')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], "GEG-TEST")

    def test_departments_list(self):
        url = reverse('department-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_employee_hierarchy(self):
        # Create subordinate
        sub_prof = Profile.objects.create(full_name="Junior Staff", email="junior@test.com")
        sub_emp = Employee.objects.create(
            organization=self.org,
            profile=sub_prof,
            department=self.dept,
            role=self.role,
            employee_code="EMP-TEST-002",
            designation="Junior Associate",
            manager=self.employee
        )
        url = reverse('employee-hierarchy', args=[self.employee.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['direct_reports_count'], 1)

    def test_task_creation_and_comment(self):
        task = Task.objects.create(
            organization=self.org,
            title="Deploy Security Patch",
            assigned_to=self.employee,
            department=self.dept,
            priority=TaskPriority.HIGH,
            status=TaskStatus.IN_PROGRESS
        )
        # Add comment
        url = reverse('task-comments', args=[task.id])
        response = self.client.post(url, {"comment": "Deployment initiated successfully."}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(task.comments.count(), 1)

    def test_approval_action(self):
        approval = Approval.objects.create(
            organization=self.org,
            requester=self.employee,
            request_type=ApprovalType.EXPENSE,
            amount=Decimal("1200.00"),
            status=ApprovalStatus.PENDING
        )
        url = reverse('approval-action', args=[approval.id])
        response = self.client.post(url, {"action": "APPROVE", "comment": "Approved by board"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        approval.refresh_from_db()
        self.assertEqual(approval.status, ApprovalStatus.APPROVED)

    def test_analytics_dashboard_endpoint(self):
        url = reverse('corporate-analytics-dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("metrics", response.data)
        self.assertIn("tasks_by_status", response.data)
        self.assertIn("leads_pipeline", response.data)
        self.assertIn("recent_activities", response.data)
        self.assertEqual(response.data['metrics']['total_employees'], 1)

    def test_onboarding_sign_off_auto_provisioning(self):
        from .models import Candidate, Onboarding, OnboardingStatus, CandidateStage
        candidate = Candidate.objects.create(
            organization=self.org,
            full_name="Elena Gilbert",
            email="elena.gilbert@test.com",
            phone="+123456789",
            position="VP of Human Resources",
            department=self.dept,
            stage=CandidateStage.ONBOARDING
        )
        onboarding = Onboarding.objects.create(
            organization=self.org,
            candidate=candidate,
            department=self.dept,
            status=OnboardingStatus.IN_PROGRESS
        )
        url = reverse('onboarding-sign-off', args=[onboarding.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        onboarding.refresh_from_db()
        self.assertEqual(onboarding.status, OnboardingStatus.COMPLETED)
        self.assertIsNotNone(onboarding.employee)
        self.assertEqual(onboarding.employee.profile.email, "elena.gilbert@test.com")

