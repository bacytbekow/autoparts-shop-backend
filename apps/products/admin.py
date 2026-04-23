# apps/products/admin.py

from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'brand', 'price', 'quantity', 'is_available', 'is_active', 'created_at']
    list_display_links = ['id', 'name']
    list_filter = ['brand', 'is_available', 'is_popular', 'is_new', 'is_active', 'created_at']
    search_fields = ['name', 'article', 'manufacturer_code', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['views_count', 'orders_count', 'created_at', 'updated_at', 'created_by', 'updated_by']
    list_editable = ['price', 'quantity', 'is_available', 'is_active']

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'article', 'manufacturer_code', 'brand', 'categories', 'cars')
        }),
        ('Описание', {
            'fields': ('short_description', 'description', 'specifications')
        }),
        ('Цены и наличие', {
            'fields': ('price', 'old_price', 'quantity', 'is_available')
        }),
        ('Фото', {
            'fields': ('main_image',)
        }),
        ('Настройки', {
            'fields': ('is_popular', 'is_new', 'is_active')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Статистика', {
            'fields': ('views_count', 'orders_count'),
            'classes': ('collapse',)
        }),
        ('Аудит', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)