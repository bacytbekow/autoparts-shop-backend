# apps/core/views.py
from rest_framework import generics, permissions
from .models import FooterSettings, FooterCategory, FooterInfoLink, SocialLink
from .serializers import (
    FooterSettingsSerializer,
    FooterCategorySerializer,
    FooterInfoLinkSerializer,
    SocialLinkSerializer
)
from .permissions import IsAdminOrSuperuser


class FooterSettingsView(generics.RetrieveUpdateAPIView):
    """Получение и обновление настроек футера"""
    permission_classes = [IsAdminOrSuperuser]
    serializer_class = FooterSettingsSerializer

    def get_object(self):
        obj, created = FooterSettings.objects.get_or_create(id=1)
        return obj


class FooterCategoryListCreateView(generics.ListCreateAPIView):
    """Список категорий и создание новой"""
    queryset = FooterCategory.objects.filter(is_active=True)
    serializer_class = FooterCategorySerializer
    permission_classes = [IsAdminOrSuperuser]


class FooterCategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Получение, обновление, удаление категории по id"""
    queryset = FooterCategory.objects.all()
    serializer_class = FooterCategorySerializer
    permission_classes = [IsAdminOrSuperuser]


class FooterInfoLinkListCreateView(generics.ListCreateAPIView):
    """Список ссылок и создание новой"""
    queryset = FooterInfoLink.objects.filter(is_active=True)
    serializer_class = FooterInfoLinkSerializer
    permission_classes = [IsAdminOrSuperuser]


class FooterInfoLinkRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Получение, обновление, удаление ссылки по id"""
    queryset = FooterInfoLink.objects.all()
    serializer_class = FooterInfoLinkSerializer
    permission_classes = [IsAdminOrSuperuser]


class SocialLinkListCreateView(generics.ListCreateAPIView):
    """Список соцсетей и создание новой"""
    queryset = SocialLink.objects.filter(is_active=True)
    serializer_class = SocialLinkSerializer
    permission_classes = [IsAdminOrSuperuser]


class SocialLinkRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Получение, обновление, удаление соцсети по id"""
    queryset = SocialLink.objects.all()
    serializer_class = SocialLinkSerializer
    permission_classes = [IsAdminOrSuperuser]