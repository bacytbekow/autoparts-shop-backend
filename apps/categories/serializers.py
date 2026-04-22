
from rest_framework import serializers
from .models import Category


# для создать и изменить
class CategoryCreateUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image', 'parent', 'order',
                  'is_active', 'meta_title', 'meta_description']

# публичный
class CategoryPublicSerializer(serializers.ModelSerializer):
    """Для покупателей и гостей (только имя, фото и дети)"""
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image', 'children']

    def get_children(self, obj):
        children = obj.children.filter(is_active=True)
        return CategoryPublicSerializer(children, many=True).data


# apps/categories/serializers.py

class CategoryDetailSerializer(serializers.ModelSerializer):
    children = CategoryPublicSerializer(many=True, read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    created_by_info = serializers.SerializerMethodField()
    updated_by_info = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'parent', 'parent_name',
                  'children', 'is_active', 'order', 'meta_title', 'meta_description',
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


class CategoryListSerializer(serializers.ModelSerializer):
    """Для админов/контента (с is_active)"""
    children_count = serializers.IntegerField(source='children.count', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image', 'parent', 'is_active', 'order', 'children_count']