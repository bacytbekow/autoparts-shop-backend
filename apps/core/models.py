# apps/core/models.py
from django.db import models


class FooterSettings(models.Model):
    """Настройки футера"""
    logo_text = models.CharField(max_length=100, default='AUTOPARTS')
    description = models.TextField(default='Магазин автозапчастей в Бишкеке. Более 500 000 наименований.')
    phone = models.CharField(max_length=50, default='+996 700 000 000')
    email = models.EmailField(default='info@autoparts.kg')
    address = models.TextField(default='Бишкек, ул. Манаса 123')
    copyright_text = models.CharField(max_length=200, default='© 2025 AutoParts. Все права защищены.')

    class Meta:
        verbose_name = 'Настройки футера'
        verbose_name_plural = 'Настройки футера'


class FooterCategory(models.Model):
    """Категории в футере"""
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=200)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']


class FooterInfoLink(models.Model):
    """Информационные ссылки в футере"""
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=200)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']


class SocialLink(models.Model):
    """Социальные сети"""
    SOCIAL_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('telegram', 'Telegram'),
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('youtube', 'YouTube'),
    ]

    name = models.CharField(max_length=50, choices=SOCIAL_CHOICES)
    url = models.URLField()
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']