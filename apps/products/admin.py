# apps/products/admin.py
from django.contrib import admin
from .models import Product
from apps.product_images.models import ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'is_main', 'order']
    show_change_link = True


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'brand', 'price', 'is_active', 'is_popular', 'is_new']
    list_filter = ['is_active', 'is_popular', 'is_new', 'brand']
    search_fields = ['name', 'article']
    inlines = [ProductImageInline]  # ← заменили main_image на inlines

    # Удалите main_image из fields или fieldsets
    fields = [
        'name', 'slug', 'article', 'manufacturer_code',
        'brand', 'categories', 'cars',
        'description', 'short_description', 'specifications',
        'price', 'old_price', 'quantity',
        # 'main_image',  # ← удалить эту строку
        'is_available', 'is_popular', 'is_new', 'is_active',
        'meta_title', 'meta_description',
        'views_count', 'orders_count'
    ]

    readonly_fields = ['views_count', 'orders_count', 'created_at', 'updated_at']