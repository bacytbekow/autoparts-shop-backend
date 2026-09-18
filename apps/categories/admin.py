# apps/categories/admin.py
from django.contrib import admin
from .models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug', 'is_active', 'parent', 'order']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}  # ✅ автоматтык толтуруу
    fields = ['name', 'slug', 'parent', 'image', 'description', 'order', 'is_active', 'meta_title', 'meta_description']