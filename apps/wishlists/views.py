# apps/wishlists/views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Wishlist
from .serializers import WishlistSerializer, WishlistCreateSerializer
from .permissions import IsOwnerOrAdmin
from apps.products.models import Product


class WishlistListView(generics.ListAPIView):
    """Список избранных товаров пользователя"""
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)


class WishlistAddView(APIView):
    """Добавить товар в избранное"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = WishlistCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data['product_id']

        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Товар не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )

        if created:
            message = f'Товар "{product.name}" добавлен в избранное'
        else:
            message = f'Товар "{product.name}" уже в избранном'

        return Response({
            'message': message,
            'is_favorite': True
        }, status=status.HTTP_200_OK)


class WishlistRemoveView(APIView):
    """Удалить товар из избранного"""
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, product_id):
        try:
            wishlist_item = Wishlist.objects.get(user=request.user, product_id=product_id)
            product_name = wishlist_item.product.name
            wishlist_item.delete()
        except Wishlist.DoesNotExist:
            return Response(
                {'error': 'Товар не найден в избранном'},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response({
            'message': f'Товар "{product_name}" удалён из избранного',
            'is_favorite': False
        }, status=status.HTTP_200_OK)

