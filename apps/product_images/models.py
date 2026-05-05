# apps/product_images/models.py

from django.db import models
from django.conf import settings
from django_resized import ResizedImageField
from apps.products.models import Product


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="Товар"
    )
    image = ResizedImageField(
        size=[1200, 1200],
        quality=85,
        upload_to='product_images/',
        force_format='WEBP',
        verbose_name="Фото"
    )
    alt_text = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="SEO текст"
    )
    is_main = models.BooleanField(
        default=False,
        verbose_name="Главное фото"
    )
    order = models.IntegerField(
        default=0,
        verbose_name="Порядок"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='created_product_images'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='updated_product_images'
    )

    class Meta:
        verbose_name = "Фото товара"
        verbose_name_plural = "Фото товаров"
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"Фото для {self.product.name}"