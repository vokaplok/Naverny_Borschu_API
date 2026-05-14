"""
Класи дозволів (permissions) для Django REST Framework.

Цей файл містить кастомні дозволи для контролю доступу до API ендпоінтів.

Використання:
    permission_classes = [IsAuthenticatedOrReadOnlyUA]
"""

from rest_framework import permissions


class IsAuthenticatedOrReadOnlyUA(permissions.BasePermission):
    """
    Дозвіл для авторизованих користувачів або тільки читання.
    
    Логіка:
    - Без авторизації: дозволені тільки безпечні методи (GET, HEAD, OPTIONS)
    - З авторизацією: дозволені всі методи
    
    Використовується для публічних ендпоінтів з можливістю
    створення/оновлення тільки для авторизованих користувачів.
    """
    
    def has_permission(self, request, view):
        """
        Перевірка дозволу на рівні запиту.
        
        Безпечні методи (GET, HEAD, OPTIONS) дозволені всім.
        Для модифікуючих методів (POST, PUT, PATCH, DELETE)
        потрібна авторизація.
        """
        # Безпечні методи дозволені всім (тільки читання)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Для модифікуючих методів потрібна авторизація
        return request.user and request.user.is_authenticated


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Дозвіл тільки для власника об'єкта або тільки читання.
    
    Логіка:
    - Без авторизації: тільки читання
    - З авторизацією: модифікація тільки якщо користувач є власником
    
    Вимагає, щоб модель мала поле 'user' або 'owner'.
    """
    
    def has_permission(self, request, view):
        """Перевірка на рівні запиту."""
        # Безпечні методи дозволені всім
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Для модифікуючих методів потрібна авторизація
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Перевірка дозволу на рівні об'єкта.
        
        Для модифікуючих методів перевіряємо, чи є користувач власником.
        """
        # Безпечні методи дозволені всім
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Перевірка власності (спроба знайти поле user або owner)
        owner = getattr(obj, 'user', None) or getattr(obj, 'owner', None)
        
        return owner == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Дозвіл тільки для адміністраторів або тільки читання.
    
    Логіка:
    - Без авторизації: тільки читання
    - З авторизацією (не адмін): тільки читання
    - Адміністратор: всі методи
    """
    
    def has_permission(self, request, view):
        """Перевірка на рівні запиту."""
        # Безпечні методи дозволені всім
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Для модифікуючих методів потрібні права адміністратора
        return request.user and request.user.is_staff
