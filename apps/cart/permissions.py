# apps/cart/permissions.py

from rest_framework.permissions import BasePermission


class IsAuthenticatedOrReadOnly(BasePermission):
    """
    - GET: могут все (но данные только свои)
    - POST, PUT, DELETE: только авторизованные
    """

    def has_permission(self, request, view):
        # POST, PUT, DELETE только для авторизованных
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            return request.user and request.user.is_authenticated

        # GET могут все
        return True

    def has_object_permission(self, request, view, obj):
        # Проверяем, что корзина принадлежит пользователю
        return obj.user == request.user