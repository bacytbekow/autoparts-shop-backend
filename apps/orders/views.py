# apps/orders/views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderCreateSerializer, OrderStatusUpdateSerializer
from .permissions import IsOwnerOrManager
from apps.products.models import Product


class OrderCreateView(APIView):
    """Создание заказа"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        data = serializer.validated_data

        items_data = []

        # Если пользователь авторизован - берем из корзины
        if user.is_authenticated and hasattr(user, 'cart'):
            cart_items = user.cart.items.all()

            # ПРОВЕРКА: корзина не пустая
            if not cart_items.exists():
                return Response(
                    {'error': 'Корзина пуста. Добавьте товары перед оформлением заказа'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            for cart_item in cart_items:
                items_data.append({
                    'product': cart_item.product,
                    'quantity': cart_item.quantity,
                    'price': cart_item.product.price
                })
        else:
            # Гость - берем из запроса
            items = data.get('items', [])

            # ПРОВЕРКА: есть товары в запросе
            if not items:
                return Response(
                    {'error': 'Не указаны товары для заказа'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            for item in items:
                try:
                    product = Product.objects.get(id=item['product_id'])
                    items_data.append({
                        'product': product,
                        'quantity': item['quantity'],
                        'price': product.price
                    })
                except Product.DoesNotExist:
                    return Response(
                        {'error': f'Товар с id={item["product_id"]} не найден'},
                        status=status.HTTP_404_NOT_FOUND
                    )

        # Создаем заказ
        order = Order.objects.create(
            user=user,
            name=data['name'],
            phone=data['phone'],
            email=data.get('email', ''),
            address=data['address'],
            comment=data.get('comment', ''),
            total_price=0
        )

        total_price = 0
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            price = item_data['price']

            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                product_article=product.article,
                price=price,
                quantity=quantity
            )
            total_price += price * quantity

        order.total_price = total_price
        order.save()

        # Очищаем корзину после успешного заказа
        if user.is_authenticated and hasattr(user, 'cart'):
            user.cart.items.all().delete()

        return Response({
            'message': f'Заказ #{order.id} успешно создан',
            'order': OrderSerializer(order).data
        }, status=status.HTTP_201_CREATED)


class OrderListView(generics.ListAPIView):
    """Список заказов пользователя"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrManager]
    action = 'list'

    def get_queryset(self):
        user = self.request.user
        if user.role in ['manager', 'admin'] or user.is_superuser:
            return Order.objects.all()
        return Order.objects.filter(user=user)


class OrderAllListView(generics.ListAPIView):
    """Все заказы (только менеджер+)"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrManager]
    action = 'list_all'

    def get_queryset(self):
        return Order.objects.all()


class OrderDetailView(generics.RetrieveAPIView):
    """Детали заказа"""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrManager]
    lookup_field = 'id'


class OrderStatusUpdateView(APIView):
    """Обновление статуса заказа (только менеджер+)"""
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, order_id):
        user = request.user
        if user.role not in ['manager', 'admin'] and not user.is_superuser:
            return Response(
                {'error': 'У вас нет прав на изменение статуса заказа'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Заказ не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = OrderStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order.status = serializer.validated_data['status']
        order.save()

        return Response({
            'message': f'Статус заказа #{order.id} изменён на "{order.get_status_display()}"',
            'order': OrderSerializer(order).data
        }, status=status.HTTP_200_OK)