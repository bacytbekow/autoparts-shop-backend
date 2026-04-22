# apps/cars/admin.py

from django.contrib import admin
from .models import Car


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['id', 'brand', 'model', 'generation', 'year_from', 'year_to', 'engine', 'body_type', 'is_active',
                    'created_at']
    list_display_links = ['id', 'brand', 'model']
    list_filter = ['brand', 'is_active', 'body_type', 'year_from']
    search_fields = ['brand__name', 'model', 'generation', 'engine']
    prepopulated_fields = {'slug': ('model',)}
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    list_editable = ['is_active']

    fieldsets = (
        ('Основная информация', {
            'fields': ('brand', 'model', 'slug', 'generation', 'year_from', 'year_to', 'engine', 'body_type')
        }),
        ('Настройки', {
            'fields': ('is_active',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
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