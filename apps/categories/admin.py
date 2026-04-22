from django.contrib import admin
from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug', 'is_active', 'parent', 'order', 'created_at']
    list_display_links = ['id', 'name']
    list_filter = ['is_active', 'parent', 'created_at']
    search_fields = ['name', 'description', 'meta_title']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    list_editable = ['is_active', 'order']

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'parent', 'description', 'image')
        }),
        ('Настройки', {
            'fields': ('order', 'is_active')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description')
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