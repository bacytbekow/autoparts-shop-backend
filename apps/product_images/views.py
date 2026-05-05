from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import ProductImage
from .serializers import ProductImageSerializer, ProductImageCreateSerializer
from .permissions import IsAdminOrContent
from rest_framework.pagination import PageNumberPagination
import os
from django.conf import settings


class NoPagination(PageNumberPagination):
    page_size = None

class ProductImageCreateView(generics.CreateAPIView):
    """Загрузка фото для товара"""
    serializer_class = ProductImageCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrContent]

    def create(self, request, *args, **kwargs):
        # Проверяем, есть ли файл
        if 'image' not in request.FILES:
            return Response(
                {'error': 'Файл изображения не предоставлен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверка: если загружаем главное фото
        if request.data.get('is_main') == 'true':
            product_id = request.data.get('product')
            if product_id:
                # Убираем главное фото у других фото этого товара
                ProductImage.objects.filter(
                    product_id=product_id,
                    is_main=True
                ).update(is_main=False)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Сохраняем с текущим пользователем
        serializer.save(
            created_by=request.user,
            updated_by=request.user
        )

        return Response({
            'message': 'Фото успешно загружено',
            'image': serializer.data
        }, status=status.HTTP_201_CREATED)


class ProductImageListView(generics.ListAPIView):
    pagination_class = NoPagination
    """Список фото для товара"""
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        return ProductImage.objects.filter(product_id=product_id)


class ProductImageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Детали, редактирование, удаление фото"""
    queryset = ProductImage.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdminOrContent]
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProductImageSerializer
        return ProductImageCreateSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        user = request.user

        # Контент может редактировать только свои фото
        if user.role == 'content' and instance.created_by != user:
            return Response(
                {'error': 'Вы можете редактировать только свои фото'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Проверка: если пытаемся сделать фото главным
        if request.data.get('is_main') == True:
            # Убираем главное фото у других фото этого товара
            ProductImage.objects.filter(
                product=instance.product,
                is_main=True
            ).exclude(id=instance.id).update(is_main=False)

        # Сохраняем старый путь до обновления
        old_image_path = instance.image.path if instance.image else None

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=user)

        # Удаляем старый файл, если он был заменен
        new_image_path = instance.image.path if instance.image else None
        if old_image_path and old_image_path != new_image_path:
            if os.path.isfile(old_image_path):
                os.remove(old_image_path)

        return Response({
            'message': 'Фото успешно обновлено',
            'image': serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        user = request.user
        instance = self.get_object()

        if user.role == 'content' and instance.created_by != user:
            return Response(
                {'error': 'Вы можете удалять только свои фото'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Удаляем файл с диска
        if instance.image:
            if os.path.isfile(instance.image.path):
                os.remove(instance.image.path)

        instance.delete()
        return Response({
            'message': 'Фото успешно удалено'
        }, status=status.HTTP_200_OK)