# apps/product_images/serializers.py

from rest_framework import serializers
from .models import ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра фото"""
    created_by_info = serializers.SerializerMethodField()
    updated_by_info = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'image', 'alt_text', 'is_main', 'order',
                  'created_at', 'updated_at', 'created_by_info', 'updated_by_info']
        read_only_fields = ['id', 'created_at', 'updated_at']

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


class ProductImageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'image', 'alt_text', 'is_main', 'order']

    def validate(self, data):
        product = data.get('product')
        is_main = data.get('is_main', False)

        if is_main:
            # Проверяем, есть ли уже главное фото у этого товара
            if ProductImage.objects.filter(product=product, is_main=True).exists():
                raise serializers.ValidationError(
                    f'У товара "{product.name}" уже есть главное фото. '
                    'Сначала снимите отметку с существующего главного фото.'
                )
        return data