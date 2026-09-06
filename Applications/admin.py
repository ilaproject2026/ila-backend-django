from django.contrib import admin
from Applications.Authentication.auth_admin import *
from Applications.Authentication.auth_models import FranchisePartner, AuditLog


# --- Global Authentication Extras ---
@admin.register(FranchisePartner)
class FranchisePartnerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'region', 'partner_token', 'created_at')
    search_fields = ('name', 'email', 'region', 'partner_token')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'department', 'category', 'action', 'timestamp')
    list_filter = ('category', 'department')
    search_fields = ('action', 'details', 'ip_address')
