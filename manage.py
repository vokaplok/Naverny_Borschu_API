#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Запуск адміністративних команд Django."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'naverny_borschu_api.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Не вдалося імпортувати Django. Переконайтеся, що Django встановлено "
            "та що він доступний у змінній оточення PYTHONPATH."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
