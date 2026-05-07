# apps/reviews/admin.py

from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'user', 'rating', 'status', 'created_at']
    list_display_links = ['id', 'product']
    list_filter = ['rating', 'status', 'created_at']
    search_fields = ['product__name', 'user__username', 'text']
    list_editable = ['status']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Информация', {
            'fields': ('product', 'user', 'rating', 'text', 'status')
        }),
        ('Аудит', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )