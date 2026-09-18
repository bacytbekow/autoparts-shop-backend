# apps/cars/admin.py
from django.contrib import admin
from .models import Car


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['id', 'make', 'model', 'generation', 'year_from', 'year_to', 'is_active']  # ← убрать brand
    list_filter = ['is_active', 'make']  # ← убрать brand
    search_fields = ['make', 'model', 'generation']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']

    fieldsets = (
        ('Основная информация', {
            'fields': ('make', 'model', 'generation', 'slug')
        }),
        ('Годы выпуска', {
            'fields': ('year_from', 'year_to')
        }),
        ('Технические характеристики', {
            'fields': ('engine', 'body_type')
        }),
        ('Статус', {
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