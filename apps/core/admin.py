# apps/core/admin.py
from django.contrib import admin
from .models import FooterSettings, FooterCategory, FooterInfoLink, SocialLink


@admin.register(FooterSettings)
class FooterSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Логотип и описание', {
            'fields': ('logo_text', 'description')
        }),
        ('Контакты', {
            'fields': ('phone', 'email', 'address')
        }),
        ('Копирайт', {
            'fields': ('copyright_text',)
        }),
    )


@admin.register(FooterCategory)
class FooterCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(FooterInfoLink)
class FooterInfoLinkAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ['get_name_display', 'url', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active', 'name']