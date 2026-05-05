# apps/cart/admin.py

from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    raw_id_fields = ['product']
    extra = 0
    fields = ['product', 'quantity', 'created_at', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'get_item_count', 'get_total_price', 'created_at', 'updated_at']
    list_display_links = ['id', 'user']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CartItemInline]

    def get_item_count(self, obj):
        return obj.items.count()
    get_item_count.short_description = "Количество товаров"

    def get_total_price(self, obj):
        return f"{obj.get_total_price()} ₽"
    get_total_price.short_description = "Общая сумма"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart', 'product', 'quantity', 'get_total_price', 'created_at']
    list_display_links = ['id', 'cart']
    search_fields = ['cart__user__username', 'product__name']
    list_filter = ['created_at']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['cart', 'product']

    def get_total_price(self, obj):
        return f"{obj.get_total_price()} ₽"
    get_total_price.short_description = "Сумма"