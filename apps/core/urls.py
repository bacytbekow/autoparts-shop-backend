# apps/core/urls.py
from django.urls import path
from .views import (
    FooterSettingsView,
    FooterCategoryListCreateView,
    FooterCategoryRetrieveUpdateDestroyView,
    FooterInfoLinkListCreateView,
    FooterInfoLinkRetrieveUpdateDestroyView,
    SocialLinkListCreateView,
    SocialLinkRetrieveUpdateDestroyView,
)

urlpatterns = [
    # Footer settings
    path('footer-settings/', FooterSettingsView.as_view(), name='footer-settings'),

    # Categories
    path('footer-categories/', FooterCategoryListCreateView.as_view(), name='footer-categories'),
    path('footer-categories/<int:pk>/', FooterCategoryRetrieveUpdateDestroyView.as_view(),
         name='footer-category-detail'),

    # Info links
    path('footer-info-links/', FooterInfoLinkListCreateView.as_view(), name='footer-info-links'),
    path('footer-info-links/<int:pk>/', FooterInfoLinkRetrieveUpdateDestroyView.as_view(),
         name='footer-info-link-detail'),

    # Social links
    path('social-links/', SocialLinkListCreateView.as_view(), name='social-links'),
    path('social-links/<int:pk>/', SocialLinkRetrieveUpdateDestroyView.as_view(), name='social-link-detail'),
]