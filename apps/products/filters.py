# apps/products/filters.py
from django_filters import rest_framework as filters
from .models import Product
from django.db import models


class ProductFilter(filters.FilterSet):
    # Категория
    category = filters.NumberFilter(field_name='categories__id')
    category_slug = filters.CharFilter(field_name='categories__slug', lookup_expr='exact')

    # Бренд
    brand = filters.NumberFilter(field_name='brand__id')
    brand_slug = filters.CharFilter(field_name='brand__slug', lookup_expr='exact')

    # Автомобиль
    car = filters.NumberFilter(field_name='cars__id')
    car_make = filters.CharFilter(field_name='cars__make', lookup_expr='exact')
    car_model = filters.CharFilter(field_name='cars__model', lookup_expr='exact')
    car_year = filters.NumberFilter(field_name='cars__year_from', lookup_expr='exact')

    # Баа
    price_min = filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = filters.NumberFilter(field_name='price', lookup_expr='lte')

    # Статус
    is_available = filters.BooleanFilter(field_name='is_available')
    is_popular = filters.BooleanFilter(field_name='is_popular')
    is_new = filters.BooleanFilter(field_name='is_new')
    is_active = filters.BooleanFilter(field_name='is_active')

    # ✅ Издөө (search)
    search = filters.CharFilter(method='filter_search')

    class Meta:
        model = Product
        fields = []

    def filter_search(self, queryset, name, value):
        search_term = value.strip()
        if not search_term:
            return queryset

        return queryset.filter(
            models.Q(name__icontains=search_term) |
            models.Q(article__icontains=search_term) |
            models.Q(manufacturer_code__icontains=search_term) |
            models.Q(brand__name__icontains=search_term) |
            models.Q(categories__name__icontains=search_term)
        ).distinct()