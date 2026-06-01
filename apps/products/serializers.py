from rest_framework import serializers
from .models import Product
from apps.categories.serializers import CategoryPublicSerializer
from apps.brands.serializers import BrandPublicSerializer
from apps.cars.serializers import CarPublicSerializer
from apps.wishlists.models import Wishlist  # добавить импорт
from rest_framework import serializers
from .models import Product
from apps.wishlists.models import Wishlist

class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'article', 'manufacturer_code', 'brand',
                  'categories', 'cars', 'description', 'short_description',
                  'specifications', 'price', 'old_price', 'quantity',
                    'is_available', 'is_popular', 'is_new',
                  'is_active', 'meta_title', 'meta_description']
        extra_kwargs = {
            'name': {'required': True},
            'brand': {'required': True},
            'categories': {'required': True},
            'price': {'required': True},
            'quantity': {'required': False, 'default': 0},
        }

class ProductListSerializer(serializers.ModelSerializer):
    """Для списка товаров (админ/контент)"""
    brand_name = serializers.CharField(source='brand.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'article', 'brand', 'brand_name',
                  'price', 'old_price', 'main_image', 'is_available',
                  'is_popular', 'is_new', 'is_active', 'quantity']



class ProductPublicSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    main_image_url = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()  # ← добавить метод

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'article', 'brand_name',
            'price', 'old_price', 'main_image_url',
            'is_available', 'is_popular', 'is_new',
            'short_description', 'is_favorite', 'quantity'
        ]

    def get_main_image_url(self, obj):
        """Возвращает URL главного фото"""
        main_image = obj.images.filter(is_main=True).first()
        if main_image:
            return main_image.image.url
        first_image = obj.images.first()
        if first_image:
            return first_image.image.url
        return None

    def get_is_favorite(self, obj):  # ← добавить этот метод
        """Проверяет, находится ли товар в избранном у пользователя"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Wishlist.objects.filter(user=request.user, product=obj).exists()
        return False


class ProductDetailSerializer(serializers.ModelSerializer):
    """Детальный просмотр товара (админ/контент)"""
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    categories = CategoryPublicSerializer(many=True, read_only=True)
    cars = CarPublicSerializer(many=True, read_only=True)
    created_by_info = serializers.SerializerMethodField()
    updated_by_info = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()  # ← добавить
    main_image = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'article', 'manufacturer_code',
                  'brand', 'brand_name', 'categories', 'cars',
                  'description', 'short_description', 'specifications',
                  'price', 'old_price', 'quantity', 'main_image',
                  'is_available', 'is_popular', 'is_new', 'is_active',
                  'meta_title', 'meta_description', 'views_count', 'orders_count',
                  'created_at', 'updated_at', 'created_by_info', 'updated_by_info',
                  'is_favorite']  # ← добавить

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

    def get_is_favorite(self, obj):  # ← добавить
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Wishlist.objects.filter(user=request.user, product=obj).exists()
        return False