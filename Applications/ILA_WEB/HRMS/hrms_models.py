from django.db import models
from django.conf import settings
import uuid


def generate_att_id():
    return f"ATT-{uuid.uuid4().hex[:6]}"


def generate_cand_id():
    return f"CAND-{uuid.uuid4().hex[:6]}"


def generate_task_id():
    return f"TASK-{uuid.uuid4().hex[:6]}"


def generate_req_id():
    return f"REQ-{uuid.uuid4().hex[:6]}"


class StaffProfile(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('On Leave', 'On Leave'),
        ('Terminated', 'Terminated'),
    ]

    APPROVAL_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='staff_profile')
    employee_id = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=100)
    joining_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Active')
    phone = models.CharField(max_length=50, blank=True)
    resume_url = models.CharField(max_length=500, blank=True)
    hr_approval_status = models.CharField(max_length=50, choices=APPROVAL_STATUS_CHOICES, default='Approved')
    monthly_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    class Meta:
        ordering = ['employee_id']

    def __str__(self):
        return f"{self.user.fullname or self.user.username} ({self.employee_id}) - {self.department}"


class AttendanceLog(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('On Leave', 'On Leave'),
        ('Late', 'Late'),
    ]

    id = models.CharField(max_length=50, primary_key=True, default=generate_att_id)
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='attendance_logs')
    date = models.DateField(db_index=True)
    check_in_time = models.CharField(max_length=50, blank=True)
    check_out_time = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Present')

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.staff.employee_id} on {self.date}: {self.status}"


class HRCandidate(models.Model):
    STAGE_CHOICES = [
        ('Hiring & Interview', 'Hiring & Interview'),
        ('Pending Department Approval', 'Pending Department Approval'),
        ('Onboarding & Payroll', 'Onboarding & Payroll'),
        ('Training & ID Generation', 'Training & ID Generation'),
        ('Completed', 'Completed'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    id = models.CharField(max_length=50, primary_key=True, default=generate_cand_id)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    position = models.CharField(max_length=255)
    department = models.CharField(max_length=100)
    stage = models.CharField(max_length=100, choices=STAGE_CHOICES, default='Hiring & Interview')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    expected_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    offered_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    notes = models.TextField(blank=True)
    character_analysis = models.TextField(blank=True)
    resume_url = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.position} ({self.stage})"


class EnterpriseTask(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Success', 'Success'),
        ('Negative', 'Negative'),
    ]

    PRIORITY_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]

    id = models.CharField(max_length=50, primary_key=True, default=generate_task_id)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assigned_to_dept = models.CharField(max_length=100)
    assigned_staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES, default='Medium')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.priority}] {self.title} ({self.status})"


class ApprovalRequest(models.Model):
    REQUEST_TYPE_CHOICES = [
        ('New Staff', 'New Staff'),
        ('New Course', 'New Course'),
        ('Data Edit', 'Data Edit'),
        ('Deletion', 'Deletion'),
        ('General', 'General'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    id = models.CharField(max_length=50, primary_key=True, default=generate_req_id)
    request_type = models.CharField(max_length=50, choices=REQUEST_TYPE_CHOICES, default='General')
    description = models.TextField()
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='submitted_requests')
    department = models.CharField(max_length=100)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_requests')
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.request_type} from {self.department}: {self.status}"
