# apps/products/models.py

from django.db import models
from django.conf import settings
from django.utils.text import slugify
from apps.categories.models import Category
from apps.brands.models import Brand
from apps.cars.models import Car


class Product(models.Model):
    # Основная информация
    name = models.CharField(max_length=255, verbose_name="Название товара")
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    article = models.CharField(max_length=100, blank=True, verbose_name="OEM-номер")
    manufacturer_code = models.CharField(max_length=100, blank=True, verbose_name="Код производителя")

    # Связи
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name="Бренд")
    categories = models.ManyToManyField(Category, related_name='products', verbose_name="Категории")
    cars = models.ManyToManyField(Car, blank=True, related_name='products', verbose_name="Совместимые автомобили")

    # Описание
    description = models.TextField(blank=True, verbose_name="Полное описание")
    short_description = models.TextField(blank=True, verbose_name="Краткое описание")
    specifications = models.JSONField(default=dict, blank=True, verbose_name="Характеристики")

    # Цены и наличие
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Старая цена")
    quantity = models.IntegerField(default=0, verbose_name="Остаток на складе")

    # Фото
    main_image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Главное фото")

    # Флаги
    is_available = models.BooleanField(default=True, verbose_name="В наличии")
    is_popular = models.BooleanField(default=False, verbose_name="Популярный")
    is_new = models.BooleanField(default=False, verbose_name="Новинка")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    # SEO
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)

    # Статистика
    views_count = models.IntegerField(default=0, verbose_name="Просмотры")
    orders_count = models.IntegerField(default=0, verbose_name="Продажи")

    # Аудит
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='created_products'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='updated_products'
    )

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.brand.name})"