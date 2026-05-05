# apps/cart/serializers.py

from rest_framework import serializers
from .models import Cart, CartItem
from apps.products.serializers import ProductPublicSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product_info = ProductPublicSerializer(source='product', read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_info', 'quantity', 'total_price', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    item_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price', 'item_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CartAddSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)


class CartUpdateSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)