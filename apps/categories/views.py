# apps/categories/views.py
from django.core.cache import cache
from rest_framework import permissions
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .serializers import *
from .permissions import IsAdminOrContentOrReadOnly


class CategoryCreateView(generics.CreateAPIView):
    """Создание категории"""
    serializer_class = CategoryCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrContentOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def perform_create(self, serializer):
        # Очищаем кэш корневых категорий
        cache.delete('root_categories')
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user
        )

    def create(self, request, *args, **kwargs):
        print("=== ДАННЫЕ ЗАПРОСА ===")
        print("FILES:", request.FILES)
        print("DATA:", request.data)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Сохраняем и получаем категорию
        category = serializer.save()

        return Response({
            'message': f'Категория "{category.name}" успешно создана',
            'category': CategoryDetailSerializer(category).data
        }, status=status.HTTP_201_CREATED)

class CategoryListView(generics.ListAPIView):
    """Корневые категории с кэшированием"""
    serializer_class = CategoryListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Category.objects.filter(parent__isnull=True, is_active=True)

    def list(self, request, *args, **kwargs):
        """Получение категорий с кэшированием"""
        cache_key = 'root_categories'

        # Пытаемся взять из кэша
        cached_data = cache.get(cache_key)

        if cached_data:
            print("✅ Категории из Redis кэша")
            return Response(cached_data)

        print("📡 Категории из базы данных")

        # Если нет в кэше - берем из БД
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        # Сохраняем в кэш на 1 час
        cache.set(cache_key, data, 3600)

        return Response(data)


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
        200: {'description': 'Категория скрыта или удалена'},
        400: {'description': 'Ошибка: есть дочерние категории'},
        403: {'description': 'Нет прав'},
    }
)
class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Получение, обновление, удаление категории по id"""
    queryset = Category.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdminOrContentOrReadOnly]
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CategoryDetailSerializer
        return CategoryCreateUpdateSerializer

    def get_queryset(self):
        return Category.objects.all()

    def update(self, request, *args, **kwargs):
        """Обновление с проверкой прав"""
        user = request.user
        instance = self.get_object()

        if user.role == 'content' and instance.created_by != user:
            return Response(
                {'error': 'Вы можете редактировать только свои категории'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Очищаем кэш корневых категорий
        cache.delete('root_categories')

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """Удаление категории с проверкой прав"""
        user = request.user
        instance = self.get_object()

        # Полное удаление (hard)
        if request.query_params.get('hard') == 'true':
            if user.role == 'content':
                return Response(
                    {'error': 'Контент-менеджер не может полностью удалять категории'},
                    status=status.HTTP_403_FORBIDDEN
                )

            if instance.children.exists():
                return Response(
                    {'error': f'Сначала удалите или переместите дочерние категории (их {instance.children.count()})'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Очищаем кэш
            cache.delete('root_categories')
            instance.delete()
            return Response(
                {'message': f'Категория "{instance.name}" полностью удалена'},
                status=status.HTTP_200_OK
            )

        # Мягкое удаление (скрыть) - контент может только свои
        if user.role == 'content':
            if instance.created_by != user:
                return Response(
                    {'error': 'Вы можете скрывать только свои категории'},
                    status=status.HTTP_403_FORBIDDEN
                )
            # Очищаем кэш
            cache.delete('root_categories')
            instance.is_active = False
            instance.save()
            return Response(
                {'message': f'Категория "{instance.name}" скрыта'},
                status=status.HTTP_200_OK
            )

        # Админ и суперадмин могут скрывать любые
        cache.delete('root_categories')
        instance.is_active = False
        instance.save()
        return Response(
            {'message': f'Категория "{instance.name}" скрыта'},
            status=status.HTTP_200_OK
        )