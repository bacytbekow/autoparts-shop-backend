# apps/orders/permissions.py

from rest_framework.permissions import BasePermission


class IsOwnerOrManager(BasePermission):
    """
    - Покупатель видит только свои заказы
    - Менеджер/админ/суперадмин видят все заказы
    """

    def has_permission(self, request, view):
        # GET /orders/all/ - только менеджер+
        if view.action == 'list_all':
            return request.user and request.user.is_authenticated and (
                    request.user.role == 'manager' or
                    request.user.role == 'admin' or
                    request.user.is_superuser
            )

        # Остальные запросы - только авторизованные
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Менеджер/админ/суперадмин могут всё
        if request.user.role in ['manager', 'admin'] or request.user.is_superuser:
            return True

        # Покупатель видит только свои заказы
        return obj.user == request.user