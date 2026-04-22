from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'role', 'is_active', 'date_joined']
    list_display_links = ['id', 'username']
    list_filter = ['role', 'is_active', 'is_staff', 'is_superuser', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone']
    list_editable = ['role', 'is_active']

    fieldsets = (
        ('Основная информация', {
            'fields': ('username', 'email', 'password', 'role')
        }),
        ('Личные данные', {
            'fields': ('first_name', 'last_name', 'phone', 'address', 'city')
        }),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Аудит', {
            'fields': ('updated_by',),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['date_joined', 'updated_at']

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )