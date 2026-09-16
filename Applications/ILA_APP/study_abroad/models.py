from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    flag = models.CharField(max_length=10, default="🇩🇪")
    visa_type = models.CharField(max_length=200, default="National Student Visa (APS / 16b)")
    currency = models.CharField(max_length=50, default="EUR (€)")
    avg_tuition = models.CharField(max_length=150, default="€0 - €3,000 / yr")
    living_cost = models.CharField(max_length=150, default="€934 / mo (Blocked Account)")
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=50,
        choices=[("Active", "Active"), ("Coming Soon", "Coming Soon")],
        default="Active",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class College(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="colleges")
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=150)
    ranking = models.CharField(max_length=100, default="Top Ranked")
    institution_type = models.CharField(
        max_length=100,
        choices=[
            ("Public", "Public University (€0 Tuition)"),
            ("University of Applied Sciences", "University of Applied Sciences (UAS)"),
            ("Technical University", "Technical University (TU9)"),
            ("Private", "Private University"),
        ],
        default="Public",
    )
    admission_criteria = models.TextField(default="Min 7.0 CGPA, APS Certificate, IELTS 6.5")
    terms = models.JSONField(default=list, help_text="List of admission terms/checklists")
    contact_email = models.EmailField(blank=True)
    status = models.CharField(
        max_length=50,
        choices=[("Active", "Active"), ("Partnered", "Partnered"), ("Under Review", "Under Review")],
        default="Partnered",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.city} ({self.country.name})"


class StudyAbroadCourse(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="courses")
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name="courses")
    course_name = models.CharField(max_length=255)
    degree = models.CharField(
        max_length=50,
        choices=[
            ("Masters", "Masters (M.Sc / M.Eng)"),
            ("Bachelors", "Bachelors (B.Sc / B.Eng)"),
            ("Ausbildung", "Ausbildung (Paid Dual Study)"),
            ("Diploma", "Diploma / Certificate"),
        ],
        default="Masters",
    )
    duration = models.CharField(max_length=100, default="2 Years (4 Semesters)")
    language = models.CharField(
        max_length=50,
        choices=[("English", "English"), ("German", "German"), ("Bilingual", "Bilingual")],
        default="English",
    )
    tuition_per_year = models.CharField(max_length=150, default="€0 (Semester fee only)")
    min_cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=7.0)
    min_ielts = models.DecimalField(max_digits=3, decimal_places=1, default=6.5)
    min_german_level = models.CharField(
        max_length=20,
        choices=[
            ("None", "None"),
            ("A1", "A1"),
            ("A2", "A2"),
            ("B1", "B1"),
            ("B2", "B2"),
            ("C1", "C1"),
        ],
        default="None",
    )
    intake_season = models.JSONField(default=list, help_text="e.g. ['Winter (Oct)', 'Summer (Apr)']")
    description = models.TextField(blank=True)
    is_featured = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course_name} ({self.degree}) - {self.college.name}"


class StudentApplication(models.Model):
    student_name = models.CharField(max_length=200)
    student_email = models.EmailField()
    student_phone = models.CharField(max_length=50)
    target_country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    target_degree = models.CharField(max_length=50, default="Masters")
    preferred_field = models.CharField(max_length=150, default="Computer Science & AI")
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=8.0)
    ielts_score = models.DecimalField(max_digits=3, decimal_places=1, default=6.5)
    german_level = models.CharField(max_length=20, default="None")
    budget_eur = models.IntegerField(default=12000)
    resume_file_name = models.CharField(max_length=255, blank=True)
    
    # Matching / Assignment
    assigned_college = models.ForeignKey(College, on_delete=models.SET_NULL, null=True, blank=True)
    matched_course = models.ForeignKey(StudyAbroadCourse, on_delete=models.SET_NULL, null=True, blank=True)
    match_score = models.IntegerField(default=85)
    
    # Privacy Shield: Revealed to student only after Admin approval
    is_college_revealed = models.BooleanField(
        default=False, 
        help_text="Controls whether the student can see the specific College name or just the course/country."
    )
    
    status = models.CharField(
        max_length=50,
        choices=[
            ("Submitted", "Submitted"),
            ("Matched", "Matched"),
            ("Under Review", "Under Review"),
            ("College Approved", "College Approved"),
            ("Visa Processing", "Visa Processing"),
            ("Rejected", "Rejected"),
        ],
        default="Submitted",
    )
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} - {self.target_country.name if self.target_country else 'Abroad'} ({self.status})"


class DocumentChecklist(models.Model):
    country = models.CharField(max_length=100, default="Germany")
    course_track = models.CharField(max_length=100, default="All")
    doc_name = models.CharField(max_length=255)
    is_required = models.BooleanField(default=True)
    accepted_formats = models.CharField(max_length=100, default="PDF, JPG, PNG")
    max_size_mb = models.IntegerField(default=5)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.doc_name} ({self.country} - {self.course_track})"


class ConsultantATSTask(models.Model):
    STAGE_CHOICES = [
        ("Lead / Intake", "Lead / Intake"),
        ("Document Verification", "Document Verification"),
        ("University Review", "University Review"),
        ("Interview Scheduled", "Interview Scheduled"),
        ("Visa Preparation", "Visa Preparation"),
        ("Enrolled", "Enrolled"),
        ("Closed / Dropped", "Closed / Dropped"),
    ]

    student_account_id = models.CharField(max_length=150)
    student_name = models.CharField(max_length=200)
    student_email = models.EmailField()
    student_phone = models.CharField(max_length=50)
    target_country = models.CharField(max_length=100, default="Germany")
    target_course = models.CharField(max_length=255)
    match_score = models.IntegerField(default=90)
    stage = models.CharField(max_length=50, choices=STAGE_CHOICES, default="Lead / Intake")
    assigned_consultant = models.CharField(max_length=200, default="Sarah Müller (Senior Admissions Lead)")
    uploaded_documents = models.JSONField(
        default=list, 
        help_text="List of objects: [{'checklistId', 'docName', 'fileName', 'fileSize', 'uploadedAt', 'verified'}]"
    )
    consultant_notes = models.JSONField(
        default=list, 
        help_text="List of objects: [{'id', 'author', 'note', 'timestamp', 'nextFollowUpDate'}]"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ATS-{self.id}: {self.student_name} ({self.stage})"


class HybridAILog(models.Model):
    ACTOR_CHOICES = [
        ("ILA_AI", "ILA AI System"),
        ("HUMAN_CONSULTANT", "Human Consultant"),
    ]

    ats_task = models.ForeignKey(ConsultantATSTask, on_delete=models.CASCADE, related_name="hybrid_logs")
    actor = models.CharField(max_length=50, choices=ACTOR_CHOICES, default="ILA_AI")
    action = models.CharField(max_length=200)
    details = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.actor}] {self.action} - Task #{self.ats_task.id}"



class CountryTieUpCategory(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="tieup_categories")
    category_id = models.CharField(max_length=100, help_text="Unique slug/filter key e.g. public_uni, ausbildung, masters")
    label = models.CharField(max_length=150, help_text="Display label e.g. Ausbildung Dual Study")
    badge = models.CharField(max_length=100, blank=True, default="", help_text="e.g. Free Tuition, High Demand")
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "id"]
        verbose_name_plural = "Country Tie-Up Categories"

    def __str__(self):
        return f"{self.country.name} - {self.label}"
