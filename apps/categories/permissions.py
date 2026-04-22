# apps/categories/permissions.py

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrContentOrReadOnly(BasePermission):

    def has_permission(self, request, view):

        return request.user and request.user.is_authenticated and (
                request.user.role == 'admin' or
                request.user.role == 'content' or
                request.user.is_superuser
        )