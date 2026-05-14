"""
Конфігурація додатку Core.

Цей додаток містить основні моделі, серіалізатори та view для API.
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Конфігурація додатку Core."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Основне API'
