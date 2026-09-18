from rest_framework import serializers
from .models import Car
from django.utils.text import slugify

class CarCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ['id', 'make', 'model', 'generation', 'year_from', 'year_to',
                  'engine', 'body_type', 'is_active', 'meta_title', 'meta_description']

    def create(self, validated_data):
        # Генерируем slug автоматически
        make = validated_data.get('make')
        model = validated_data.get('model')
        generation = validated_data.get('generation', '')

        slug_str = f"{make} {model} {generation}".strip()
        base_slug = slugify(slug_str)
        slug = base_slug
        counter = 1

        # Проверяем уникальность
        while Car.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        validated_data['slug'] = slug
        return super().create(validated_data)

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
        fields = ['id', 'make', 'brand_name', 'model', 'slug', 'generation',
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

