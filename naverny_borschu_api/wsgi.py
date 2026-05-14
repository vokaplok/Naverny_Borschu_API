"""
WSGI конфігурація для проєкту Naverny Borschu API.

Цей файл ініціалізує WSGI додаток для синхронних веб-серверів.
"""

import os

from django.core.wsgi import get_wsgi_application

# Встановлюємо змінну оточення для налаштувань
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'naverny_borschu_api.settings')

# Отримуємо WSGI додаток
application = get_wsgi_application()
