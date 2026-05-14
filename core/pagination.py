"""
Класи пагінації для Django REST Framework.

Цей файл містить кастомні класи пагінації для контролю
відображення великих списків даних.

Використання:
    pagination_class = CustomPageNumberPagination
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPageNumberPagination(PageNumberPagination):
    """
    Кастомна пагінація з параметрами page та page_size.
    
    Параметри запиту:
    - page: номер сторінки (починаючи з 1)
    - page_size: кількість записів на сторінці (за замовчуванням 20)
    
    Приклад запиту:
        GET /api/borsches/?page=2&page_size=10
    
    Відповідь містить:
    - count: загальна кількість записів
    - next: URL наступної сторінки (або null)
    - previous: URL попередньої сторінки (або null)
    - results: масив об'єктів на поточній сторінці
    """
    
    # Параметр для номера сторінки
    page_query_param = 'page'
    
    # Параметр для розміру сторінки
    page_size_query_param = 'page_size'
    
    # Розмір сторінки за замовчуванням
    page_size = 20
    
    # Максимальний розмір сторінки (обмеження для захисту від перевантаження)
    max_page_size = 100
    
    def get_paginated_response(self, data):
        """
        Формування відповіді з пагінацією.
        
        Повертає структуровану відповідь з мета-даними.
        """
        return Response({
            'count': self.page.paginator.count,  # Загальна кількість
            'next': self.get_next_link(),  # URL наступної сторінки
            'previous': self.get_previous_link(),  # URL попередньої сторінки
            'results': data,  # Дані поточної сторінки
            'page': self.page.number,  # Поточний номер сторінки
            'page_size': self.get_page_size(self.request),  # Розмір сторінки
            'total_pages': self.page.paginator.num_pages  # Загальна кількість сторінок
        })


class NoPagination(PageNumberPagination):
    """
    Пагінація, яка вимкнена (повертає всі записи).
    
    Використовується для ендпоінтів, де потрібен повний список
    без обмежень (наприклад, довідники типів).
    """
    
    page_size = None  # Вимкнути пагінацію
    page_query_param = None
    page_size_query_param = None
