# apps/core/serializers.py
from rest_framework import serializers
from .models import FooterSettings, FooterCategory, FooterInfoLink, SocialLink


class FooterCategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий футера"""

    class Meta:
        model = FooterCategory
        fields = ['name', 'url']


class FooterInfoLinkSerializer(serializers.ModelSerializer):
    """Сериализатор для информационных ссылок"""

    class Meta:
        model = FooterInfoLink
        fields = ['name', 'url']


class SocialLinkSerializer(serializers.ModelSerializer):
    """Сериализатор для социальных сетей"""
    icon = serializers.SerializerMethodField()

    class Meta:
        model = SocialLink
        fields = ['name', 'url', 'icon']

    def get_icon(self, obj):
        return obj.name.lower()


class FooterSettingsSerializer(serializers.ModelSerializer):
    """Сериализатор для настроек футера"""
    categories = serializers.SerializerMethodField()
    info_links = serializers.SerializerMethodField()
    social_links = serializers.SerializerMethodField()

    class Meta:
        model = FooterSettings
        fields = [
            'logo_text',
            'description',
            'phone',
            'email',
            'address',
            'copyright_text',
            'categories',
            'info_links',
            'social_links'
        ]

    def get_categories(self, obj):
        """Получаем все активные категории"""
        categories = FooterCategory.objects.filter(is_active=True)
        return FooterCategorySerializer(categories, many=True).data

    def get_info_links(self, obj):
        """Получаем все активные информационные ссылки"""
        info_links = FooterInfoLink.objects.filter(is_active=True)
        return FooterInfoLinkSerializer(info_links, many=True).data

    def get_social_links(self, obj):
        """Получаем все активные социальные сети"""
        social_links = SocialLink.objects.filter(is_active=True)
        return SocialLinkSerializer(social_links, many=True).data