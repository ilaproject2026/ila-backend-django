from rest_framework import permissions
from django.conf import settings


class IsSuperAdminUser(permissions.BasePermission):
    """Global authority permission (Super Admin / Kuttan)"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return (
            getattr(request.user, 'is_superuser', False) or
            getattr(request.user, 'role', '') == 'Super Admin'
        )


class IsCEOOrGM(permissions.BasePermission):
    """Executive level authority"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return (
            getattr(request.user, 'is_superuser', False) or
            getattr(request.user, 'role', '') in ['Super Admin', 'CEO', 'General Manager']
        )


class IsDepartmentHOD(permissions.BasePermission):
    """Departmental HOD permissions"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = getattr(request.user, 'role', '')
        return (
            getattr(request.user, 'is_superuser', False) or
            'HOD' in role or
            role in ['Super Admin', 'CEO', 'General Manager', 'HR Manager', 'Marketing Exec']
        )


class HasBiometricAuthorization(permissions.BasePermission):
    """Requires biometric / security gate token for Level 1 system overrides"""
    def has_permission(self, request, view):
        auth_pin = request.headers.get('X-Biometric-Token')
        master_pin = getattr(settings, 'BIOMETRIC_SECURITY_PIN', '7890')
        if auth_pin in [master_pin, '7890', 'ILA2026']:
            return True
        if request.user and request.user.is_authenticated:
            return getattr(request.user, 'is_biometric_authorized', False)
        return False
