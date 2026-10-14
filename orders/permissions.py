from rest_framework import permissions


class IsAdminRole(permissions.BasePermission):
    """Checks our custom role field, not Django's is_staff — matches how
    the frontend decides whether to show /admin/* routes."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "admin"
        )
