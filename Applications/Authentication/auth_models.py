from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid
import secrets
import string
from django.utils import timezone
from datetime import timedelta


def generate_referral_code(length=8):
    characters = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


class CustomUserManager(BaseUserManager):
    def create_user(self, username=None, email=None, phone=None, password=None, **extra_fields):
        if not (username or email or phone):
            raise ValueError("User must have either a username, email, or phone")

        if email:
            email = self.normalize_email(email)

        user = self.model(
            username=username,
            email=email,
            phone=phone,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, phone=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username=username, email=email, phone=phone, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    id = models.AutoField(primary_key=True)
    
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    password = models.CharField(max_length=128)
    
    first_name = models.CharField(max_length=150, blank=True, default='')
    last_name = models.CharField(max_length=150, blank=True, default='')
    fullname = models.CharField(max_length=255, null=True, blank=True)
    
    referral_code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')
    
    # Binary Referral Tree Placement
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    position = models.CharField(max_length=1, choices=[('L', 'Left'), ('R', 'Right')], null=True, blank=True)
    
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Role & Department Hierarchy (Blueprint Multi-Tier RBAC)
    ROLE_CHOICES = [
        ('Super Admin', 'Super Admin (Global Authority / Kuttan)'),
        ('CEO', 'Master CEO'),
        ('General Manager', 'General Manager (Operational Oversight)'),
        ('Academic HOD', 'Department Head - Education & All Courses'),
        ('Study Abroad HOD', 'Department Head - Study Abroad Hub'),
        ('Visa HOD', 'Department Head - Visa & Compliance'),
        ('Work & Study HOD', 'Department Head - Work and Study Hub'),
        ('Jobs HOD', 'Department Head - Jobs & Career Hub'),
        ('HR Manager', 'HR Department Manager'),
        ('Finance Officer', 'Finance & Accounts Officer'),
        ('Marketing Exec', 'Marketing Studio Executive'),
        ('Academic Counselor', 'Front Office Intake & Academic Counselor'),
        ('Franchise Partner', 'Franchise Partner / Regional Territory Lead'),
        ('student', 'Student / Candidate Enrollee'),
        ('employer', 'Corporate Employer / Partner'),
        ('Tech Admin', 'Tech Admin'),
        ('Student', 'Student'),
        ('Partner', 'Partner'),
    ]
    DEPARTMENT_CHOICES = [
        ('Super Admin', 'Super Admin'),
        ('General Manager', 'General Manager'),
        ('Finance', 'Finance'),
        ('HR', 'HR'),
        ('Marketing', 'Marketing'),
        ('Academic', 'Academic'),
        ('Visa', 'Visa'),
        ('Study Abroad', 'Study Abroad'),
        ('Jobs', 'Jobs'),
        ('Front Office', 'Front Office'),
    ]

    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='student')
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES, null=True, blank=True)
    avatar = models.CharField(max_length=500, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    security_pin_hash = models.CharField(max_length=255, null=True, blank=True)

    hr_issued_id = models.CharField(max_length=50, blank=True, null=True, unique=True)
    hr_approval_status = models.CharField(
        max_length=50,
        choices=[('Pending HR Approval', 'Pending HR Approval'), ('Verified', 'Verified'), ('Rejected', 'Rejected')],
        default='Verified'
    )
    status = models.CharField(
        max_length=50,
        choices=[('Active', 'Active'), ('On Leave', 'On Leave'), ('Terminated', 'Terminated')],
        default='Active'
    )
    is_biometric_authorized = models.BooleanField(default=False)

    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "phone"]

    def get_full_name(self):
        full = f"{self.first_name} {self.last_name}".strip()
        return full or self.fullname or self.username or ''

    @property
    def created_at(self):
        return self.date_joined

    def save(self, *args, **kwargs):
        if not self.referral_code:
            code = generate_referral_code()
            while User.objects.filter(referral_code=code).exists():
                code = generate_referral_code()
            self.referral_code = code
        super().save(*args, **kwargs)

    @property
    def left_child(self):
        return self.children.filter(position='L').first()

    @property
    def right_child(self):
        return self.children.filter(position='R').first()

    def __str__(self):
        return self.username or self.email or self.phone or "User"


class RegistrationOTP(models.Model):
    identifier = models.CharField(max_length=255)
    username = models.CharField(max_length=150, null=True, blank=True)
    referral_code = models.CharField(max_length=50, null=True, blank=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.identifier} - {self.otp}"
    
    def save(self, *args, **kwargs):
        # Delete old OTPs for the same identifier
        RegistrationOTP.objects.filter(identifier=self.identifier).delete()
        super().save(*args, **kwargs)

    def is_valid(self, input_otp):
        # OTP is valid for 10 minutes
        if self.otp != input_otp:
            return False
        if timezone.now() > self.created_at + timedelta(minutes=10):
            return False
        return True


class FranchisePartner(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    region = models.CharField(max_length=255, default='Germany / EU')
    partner_token = models.CharField(max_length=255, unique=True, null=True, blank=True)
    franchise_token = models.CharField(max_length=255, unique=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_franchises')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.id:
            import uuid
            self.id = f"FRN-{uuid.uuid4().hex[:8]}"
        if not self.franchise_token:
            self.franchise_token = self.partner_token or f"ILA-FR-{uuid.uuid4().hex[:6].upper()}"
        if not self.partner_token:
            self.partner_token = self.franchise_token
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.id})"



class AuditLog(models.Model):
    CATEGORY_CHOICES = [
        ('System', 'System'),
        ('Content', 'Content'),
        ('Personnel', 'Personnel'),
        ('Data', 'Data'),
    ]

    id = models.CharField(max_length=50, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    department = models.CharField(max_length=100, null=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='System')
    action = models.CharField(max_length=255)
    details = models.TextField(null=True, blank=True)
    ip_address = models.CharField(max_length=50, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.category}] {self.action} by {self.user or 'System'} at {self.timestamp}"

