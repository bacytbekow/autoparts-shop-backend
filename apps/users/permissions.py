from rest_framework.permissions import BasePermission


# ========== ДЛЯ СПИСКОВ И CREATE =========

class OnlySuperAdmin(BasePermission):
    """Только суперадмин"""
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class AdminOrSuperAdmin(BasePermission):
    """Админ или суперадмин"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.role == 'admin' or request.user.is_superuser
        )


class ManagerAdminOrSuperAdmin(BasePermission):
    """Менеджер, админ или суперадмин"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.role == 'manager' or
            request.user.role == 'admin' or
            request.user.is_superuser
        )


# ========== ДЛЯ ДЕТАЛЕЙ =================

class SeeOwnOrAllByAdmin(BasePermission):
    """Обычный пользователь видит только себя, админ/суперадмин - всех"""
    def has_object_permission(self, request, view, obj):
        # Обычный пользователь (менеджер, контент, покупатель)
        if request.user.role in ['manager', 'content', 'customer']:
            return obj.id == request.user.id
        # Админ или суперадмин
        return request.user.is_superuser or request.user.role == 'admin'