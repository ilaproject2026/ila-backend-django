from django.contrib import admin
from .models import CommunicationWorkflowRule, DispatchLog

@admin.register(CommunicationWorkflowRule)
class CommunicationWorkflowRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'trigger_event', 'channel', 'category', 'is_active', 'total_dispatched', 'delivered_count', 'opened_count')
    list_filter = ('trigger_event', 'channel', 'category', 'is_active')
    search_fields = ('name', 'subject', 'message_template')

@admin.register(DispatchLog)
class DispatchLogAdmin(admin.ModelAdmin):
    list_display = ('recipient_name', 'channel', 'course_or_batch', 'status', 'dispatched_at', 'latency_ms')
    list_filter = ('channel', 'status', 'dispatched_at')
    search_fields = ('recipient_name', 'recipient_email', 'recipient_phone', 'message_preview')
