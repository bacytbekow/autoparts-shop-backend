# apps/products/views.py
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Product
from django.db.models import Prefetch, Exists, OuterRef, Value, BooleanField
from .serializers import *
from .permissions import IsAdminOrContent
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .filters import ProductFilter
from django.db.models import Exists, OuterRef, Value, BooleanField
from apps.product_images.models import ProductImage
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.db import connections
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
    serializer_class = ProductPublicSerializer
    permission_classes = [permissions.AllowAny]

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ProductFilter
    ordering_fields = ['price', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        user = self.request.user
        if user.is_authenticated and (user.role in ['admin', 'content'] or user.is_superuser):
            return ProductListSerializer
        return ProductPublicSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        user = self.request.user
        queryset = Product.objects.all()

        # Оптимизация: загружаем фото одним запросом
        queryset = queryset.prefetch_related(
            Prefetch('images', queryset=ProductImage.objects.all())
        )

        # Оптимизация: добавляем флаг избранного одним запросом
        if user.is_authenticated:
            queryset = queryset.annotate(
                is_favorite=Exists(
                    Wishlist.objects.filter(user=user, product=OuterRef('pk'))
                )
            )
        else:
            queryset = queryset.annotate(is_favorite=Value(False, output_field=BooleanField()))

        # Фильтр по активности для не-админов
        if not (user.is_authenticated and (user.role in ['admin', 'content'] or user.is_superuser)):
            queryset = queryset.filter(is_active=True)

        # ✅ SEARCH - базага жараша
        search_term = self.request.query_params.get('search')
        if search_term:
            db_engine = connections['default'].vendor

            if db_engine == 'postgresql':
                # PostgreSQL үчүн (unaccent + icontains)
                queryset = queryset.filter(
                    Q(name__unaccent__icontains=search_term) |
                    Q(article__unaccent__icontains=search_term) |
                    Q(manufacturer_code__unaccent__icontains=search_term) |
                    Q(brand__name__unaccent__icontains=search_term) |
                    Q(categories__name__unaccent__icontains=search_term)
                ).distinct()
            else:
                # SQLite жана башкалар үчүн
                queryset = queryset.filter(
                    Q(name__icontains=search_term) |
                    Q(article__icontains=search_term) |
                    Q(manufacturer_code__icontains=search_term) |
                    Q(brand__name__icontains=search_term) |
                    Q(categories__name__icontains=search_term)
                ).distinct()

        return queryset

    def list(self, request, *args, **kwargs):
        # КЭШ
        user = request.user
        cache_key = f"products_list_{user.id if user.is_authenticated else 'anon'}_{hash(frozenset(request.GET.items()))}"

        cached_response = cache.get(cache_key)
        if cached_response:
            return Response(cached_response)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, 60)

        return response
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
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsAdminOrContent()]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            user = self.request.user
            if user.is_authenticated and (user.role in ['admin', 'content'] or user.is_superuser):
                return ProductDetailAdminSerializer
            return ProductDetailPublicSerializer
        return ProductCreateUpdateSerializer

    def get_object(self):
        lookup = self.kwargs.get('slug')
        if lookup and lookup.isdigit():
            return get_object_or_404(Product, id=lookup)
        return get_object_or_404(Product, slug=lookup)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def retrieve(self, request, *args, **kwargs):
        """Кэш менен деталды алуу"""
        instance = self.get_object()
        cache_key = f"product_detail_{instance.slug}"

        # Кэштен алуу
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        # Кэш жок
        serializer = self.get_serializer(instance)
        data = serializer.data

        # Кэшке сактоо (5 минут)
        cache.set(cache_key, data, 300)

        return Response(data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        user = request.user

        if user.role == 'content' and instance.created_by != user:
            return Response(
                {'error': 'Вы можете редактировать только свои товары'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=user)

        # ✅ Кэшти тазалоо
        cache.delete(f"product_detail_{instance.slug}")
        cache.delete_pattern("products_list_*")

        return Response({
            'message': f'Товар "{instance.name}" успешно обновлён',
            'product': serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        user = request.user
        instance = self.get_object()

        if request.query_params.get('hard') == 'true':
            if user.role != 'admin' and not user.is_superuser:
                return Response(
                    {'error': 'Только администраторы могут полностью удалять товары'},
                    status=status.HTTP_403_FORBIDDEN
                )
            cache.delete(f"product_detail_{instance.slug}")
            cache.delete_pattern("products_list_*")
            instance.delete()
            return Response({
                'message': f'Товар "{instance.name}" полностью удалён из БД'},
                status=status.HTTP_200_OK
            )

        if user.role == 'content' and instance.created_by != user:
            return Response(
                {'error': 'Вы можете скрывать только свои товары'},
                status=status.HTTP_403_FORBIDDEN
            )

        instance.is_active = False
        instance.save()

        # ✅ Кэшти тазалоо
        cache.delete(f"product_detail_{instance.slug}")
        cache.delete_pattern("products_list_*")

        return Response({
            'message': f'Товар "{instance.name}" скрыт'},
            status=status.HTTP_200_OK
        )