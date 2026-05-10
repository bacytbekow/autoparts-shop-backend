# apps/categories/views.py
from rest_framework import permissions
from rest_framework import generics
from .serializers import *
from .permissions import IsAdminOrContentOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema, OpenApiParameter


class CategoryCreateView(generics.CreateAPIView):
    """Создание категории"""
    serializer_class = CategoryCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrContentOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]  # ← добавить

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user
        )

    def create(self, request, *args, **kwargs):
        print("=== ДАННЫЕ ЗАПРОСА ===")
        print("FILES:", request.FILES)  # ← что приходит
        print("DATA:", request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            'message': f'Категория "{serializer.instance.name}" успешно создана',
            'category': serializer.data
        }, status=status.HTTP_201_CREATED)

# apps/categories/views.py

class CategoryListView(generics.ListAPIView):
    """Список категорий"""
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        user = self.request.user

        # Админ, контент, суперадмин видят поле is_active
        if user.is_authenticated and (user.role in ['admin', 'content'] or user.is_superuser):
            return CategoryListSerializer  # с is_active

        # Гости и покупатели видят только публичные поля
        return CategoryPublicSerializer  # без is_active

    def get_queryset(self):
        user = self.request.user

        # Админ, контент, суперадмин видят все категории
        if user.is_authenticated and (user.role in ['admin', 'content'] or user.is_superuser):
            return Category.objects.filter(parent__isnull=True)

        # Гости и покупатели видят только активные
        return Category.objects.filter(parent__isnull=True, is_active=True)



@extend_schema(
    methods=['DELETE'],
    parameters=[  # ← квадратные скобки!
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

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=user)

        return Response(serializer.data, status=status.HTTP_200_OK)


    def destroy(self, request, *args, **kwargs):  # ← декоратор прямо над методом
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
            instance.is_active = False
            instance.save()
            return Response(
                {'message': f'Категория "{instance.name}" скрыта'},
                status=status.HTTP_200_OK
            )

        # Админ и суперадмин могут скрывать любые
        instance.is_active = False
        instance.save()
        return Response(
            {'message': f'Категория "{instance.name}" скрыта'},
            status=status.HTTP_200_OK
        )
