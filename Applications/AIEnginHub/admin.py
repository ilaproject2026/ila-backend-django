from django.contrib import admin
from .models import (
    CourseCategory, LibraryCourse, CourseChapter, CourseVersionSnapshot,
    ChatSession, ChatMessage, LegacyChatHistory,
    TieupLead, TieupPolicy, OutreachStatusLog, SmtpConfiguration,
    AIProductPreset, GenerationJob, SystemActivityLog, MetricSnapshot
)


class CourseChapterInline(admin.TabularInline):
    model = CourseChapter
    extra = 0
    fields = ('chapter_number', 'title', 'is_completed')


class CourseVersionSnapshotInline(admin.TabularInline):
    model = CourseVersionSnapshot
    extra = 0
    fields = ('version_number', 'label', 'auto_saved', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'department', 'color', 'created_at')
    search_fields = ('name', 'department', 'description')


@admin.register(LibraryCourse)
class LibraryCourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'total_chapters', 'is_permanent', 'locked', 'download_count', 'updated_at')
    list_filter = ('category', 'is_permanent', 'locked', 'is_favorite')
    search_fields = ('title', 'subtitle', 'overview', 'tags')
    inlines = [CourseChapterInline, CourseVersionSnapshotInline]


@admin.register(CourseChapter)
class CourseChapterAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'chapter_number', 'title', 'is_completed')
    list_filter = ('is_completed',)
    search_fields = ('title', 'summary', 'content')


@admin.register(CourseVersionSnapshot)
class CourseVersionSnapshotAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'version_number', 'label', 'auto_saved', 'created_at')
    list_filter = ('auto_saved',)


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    fields = ('role', 'content', 'model', 'response_time_ms', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'product_type', 'is_pinned', 'is_permanent', 'locked', 'updated_at')
    list_filter = ('product_type', 'is_pinned', 'is_permanent', 'locked')
    search_fields = ('title', 'product_type', 'studied_by', 'target_audience')
    inlines = [ChatMessageInline]


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'role', 'model', 'response_time_ms', 'created_at')
    list_filter = ('role', 'model')
    search_fields = ('content',)


@admin.register(LegacyChatHistory)
class LegacyChatHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'model', 'is_favorite', 'created_at')
    search_fields = ('query', 'response')


@admin.register(TieupLead)
class TieupLeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'category', 'contact_person', 'contact_email', 'is_partner', 'compatibility_score', 'anti_spam_status')
    list_filter = ('country', 'category', 'is_partner', 'anti_spam_status')
    search_fields = ('name', 'country', 'contact_person', 'contact_email', 'location_main')


@admin.register(TieupPolicy)
class TieupPolicyAdmin(admin.ModelAdmin):
    list_display = ('id', 'min_commission_percent', 'target_commission_percent', 'preferred_payment_terms', 'updated_at')


@admin.register(OutreachStatusLog)
class OutreachStatusLogAdmin(admin.ModelAdmin):
    list_display = ('institution_name', 'recipient_email', 'sender_email', 'status', 'spam_score', 'created_at')
    list_filter = ('status', 'phase')
    search_fields = ('institution_name', 'recipient_email', 'subject')


@admin.register(SmtpConfiguration)
class SmtpConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'host', 'port', 'sender_email', 'is_secure', 'is_active', 'sent_today')


@admin.register(AIProductPreset)
class AIProductPresetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'default_model', 'temperature', 'is_active')
    list_filter = ('is_active',)


@admin.register(GenerationJob)
class GenerationJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'job_type', 'status', 'progress', 'created_at', 'completed_at')
    list_filter = ('job_type', 'status')


@admin.register(SystemActivityLog)
class SystemActivityLogAdmin(admin.ModelAdmin):
    list_display = ('action_type', 'module', 'user_identifier', 'created_at')
    list_filter = ('module', 'action_type')


@admin.register(MetricSnapshot)
class MetricSnapshotAdmin(admin.ModelAdmin):
    list_display = ('metric_key', 'metric_value', 'recorded_at')
    list_filter = ('metric_key',)
