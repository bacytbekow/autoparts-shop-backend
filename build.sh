#!/usr/bin/env bash

# Установка зависимостей
pip install -r requirements.txt

# Сбор статики
python manage.py collectstatic --noinput

# Миграции
python manage.py migrate --noinput

# Создание суперпользователя (если не существует)
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
import os

User = get_user_model()
username = os.environ.get('SUPER_ADMIN_USERNAME', 'admin')
email = os.environ.get('SUPER_ADMIN_EMAIL', 'admin@shop.com')
password = os.environ.get('SUPER_ADMIN_PASSWORD', 'admin123')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'Суперпользователь "{username}" создан')
else:
    print(f'Суперпользователь "{username}" уже существует')
EOF