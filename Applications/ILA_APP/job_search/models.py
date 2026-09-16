from django.db import models


class PartnerCompany(models.Model):
    name = models.CharField(max_length=255)
    logo = models.CharField(max_length=50, default="🏢")
    industry = models.CharField(max_length=150)
    location = models.CharField(max_length=200)
    country = models.CharField(max_length=100, default="Germany")
    hiring_tier = models.CharField(
        max_length=100,
        choices=[
            ("Strategic Partner", "Strategic Partner"),
            ("Enterprise Client", "Enterprise Client"),
            ("Direct Recruiter", "Direct Recruiter"),
        ],
        default="Strategic Partner",
    )
    website = models.URLField(blank=True)
    contact_person = models.CharField(max_length=200, blank=True)
    status = models.CharField(
        max_length=50,
        choices=[("Active", "Active"), ("Under Audit", "Under Audit")],
        default="Active",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.country})"


class JobListing(models.Model):
    company = models.ForeignKey(PartnerCompany, on_delete=models.CASCADE, related_name="jobs")
    title = models.CharField(max_length=255)
    domain = models.CharField(
        max_length=100,
        choices=[
            ("Software & IT", "Software & IT"),
            ("Healthcare", "Healthcare"),
            ("Engineering", "Engineering"),
            ("Business & Finance", "Business & Finance"),
            ("Operations", "Operations"),
        ],
        default="Software & IT",
    )
    country = models.CharField(max_length=100, default="Germany")
    city = models.CharField(max_length=100, default="Munich")
    salary_range = models.CharField(max_length=150, default="€65,000 - €80,000 / yr")
    contract_type = models.CharField(
        max_length=100,
        choices=[
            ("Full-Time Permanent", "Full-Time Permanent"),
            ("Dual Training (Ausbildung)", "Dual Training (Ausbildung)"),
            ("Hybrid Contractor", "Hybrid Contractor"),
        ],
        default="Full-Time Permanent",
    )
    blue_card_eligible = models.BooleanField(default=True)
    required_skills = models.JSONField(default=list, help_text="e.g. ['Kubernetes', 'Go', 'AWS']")
    min_experience = models.CharField(max_length=100, default="2+ Years")
    min_german_level = models.CharField(
        max_length=20,
        choices=[
            ("None", "None"),
            ("A2", "A2"),
            ("B1", "B1"),
            ("B2", "B2"),
            ("C1", "C1"),
        ],
        default="None",
    )
    openings = models.IntegerField(default=1)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=50,
        choices=[("Active", "Active"), ("Draft", "Draft"), ("Filled", "Filled")],
        default="Active",
    )
    posted_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} at {self.company.name}"


class CandidateResume(models.Model):
    candidate_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    target_country = models.CharField(max_length=100, default="Germany")
    field = models.CharField(max_length=150, default="Software & IT")
    years_of_experience = models.IntegerField(default=3)
    highest_degree = models.CharField(max_length=150, default="B.Tech Computer Science")
    primary_skills = models.JSONField(default=list, help_text="Parsed skill tokens")
    german_level = models.CharField(max_length=20, default="None")
    english_level = models.CharField(max_length=50, default="Fluent")
    resume_file_name = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ("New", "New"),
            ("Matched", "Matched"),
            ("Interview Scheduled", "Interview Scheduled"),
            ("Placed", "Placed"),
            ("Archived", "Archived"),
        ],
        default="New",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidate_name} ({self.field}) - {self.status}"


class JobMatch(models.Model):
    candidate = models.ForeignKey(CandidateResume, on_delete=models.CASCADE, related_name="matches")
    job = models.ForeignKey(JobListing, on_delete=models.CASCADE, related_name="matches")
    match_score = models.IntegerField(default=75)
    matched_skills = models.JSONField(default=list)
    status = models.CharField(
        max_length=50,
        choices=[
            ("Suggested", "Suggested"),
            ("Shortlisted", "Shortlisted"),
            ("Interview Scheduled", "Interview Scheduled"),
            ("Offer Extended", "Offer Extended"),
            ("Rejected", "Rejected"),
        ],
        default="Suggested",
    )
    matched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidate.candidate_name} -> {self.job.title} ({self.match_score}%)"
