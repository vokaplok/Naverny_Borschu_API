"""
Тестові налаштування Django.

Використовують SQLite, щоб тести не залежали від зовнішнього PostgreSQL
та прав доступу на сервері БД.
"""

from .settings import *  # noqa


# Окрема тестова БД у файлі (стабільно працює на Windows/Linux/macOS).
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test_db.sqlite3",
    }
}

