# apps/product_images/permissions.py

from rest_framework.permissions import BasePermission


class IsAdminOrContent(BasePermission):
    """Только админ, контент, суперадмин могут управлять фото"""

    def has_permission(self, request, view):
        # GET могут все
        if request.method == 'GET':
            return True



        # POST, PUT, PATCH для админ, контент, суперадмин
        return request.user and request.user.is_authenticated and (
                request.user.role == 'admin' or
                request.user.role == 'content' or
                request.user.is_superuser
        )