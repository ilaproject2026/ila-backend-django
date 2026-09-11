from django.contrib import admin
from .models import DepartmentInquiry, FollowUpAutoTriggerRule, SocialMediaCampaign


@admin.register(DepartmentInquiry)
class DepartmentInquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "form_type", "phone", "program_of_interest", "status", "created_at")
    list_filter = ("category", "form_type", "status", "department")
    search_fields = ("name", "email", "phone", "program_of_interest")


@admin.register(FollowUpAutoTriggerRule)
class FollowUpAutoTriggerRuleAdmin(admin.ModelAdmin):
    list_display = ("trigger_name", "department", "event_type", "channel", "delay_hours", "is_active", "execution_count")
    list_filter = ("department", "event_type", "channel", "is_active")
    search_fields = ("trigger_name",)


@admin.register(SocialMediaCampaign)
class SocialMediaCampaignAdmin(admin.ModelAdmin):
    list_display = ("title", "department", "status", "reach_count", "clicks_count", "scheduled_at")
    list_filter = ("department", "status")
    search_fields = ("title",)
