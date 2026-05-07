# apps/wishlists/serializers.py

from rest_framework import serializers
from .models import Wishlist
from apps.products.serializers import ProductPublicSerializer


class WishlistSerializer(serializers.ModelSerializer):
    product_info = ProductPublicSerializer(source='product', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'user_name', 'product', 'product_info', 'created_at']
        read_only_fields = ['id', 'created_at', 'user']


class WishlistCreateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()