#!/usr/bin/env bash
set -euo pipefail

# Запуск тестів Django API (core/tests/test_api.py)
# Використання:
#   bash run_tests.sh

python manage.py test core.tests.test_api -v 2 --settings=naverny_borschu_api.settings_test
