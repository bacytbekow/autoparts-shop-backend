# apps/orders/admin.py

from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'product_article', 'price', 'quantity']
    fields = ['product_name', 'product_article', 'price', 'quantity']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'phone', 'status', 'total_price', 'created_at']
    list_display_links = ['id', 'name']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'phone', 'email', 'address']
    readonly_fields = ['created_at', 'updated_at', 'total_price']
    list_editable = ['status']
    inlines = [OrderItemInline]

    fieldsets = (
        ('Информация о покупателе', {
            'fields': ('user', 'name', 'phone', 'email', 'address')
        }),
        ('Детали заказа', {
            'fields': ('status', 'total_price', 'comment')
        }),
        ('Аудит', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product_name', 'price', 'quantity', 'get_total_price']
    list_display_links = ['id', 'order']
    search_fields = ['product_name', 'product_article']
    readonly_fields = ['order', 'product', 'product_name', 'product_article', 'price', 'quantity']

    def get_total_price(self, obj):
        return obj.get_total_price()
    get_total_price.short_description = "Сумма"