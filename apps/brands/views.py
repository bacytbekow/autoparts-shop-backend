# apps/brands/views.py
from rest_framework import generics, permissions, status
from rest_framework import generics, permissions
from .models import Brand
from .serializers import *
from .permissions import *
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
class BrandListView(generics.ListAPIView):
    """Список брендов"""
    permission_classes = [permissions.AllowAny, ]

    def get_serializer_class(self):
        user = self.request.user

        # Админ, контент, суперадмин видят все бренды (с is_active)
        if user.is_authenticated and (user.role in ['admin', 'content'] or user.is_superuser):
            return BrandListSerializer

        # Гости и покупатели видят только активные бренды (без is_active)
        return BrandPublicSerializer

    def get_queryset(self):
        user = self.request.user

        # Админ, контент, суперадмин видят все бренды
        if user.is_authenticated and (user.role in ['admin', 'content'] or user.is_superuser):
            return Brand.objects.all()

        # Гости и покупатели видят только активные
        return Brand.objects.filter(is_active=True)


class BrandCreateView(generics.CreateAPIView):
    """Создание бренда"""
    serializer_class = BrandCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrContent]

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            'message': f'Бренд "{serializer.instance.name}" успешно создан',
            'brand': serializer.data
        }, status=status.HTTP_201_CREATED)

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
        200: {
            'description': 'Мягкое удаление: бренд скрыт (is_active=False). Полное удаление: бренд удалён из БД'
        },
        403: {
            'description': 'Нет прав (контент-менеджер не может удалять)'
        },
        404: {
            'description': 'Бренд не найден'
        },
    }
)
class BrandDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Детали, редактирование, удаление бренда"""
    queryset = Brand.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdminOrContent]
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BrandDetailSerializer
        return BrandCreateUpdateSerializer

    def get_queryset(self):
        user = self.request.user
        # Все авторизованные видят все бренды (проверки прав в update/delete)
        return Brand.objects.all()

    def update(self, request, *args, **kwargs):
        """Обновление бренда с проверкой прав"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        user = request.user

        # Контент может редактировать только свои бренды
        if user.role == 'content' and instance.created_by != user:
            return Response(
                {'error': 'Вы можете редактировать только свои бренды'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=user)

        return Response({
            'message': f'Бренд "{instance.name}" успешно обновлён',
            'brand': serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """Удаление бренда"""
        user = request.user
        instance = self.get_object()

        # Полное удаление (hard) - только админ, суперадмин
        if request.query_params.get('hard') == 'true':
            if user.role != 'admin' and not user.is_superuser:
                return Response(
                    {'error': 'Только администраторы могут полностью удалять бренды'},
                    status=status.HTTP_403_FORBIDDEN
                )
            instance.delete()
            return Response(
                {'message': f'Бренд "{instance.name}" полностью удалён из БД'},
                status=status.HTTP_200_OK
            )

        # Мягкое удаление (скрыть) - контент может только свои
        if user.role == 'content':
            if instance.created_by != user:
                return Response(
                    {'error': 'Вы можете скрывать только свои бренды'},
                    status=status.HTTP_403_FORBIDDEN
                )
            instance.is_active = False
            instance.save()
            return Response(
                {'message': f'Бренд "{instance.name}" скрыт'},
                status=status.HTTP_200_OK
            )

        # Админ и суперадмин могут скрывать любые
        instance.is_active = False
        instance.save()
        return Response(
            {'message': f'Бренд "{instance.name}" скрыт'},
            status=status.HTTP_200_OK
        )