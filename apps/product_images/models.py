# apps/product_images/models.py
from django.db import models
from django.conf import settings
from apps.products.models import Product
import cloudinary.uploader
from cloudinary.models import CloudinaryField


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="Товар"
    )
    image = CloudinaryField(
        'image',
        folder='product_images/',
        format='webp',
        transformation={
            'width': 1200,
            'height': 1200,
            'crop': 'limit',
            'quality': 'auto',
            'fetch_format': 'webp'
        },
        blank=True,
        null=True,
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

    def save(self, *args, **kwargs):
        # ЭСКИ СҮРӨТТҮН ПУБЛИК ID'СИН АЛУУ
        old_public_id = None
        if self.pk:
            try:
                old_instance = ProductImage.objects.get(pk=self.pk)
                if old_instance.image:
                    # Cloudinary URL'ден public_id алуу
                    if hasattr(old_instance.image, 'public_id'):
                        old_public_id = old_instance.image.public_id
                    elif hasattr(old_instance.image, 'url'):
                        # URL'ден public_id алуу
                        url = old_instance.image.url
                        if '/upload/' in url:
                            parts = url.split('/upload/')
                            if len(parts) > 1:
                                old_public_id = parts[1].split('.')[0]
            except ProductImage.DoesNotExist:
                pass

        # ЖАҢЫ СҮРӨТТҮ САКТОО
        super().save(*args, **kwargs)

        # ЭСКИ СҮРӨТТҮ УДАЛИТЬ КЫЛУУ (эгер өзгөргөн болсо)
        if old_public_id:
            # Жаңы сүрөттүн public_id'син алуу
            new_public_id = None
            if self.image:
                if hasattr(self.image, 'public_id'):
                    new_public_id = self.image.public_id
                elif hasattr(self.image, 'url'):
                    url = self.image.url
                    if '/upload/' in url:
                        parts = url.split('/upload/')
                        if len(parts) > 1:
                            new_public_id = parts[1].split('.')[0]

            # Эгерде public_id өзгөргөн болсо, эскисин удалить
            if old_public_id and old_public_id != new_public_id:
                cloudinary.uploader.destroy(old_public_id)

    def delete(self, *args, **kwargs):
        """Удалить кылганда Cloudinary'ден удалить"""
        if self.image:
            public_id = None
            if hasattr(self.image, 'public_id'):
                public_id = self.image.public_id
            elif hasattr(self.image, 'url'):
                url = self.image.url
                if '/upload/' in url:
                    parts = url.split('/upload/')
                    if len(parts) > 1:
                        public_id = parts[1].split('.')[0]

            if public_id:
                cloudinary.uploader.destroy(public_id)

        super().delete(*args, **kwargs)