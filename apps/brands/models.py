# apps/brands/models.py

from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Brand(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="Название бренда")
    slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name="URL")
    logo = models.ImageField(upload_to='brands/', blank=True, null=True, verbose_name="Логотип")
    description = models.TextField(blank=True, verbose_name="Описание")
    country = models.CharField(max_length=100, blank=True, verbose_name="Страна")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    order = models.IntegerField(default=0, verbose_name="Порядок сортировки")
    meta_title = models.CharField(max_length=255, blank=True, verbose_name="SEO заголовок")
    meta_description = models.TextField(blank=True, verbose_name="SEO описание")

    # Аудит
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_brands',
        verbose_name="Кто создал"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_brands',
        verbose_name="Кто обновил"
    )

    class Meta:
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name