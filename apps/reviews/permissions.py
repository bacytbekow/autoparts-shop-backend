# apps/reviews/permissions.py

from rest_framework.permissions import BasePermission


class IsOwnerOrAdmin(BasePermission):
    """Пользователь может редактировать только свои отзывы, админ - все"""

    def has_object_permission(self, request, view, obj):
        # Админ/суперадмин могут всё
        if request.user.role == 'admin' or request.user.is_superuser:
            return True

        # Обычный пользователь может редактировать/удалять только свои отзывы
        return obj.user == request.user


class IsAdminOrContent(BasePermission):
    """Для управления статусами отзывов"""

    def has_permission(self, request, view):
        # Модерация отзывов только для админа/контента
        # Убираем проверку view.action
        return request.user and request.user.is_authenticated and (
                request.user.role == 'admin' or
                request.user.role == 'content' or
                request.user.is_superuser
        )