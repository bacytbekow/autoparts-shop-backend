
# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)

    ROLE_CHOICES = (
        ('customer', 'Покупатель'),
        ('manager', 'Менеджер'),
        ('content', 'Контент-менеджер'),
        ('admin', 'Администратор'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    updated_at = models.DateTimeField(auto_now=True)  # автоматически обновляется при каждом изменении
    updated_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_users'
    )

    def __str__(self):
        return self.username

