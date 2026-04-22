from rest_framework import serializers
from .models import Car


class CarCreateUpdateSerializer(serializers.ModelSerializer):
    """Создание и обновление автомобиля"""

    class Meta:
        model = Car
        fields = ['id', 'brand', 'model', 'generation', 'year_from', 'year_to',
                  'engine', 'body_type', 'is_active', 'meta_title', 'meta_description']

class CarListSerializer(serializers.ModelSerializer):
    """Для списка автомобилей (админ/контент)"""
    brand_name = serializers.CharField(source='brand.name', read_only=True)

    class Meta:
        model = Car
        fields = ['id', 'brand', 'brand_name', 'model', 'slug', 'generation',
                  'year_from', 'year_to', 'engine', 'body_type', 'is_active']


class CarPublicSerializer(serializers.ModelSerializer):
    """Для покупателей и гостей (только активные)"""
    brand_name = serializers.CharField(source='brand.name', read_only=True)

    class Meta:
        model = Car
        fields = ['id', 'brand', 'brand_name', 'model', 'slug', 'generation',
                  'year_from', 'year_to', 'engine', 'body_type']


class CarDetailSerializer(serializers.ModelSerializer):
    """Детальный просмотр автомобиля (админ/контент)"""
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    created_by_info = serializers.SerializerMethodField()
    updated_by_info = serializers.SerializerMethodField()

    class Meta:
        model = Car
        fields = ['id', 'brand', 'brand_name', 'model', 'slug', 'generation',
                  'year_from', 'year_to', 'engine', 'body_type', 'is_active',
                  'meta_title', 'meta_description', 'created_at', 'updated_at',
                  'created_by_info', 'updated_by_info']

    def get_created_by_info(self, obj):
        if obj.created_by:
            return {
                'id': obj.created_by.id,
                'username': obj.created_by.username
            }
        return None

    def get_updated_by_info(self, obj):
        if obj.updated_by:
            return {
                'id': obj.updated_by.id,
                'username': obj.updated_by.username
            }
        return None

