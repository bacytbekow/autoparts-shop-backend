# apps/products/filters.py

from django_filters import rest_framework as filters
from .models import Product
from django.db import models

class ProductFilter(filters.FilterSet):
    category = filters.NumberFilter(field_name='categories__id')
    car = filters.NumberFilter(field_name='cars__id')
    price_min = filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = filters.NumberFilter(field_name='price', lookup_expr='lte')
    search = filters.CharFilter(method='filter_search')

    class Meta:
        model = Product
        fields = {
            'brand': ['exact'],
            'is_available': ['exact'],
            'is_popular': ['exact'],
            'is_new': ['exact'],
        }

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(name__icontains=value) |
            models.Q(article__icontains=value) |
            models.Q(manufacturer_code__icontains=value)
        )