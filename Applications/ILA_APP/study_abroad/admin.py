from django.contrib import admin
from .models import (
    Country,
    College,
    StudyAbroadCourse,
    StudentApplication,
    DocumentChecklist,
    ConsultantATSTask,
    HybridAILog,
)


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "flag", "visa_type", "status", "created_at")
    search_fields = ("name", "code")


@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "city", "ranking", "institution_type", "status")
    list_filter = ("country", "institution_type", "status")
    search_fields = ("name", "city")


@admin.register(StudyAbroadCourse)
class StudyAbroadCourseAdmin(admin.ModelAdmin):
    list_display = ("course_name", "degree", "college", "country", "language", "min_cgpa", "min_ielts")
    list_filter = ("degree", "language", "country")
    search_fields = ("course_name", "college__name")


@admin.register(StudentApplication)
class StudentApplicationAdmin(admin.ModelAdmin):
    list_display = ("student_name", "student_email", "target_country", "target_degree", "is_college_revealed", "status")
    list_filter = ("status", "is_college_revealed", "target_country")
    search_fields = ("student_name", "student_email", "student_phone")


@admin.register(DocumentChecklist)
class DocumentChecklistAdmin(admin.ModelAdmin):
    list_display = ("doc_name", "country", "course_track", "is_required", "accepted_formats", "max_size_mb")
    list_filter = ("country", "course_track", "is_required")
    search_fields = ("doc_name", "country")


@admin.register(ConsultantATSTask)
class ConsultantATSTaskAdmin(admin.ModelAdmin):
    list_display = ("student_name", "student_email", "target_country", "target_course", "match_score", "stage", "assigned_consultant")
    list_filter = ("stage", "target_country", "assigned_consultant")
    search_fields = ("student_name", "student_email", "student_phone", "target_course")


@admin.register(HybridAILog)
class HybridAILogAdmin(admin.ModelAdmin):
    list_display = ("ats_task", "actor", "action", "created_at")
    list_filter = ("actor", "created_at")
    search_fields = ("action", "details")

