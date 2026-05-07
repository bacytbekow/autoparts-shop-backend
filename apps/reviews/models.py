# apps/reviews/models.py

from django.db import models
from django.conf import settings
from apps.products.models import Product


class Review(models.Model):
    STATUS_CHOICES = (
        ('pending', 'На модерации'),
        ('approved', 'Опубликован'),
        ('rejected', 'Отклонён'),
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name="Товар"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name="Пользователь"
    )
    rating = models.PositiveSmallIntegerField(
        choices=[(i, i) for i in range(1, 6)],
        verbose_name="Оценка"
    )
    text = models.TextField(verbose_name="Текст отзыва")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Статус"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} - {self.user.username} - {self.rating}★"