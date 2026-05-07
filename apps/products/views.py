# apps/products/views.py
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Product
from .serializers import *
from .permissions import IsAdminOrContent


class ProductCreateView(generics.CreateAPIView):
    """Создание товара"""
    serializer_class = ProductCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrContent]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            'message': f'Товар "{serializer.instance.name}" успешно создан',
            'product': serializer.data
        }, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user
        )


class ProductListView(generics.ListAPIView):
    """Список товаров"""
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        user = self.request.user
        if user.is_authenticated and (user.role in ['admin', 'content'] or user.is_superuser):
            return ProductListSerializer
        return ProductPublicSerializer

    def get_serializer_context(self):  # ← добавить
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and (user.role in ['admin', 'content'] or user.is_superuser):
            return Product.objects.all()
        return Product.objects.filter(is_active=True)



@extend_schema(
        methods=['DELETE'],
        parameters=[
            OpenApiParameter(
                name='hard',
                description='Полное удаление из БД (hard=true) или мягкое (по умолчанию)',
                required=False,
                type=str,
                default='false'
            )
        ],
        responses={
            200: {'description': 'Товар скрыт или удалён'},
            403: {'description': 'Нет прав'},
            404: {'description': 'Товар не найден'},
        }
    )
class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Детали, редактирование, удаление товара"""
    queryset = Product.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdminOrContent]
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProductDetailSerializer
        return ProductCreateUpdateSerializer

    def get_queryset(self):
        return Product.objects.all()

    def get_serializer_context(self):  # ← добавить
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def update(self, request, *args, **kwargs):
        """Обновление товара с проверкой прав"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        user = request.user

        # Контент может редактировать только свои товары
        if user.role == 'content' and instance.created_by != user:
            return Response(
                {'error': 'Вы можете редактировать только свои товары'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=user)

        return Response({
            'message': f'Товар "{instance.name}" успешно обновлён',
            'product': serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        user = request.user
        instance = self.get_object()

        # Полное удаление (hard) - только админ, суперадмин
        if request.query_params.get('hard') == 'true':
            if user.role != 'admin' and not user.is_superuser:
                return Response(
                    {'error': 'Только администраторы могут полностью удалять товары'},
                    status=status.HTTP_403_FORBIDDEN
                )
            instance.delete()
            return Response(
                {'message': f'Товар "{instance.name}" полностью удалён из БД'},
                status=status.HTTP_200_OK
            )

        # Мягкое удаление (скрыть) - контент может только свои
        if user.role == 'content':
            if instance.created_by != user:
                return Response(
                    {'error': 'Вы можете скрывать только свои товары'},
                    status=status.HTTP_403_FORBIDDEN
                )
            instance.is_active = False
            instance.save()
            return Response(
                {'message': f'Товар "{instance.name}" скрыт'},
                status=status.HTTP_200_OK
            )

        # Админ и суперадмин могут скрывать любые
        instance.is_active = False
        instance.save()
        return Response(
            {'message': f'Товар "{instance.name}" скрыт'},
            status=status.HTTP_200_OK
        )
