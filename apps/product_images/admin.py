# apps/product_images/admin.py

from django.contrib import admin
from .models import ProductImage


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'image', 'is_main', 'order', 'created_at']
    list_display_links = ['id', 'product']
    list_filter = ['is_main', 'created_at']
    search_fields = ['product__name', 'alt_text']
    list_editable = ['is_main', 'order']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)