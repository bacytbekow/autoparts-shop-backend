# apps/brands/serializers.py

from rest_framework import serializers
from .models import Brand


class BrandListSerializer(serializers.ModelSerializer):
    """Для списка брендов (админ/контент)"""
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'logo', 'country', 'is_active', 'order']


class BrandPublicSerializer(serializers.ModelSerializer):
    """Для покупателей и гостей (только активные)"""
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'logo', 'country']



class BrandDetailSerializer(serializers.ModelSerializer):
    created_by_info = serializers.SerializerMethodField()
    updated_by_info = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'logo', 'description', 'country',
                  'is_active', 'order', 'meta_title', 'meta_description',
                  'created_at', 'updated_at', 'created_by_info', 'updated_by_info']

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


class BrandCreateUpdateSerializer(serializers.ModelSerializer):
    """Создание и обновление бренда"""
    class Meta:
        model = Brand
        fields = ['id', 'name', 'description', 'logo', 'country', 'order',
                  'is_active', 'meta_title', 'meta_description']