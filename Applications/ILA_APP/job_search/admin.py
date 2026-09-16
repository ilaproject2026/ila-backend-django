from django.contrib import admin
from .models import PartnerCompany, JobListing, CandidateResume, JobMatch


@admin.register(PartnerCompany)
class PartnerCompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "industry", "country", "hiring_tier", "contact_person", "status")
    list_filter = ("country", "hiring_tier", "status")
    search_fields = ("name", "industry", "contact_person")


@admin.register(JobListing)
class JobListingAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "domain", "country", "city", "salary_range", "blue_card_eligible", "status")
    list_filter = ("domain", "country", "blue_card_eligible", "status")
    search_fields = ("title", "company__name", "city")


@admin.register(CandidateResume)
class CandidateResumeAdmin(admin.ModelAdmin):
    list_display = ("candidate_name", "email", "field", "years_of_experience", "target_country", "german_level", "status")
    list_filter = ("field", "target_country", "german_level", "status")
    search_fields = ("candidate_name", "email", "phone")


@admin.register(JobMatch)
class JobMatchAdmin(admin.ModelAdmin):
    list_display = ("candidate", "job", "match_score", "status", "matched_at")
    list_filter = ("status",)
    search_fields = ("candidate__candidate_name", "job__title")
