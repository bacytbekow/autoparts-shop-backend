# apps/cars/models.py

from django.db import models
from django.conf import settings
from django.utils.text import slugify
from apps.brands.models import Brand


class Car(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name="Бренд")
    model = models.CharField(max_length=200, verbose_name="Модель")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    generation = models.CharField(max_length=100, blank=True, verbose_name="Поколение")
    year_from = models.IntegerField(null=True, blank=True, verbose_name="Год от")
    year_to = models.IntegerField(null=True, blank=True, verbose_name="Год до")
    engine = models.CharField(max_length=100, blank=True, verbose_name="Двигатель")
    body_type = models.CharField(max_length=50, blank=True, verbose_name="Тип кузова")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='created_cars'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='updated_cars'
    )

    class Meta:
        verbose_name = "Автомобиль"
        verbose_name_plural = "Автомобили"
        ordering = ['brand__name', 'model', 'year_from']

    def save(self, *args, **kwargs):
        if not self.slug:
            slug_str = f"{self.brand.name} {self.model} {self.generation}".strip()
            self.slug = slugify(slug_str, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        year_str = f"({self.year_from}-{self.year_to})" if self.year_from else ""
        return f"{self.brand.name} {self.model} {self.generation} {year_str}".strip()