"""
ASGI конфігурація для проєкту Naverny Borschu API.

Цей файл ініціалізує ASGI додаток для асинхронних веб-серверів.
"""

import os

from django.core.asgi import get_asgi_application

# Встановлюємо змінну оточення для налаштувань
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'naverny_borschu_api.settings')

# Отримуємо ASGI додаток
application = get_asgi_application()
