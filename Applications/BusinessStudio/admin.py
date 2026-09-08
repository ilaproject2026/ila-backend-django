from django.contrib import admin
from .StudioCore.studiocore_models import Application, PackageTier, ChatMessageLog


# --- BusinessStudio: Applications ---
@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'business_name', 'industry', 'package_option', 'status', 'created_at')
    list_filter = ('status', 'package_option', 'industry')
    search_fields = ('full_name', 'email', 'business_name')
    readonly_fields = ('created_at', 'updated_at')


# --- BusinessStudio: Package Tiers ---
@admin.register(PackageTier)
class PackageTierAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'setup_fee', 'ownership', 'highlight', 'display_order', 'is_active')
    list_filter = ('is_active', 'highlight')
    list_editable = ('display_order', 'is_active', 'highlight')
    prepopulated_fields = {'slug': ('name',)}


# --- BusinessStudio: Chat Logs ---
@admin.register(ChatMessageLog)
class ChatMessageLogAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'model_used', 'ip_address', 'created_at')
    list_filter = ('model_used', 'created_at')
    search_fields = ('prompt', 'response', 'session_id')
    readonly_fields = ('created_at',)
