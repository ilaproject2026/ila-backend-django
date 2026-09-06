from rest_framework.permissions import BasePermission


class IsUserAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

class IsSuperUserAuthenticated(BasePermission):
    def has_permission(self, request, view):
        user = request.user 
        return bool(user and user.is_authenticated and user.is_superuser)


class IsStaffUserAuthenticated(BasePermission):
    """
    Allows access only to authenticated staff or admin users.
    """
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and (user.is_staff or user.is_admin or user.is_superuser))