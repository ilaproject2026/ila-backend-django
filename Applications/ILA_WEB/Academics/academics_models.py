from django.db import models
from django.conf import settings
import uuid


def generate_subcategory_id():
    return f"subcat-{uuid.uuid4().hex[:6]}"


def generate_batch_id():
    return f"batch-{uuid.uuid4().hex[:6]}"


def generate_session_id():
    return f"sess-{uuid.uuid4().hex[:6]}"


class GlobalCategory(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class GlobalSubCategory(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_subcategory_id)
    category = models.ForeignKey(GlobalCategory, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} - {self.category.name}"


class TeachingStrategy(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    tagline = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    pacing_model = models.CharField(max_length=100, blank=True)
    target_learner = models.CharField(max_length=255, blank=True)
    default_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.name} ({self.category})"


class StudentAnalyzingStrategy(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255)
    target_metric = models.CharField(max_length=100)
    threshold = models.CharField(max_length=50, blank=True)
    description = models.TextField()
    adaptation_action = models.CharField(max_length=255, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.name} - {self.target_metric}"


class GlobalCourse(models.Model):
    VIEW_TYPE_CHOICES = [
        ('Main View', 'Main View'),
        ('Blocks View', 'Blocks View'),
        ('Both', 'Both'),
    ]

    LIBRARY_TYPE_CHOICES = [
        ('TUTOR', 'TUTOR'),
        ('AI', 'AI'),
    ]

    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255)
    top_title = models.CharField(max_length=255, blank=True)
    subtitle = models.CharField(max_length=255, blank=True)
    category = models.ForeignKey(GlobalCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    sub_category_name = models.CharField(max_length=255, blank=True)
    show_in_sub_nav = models.BooleanField(default=True)
    display_position = models.IntegerField(default=0)
    view_type = models.CharField(max_length=50, choices=VIEW_TYPE_CHOICES, default='Both')
    library_type = models.CharField(max_length=50, choices=LIBRARY_TYPE_CHOICES, default='TUTOR')

    staff_assigned = models.CharField(max_length=255, null=True, blank=True)
    chapters_count = models.IntegerField(default=0)
    duration = models.CharField(max_length=100, default='3 Months')
    fee = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    enrolled_count = models.IntegerField(default=0)

    course_structure = models.TextField(blank=True)
    ai_payload = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_position', 'name']

    def __str__(self):
        return self.name


class GlobalPath(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    course = models.ForeignKey(GlobalCourse, on_delete=models.CASCADE, related_name='paths')
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    methods = models.CharField(max_length=255, blank=True)
    position = models.IntegerField(default=0)
    starting_date = models.DateField(null=True, blank=True)
    ending_date = models.DateField(null=True, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ['position', 'name']

    def __str__(self):
        return f"{self.course.name} - {self.name} ({self.code})"


class GlobalBatch(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_batch_id)
    course = models.ForeignKey(GlobalCourse, on_delete=models.CASCADE, related_name='batches')
    path = models.ForeignKey(GlobalPath, on_delete=models.SET_NULL, null=True, blank=True, related_name='batches')
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    timings = models.JSONField(default=list, blank=True)
    starting_date = models.DateField(null=True, blank=True)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.code}) - {self.course.name}"


class ClassScheduleSession(models.Model):
    STATUS_CHOICES = [
        ('Upcoming', 'Upcoming'),
        ('Live', 'Live'),
        ('Completed', 'Completed'),
        ('Rescheduled', 'Rescheduled'),
    ]

    id = models.CharField(max_length=50, primary_key=True, default=generate_session_id)
    date = models.DateField(db_index=True)
    course = models.ForeignKey(GlobalCourse, on_delete=models.CASCADE, related_name='schedule_sessions')
    batch = models.ForeignKey(GlobalBatch, on_delete=models.SET_NULL, null=True, blank=True, related_name='schedule_sessions')
    path = models.ForeignKey(GlobalPath, on_delete=models.SET_NULL, null=True, blank=True, related_name='schedule_sessions')
    instructor = models.CharField(max_length=255)
    time_slot = models.CharField(max_length=100)
    start_time = models.CharField(max_length=50)
    end_time = models.CharField(max_length=50)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Upcoming')
    room = models.CharField(max_length=100, default='Studio A')
    enrolled_count = models.IntegerField(default=0)
    topic = models.CharField(max_length=255)
    meeting_link = models.URLField(null=True, blank=True)

    class Meta:
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.date} {self.time_slot}: {self.course.name} ({self.topic})"


class CourseMaterial(models.Model):
    MATERIAL_TYPE_CHOICES = [
        ('chapters', 'chapters'),
        ('images', 'images'),
        ('video', 'video'),
        ('promo', 'promo'),
    ]

    course = models.ForeignKey(GlobalCourse, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=255)
    material_type = models.CharField(max_length=50, choices=MATERIAL_TYPE_CHOICES, default='chapters')
    file_url = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.name} - {self.title} ({self.material_type})"


class StudentEnrollment(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('In Class', 'In Class'),
        ('Invited', 'Invited'),
        ('Absent', 'Absent'),
        ('Completed', 'Completed'),
    ]

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(GlobalCourse, on_delete=models.CASCADE, related_name='enrollments')
    batch = models.ForeignKey(GlobalBatch, on_delete=models.SET_NULL, null=True, blank=True, related_name='enrollments')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Present')
    attendance_score = models.IntegerField(default=100)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} in {self.course.name}"
