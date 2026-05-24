from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Cart, CartItem
from .serializers import CartSerializer, CartAddSerializer, CartUpdateSerializer
from .permissions import IsAuthenticatedOrReadOnly
from apps.products.models import Product

class CartView(APIView):
    """Получить корзину"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CartAddView(APIView):
    """Добавить товар в корзину"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CartAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Товар не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        cart, _ = Cart.objects.get_or_create(user=request.user)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return Response({
            'message': f'Товар "{product.name}" добавлен в корзину',
            'quantity': cart_item.quantity,
            'cart_item_id': cart_item.id
        }, status=status.HTTP_200_OK)


class CartUpdateView(APIView):
    """Обновить количество товара в корзине"""
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, item_id):
        serializer = CartUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        quantity = serializer.validated_data['quantity']

        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Товар не найден в корзине'},
                status=status.HTTP_404_NOT_FOUND
            )

        cart_item.quantity = quantity
        cart_item.save()

        return Response({
            'message': f'Количество товара "{cart_item.product.name}" обновлено',
            'quantity': cart_item.quantity
        }, status=status.HTTP_200_OK)


class CartRemoveView(APIView):
    """Удалить товар из корзины"""
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, item_id):
        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
            product_name = cart_item.product.name
            cart_item.delete()
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Товар не найден в корзине'},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response({
            'message': f'Товар "{product_name}" удален из корзины'
        }, status=status.HTTP_200_OK)


class CartClearView(APIView):
    """Очистить корзину"""
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        CartItem.objects.filter(cart__user=request.user).delete()
        return Response({
            'message': 'Корзина очищена'
        }, status=status.HTTP_200_OK)