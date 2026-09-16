from django.contrib import admin
from .models import WorkStudyPackage, WorkStudyRoleFeature, WorkStudyStream, WorkStudyCandidate

class WorkStudyRoleFeatureInline(admin.TabularInline):
    model = WorkStudyRoleFeature
    extra = 3

class WorkStudyStreamInline(admin.TabularInline):
    model = WorkStudyStream
    extra = 2

@admin.register(WorkStudyPackage)
class WorkStudyPackageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'stipend', 'status', 'promoted_to_marketing', 'created_at')
    list_filter = ('category', 'status', 'promoted_to_marketing')
    search_fields = ('title', 'description', 'stipend')
    inlines = [WorkStudyRoleFeatureInline, WorkStudyStreamInline]

@admin.register(WorkStudyCandidate)
class WorkStudyCandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'package', 'stage', 'current_stipend', 'progress_pct', 'applied_date')
    list_filter = ('stage', 'stipend_status', 'applied_date')
    search_fields = ('name', 'email', 'phone', 'corporate_project')
