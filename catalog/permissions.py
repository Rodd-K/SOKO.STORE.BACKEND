from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Anyone can GET. Only authenticated users with role == 'admin' can
    create, update, or delete — matches the /admin/* frontend routes
    being gated the same way."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "admin"
        )
