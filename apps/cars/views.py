from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Car
from .serializers import *
from .permissions import IsAdminOrContent



class CarCreateView(generics.CreateAPIView):
    serializer_class = CarCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrContent]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            'message': f'Автомобиль "{serializer.instance.make} {serializer.instance.model}" успешно создан',
            'car': {
                'id': serializer.instance.id,
                'make': serializer.instance.make,
                'model': serializer.instance.model,
                'slug': serializer.instance.slug,  # Добавим slug в ответ
                'generation': serializer.instance.generation,
                'year_from': serializer.instance.year_from,
                'year_to': serializer.instance.year_to,
            }
        }, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user
        )

class CarListView(generics.ListAPIView):
    """Список автомобилей"""
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        user = self.request.user
        if user.is_authenticated and (user.role in ['admin', 'content'] or user.is_superuser):
            return CarListSerializer
        return CarPublicSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and (user.role in ['admin', 'content'] or user.is_superuser):
            return Car.objects.all()
        return Car.objects.filter(is_active=True)

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
            'description': 'Мягкое удаление: автомобиль скрыт (is_active=False). Полное удаление: автомобиль удалён из БД'
        },
        403: {
            'description': 'Нет прав (контент-менеджер может скрывать только свои)'
        },
        404: {
            'description': 'Автомобиль не найден'
        },
    }
)
class CarDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Детали, редактирование, удаление автомобиля"""
    queryset = Car.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdminOrContent]
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CarDetailSerializer
        return CarCreateUpdateSerializer

    def get_queryset(self):
        return Car.objects.all()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        user = request.user

        if user.role == 'content' and instance.created_by != user:
            return Response(
                {'error': 'Вы можете редактировать только свои автомобили'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=user)

        return Response({
            'message': f'Автомобиль "{instance.brand.name} {instance.model}" успешно обновлён',
            'car': serializer.data
        }, status=status.HTTP_200_OK)

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
            200: {'description': 'Автомобиль скрыт или удалён'},
            403: {'description': 'Нет прав'},
            404: {'description': 'Автомобиль не найден'},
        }
    )
    def destroy(self, request, *args, **kwargs):
        user = request.user
        instance = self.get_object()

        if request.query_params.get('hard') == 'true':
            if user.role != 'admin' and not user.is_superuser:
                return Response(
                    {'error': 'Только администраторы могут полностью удалять автомобили'},
                    status=status.HTTP_403_FORBIDDEN
                )
            instance.delete()
            return Response(
                {'message': f'Автомобиль "{instance.brand.name} {instance.model}" полностью удалён из БД'},
                status=status.HTTP_200_OK
            )

        if user.role == 'content':
            if instance.created_by != user:
                return Response(
                    {'error': 'Вы можете скрывать только свои автомобили'},
                    status=status.HTTP_403_FORBIDDEN
                )
            instance.is_active = False
            instance.save()
            return Response(
                {'message': f'Автомобиль "{instance.brand.name} {instance.model}" скрыт'},
                status=status.HTTP_200_OK
            )

        instance.is_active = False
        instance.save()
        return Response(
            {'message': f'Автомобиль "{instance.brand.name} {instance.model}" скрыт'},
            status=status.HTTP_200_OK
        )


class CarMakesView(generics.ListAPIView):
    """GET /api/cars/makes/ - Бардык маркалардын тизмеси"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        makes = Car.objects.filter(is_active=True).values_list('make', flat=True).distinct().order_by('make')
        return Response(list(makes))


class CarModelsView(generics.ListAPIView):
    """GET /api/cars/models/?make=Toyota - Марка боюнча модельдердин тизмеси"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        make = request.GET.get('make')
        if not make:
            return Response({'error': 'make параметри керек'}, status=status.HTTP_400_BAD_REQUEST)

        models = Car.objects.filter(
            make=make,
            is_active=True
        ).values_list('model', flat=True).distinct().order_by('model')

        return Response(list(models))


class CarYearsView(generics.ListAPIView):
    """GET /api/cars/years/?make=Toyota&model=Camry - Модель боюнча жылдардын тизмеси"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        make = request.GET.get('make')
        model = request.GET.get('model')

        if not make or not model:
            return Response({'error': 'make жана model параметрлери керек'}, status=status.HTTP_400_BAD_REQUEST)

        years = Car.objects.filter(
            make=make,
            model=model,
            is_active=True,
            year_from__isnull=False
        ).values_list('year_from', flat=True).distinct().order_by('-year_from')

        return Response(list(years))