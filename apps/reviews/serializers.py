# apps/reviews/serializers.py

from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'product', 'product_name', 'user', 'user_name',
                  'rating', 'text', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')

        # Показываем status только если:
        # 1. Это свой отзыв (покупатель)
        # 2. Или пользователь админ/контент
        if request and request.user.is_authenticated:
            if (request.user == instance.user) or (
                    request.user.role in ['admin', 'content'] or request.user.is_superuser):
                data['status'] = instance.status

        return data

class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['product', 'rating', 'text']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Оценка должна быть от 1 до 5")
        return value