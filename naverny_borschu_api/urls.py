"""
Головна конфігурація URL для проєкту Naverny Borschu API.

Цей файл визначає маршрутизацію запитів до відповідних view.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # Адмін-панель Django
    path('admin/', admin.site.urls),
    
    # API ендпоінти
    path('api/', include('core.urls')),
]

# Додаємо маршрути для медіа-файлів у режимі відлагодження
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
