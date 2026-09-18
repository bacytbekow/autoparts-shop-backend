# apps/products/admin.py
from django.contrib import admin
from django.utils.text import slugify
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
    inlines = [ProductImageInline]

    prepopulated_fields = {'slug': ('name',)}

    fields = [
        'name', 'slug', 'article', 'manufacturer_code',
        'brand', 'categories', 'cars',
        'description', 'short_description', 'specifications',
        'price', 'old_price', 'quantity',
        'is_available', 'is_popular', 'is_new', 'is_active',
        'meta_title', 'meta_description',
        'views_count', 'orders_count'
    ]

    readonly_fields = ['views_count', 'orders_count', 'created_at', 'updated_at']

    def save_model(self, request, obj, form, change):
        """Сактоодо уникалдуу slug түзүү"""
        if not obj.slug:
            original_slug = slugify(obj.name, allow_unicode=False)
            obj.slug = original_slug

            # Уникалдуулугун текшерүү
            counter = 1
            while Product.objects.filter(slug=obj.slug).exclude(pk=obj.pk).exists():
                obj.slug = f"{original_slug}-{counter}"
                counter += 1

        super().save_model(request, obj, form, change)