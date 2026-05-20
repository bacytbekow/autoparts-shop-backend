# apps/core/permissions.py
from rest_framework import permissions


class IsAdminOrSuperuser(permissions.BasePermission):
    """Только admin или superuser могут изменять, читать могут все"""

    def has_permission(self, request, view):
        # GET запросы разрешены всем
        if request.method == 'GET':
            return True

        # POST, PUT, PATCH, DELETE - только для admin/superuser
        if not request.user.is_authenticated:
            return False

        # Проверяем роль пользователя
        return request.user.role == 'admin' or request.user.is_superuser