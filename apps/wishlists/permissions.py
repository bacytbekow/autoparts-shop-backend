# apps/wishlists/permissions.py

from rest_framework.permissions import BasePermission


class IsOwnerOrAdmin(BasePermission):
    """Пользователь видит только свои избранные, админ - все"""

    def has_permission(self, request, view):
        # Для списка избранных - только авторизованные
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Админ может всё
        if request.user.role == 'admin' or request.user.is_superuser:
            return True

        # Обычный пользователь видит только свои избранные
        return obj.user == request.user