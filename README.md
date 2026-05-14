# Naverny Borschu API — Документація для фронтенд-розробника

Цей документ описує, як працювати з API бекенду. Тут ви знайдете приклади запитів, опис структур даних та інструкції для інтеграції.

## 📚 Зміст

- [Швидкий старт](#швидкий-старт)
- [Список endpoint'ів](#список-endpointів)
- [Авторизація](#авторизація)
- [Приклади запитів (cURL)](#приклади-запитів-curl)
- [Завантаження фото борщу](#завантаження-фото-борщу)
- [Структури даних](#структури-даних)
- [Коди помилок](#коди-помилок)

---

## 🚀 Швидкий старт

### Базова URL API

```
Розробка: http://localhost:8000/api
Production: https://api.naverny-borschu.com/api
```

### Формат даних

- **Content-Type**: `application/json` (для більшості запитів)
- **Відповіді**: JSON
- **Пагінація**: Параметри `page` та `page_size`

---

## 📋 Список endpoint'ів

### Places (Заклади)

| Метод | Endpoint | Опис | Авторизація |
|-------|----------|------|-------------|
| GET | `/api/places/` | Список закладів | ❌ |
| GET | `/api/places/{id}/` | Деталі закладу | ❌ |
| POST | `/api/places/` | Створити заклад | ✅ |
| PATCH | `/api/places/{id}/` | Оновити заклад | ✅ |
| DELETE | `/api/places/{id}/` | Видалити заклад | ✅ |

**Фільтри для GET /places/:**
- `search` — пошук по назві/адресі
- `city` — фільтр по місту
- `type` — фільтр по типу закладу

### Borsches (Борщі)

| Метод | Endpoint | Опис | Авторизація |
|-------|----------|------|-------------|
| GET | `/api/borsches/` | Список борщів | ❌ |
| GET | `/api/borsches/{id}/` | Деталі борщу | ❌ |
| POST | `/api/borsches/` | Створити борщ | ✅ |
| PATCH | `/api/borsches/{id}/` | Оновити борщ | ✅ |
| DELETE | `/api/borsches/{id}/` | Видалити борщ | ✅ |
| POST | `/api/borsches/{id}/upload_photo/` | Завантажити фото | ✅ |

**Фільтри для GET /borsches/:**
- `place_id` — фільтр по закладу
- `type_meat` — фільтр по типу м'яса (`no_meat`, `chicken`, `pork`, `beef`, `other`)
- `min_price`, `max_price` — діапазон цін

### Reviews (Відгуки)

| Метод | Endpoint | Опис | Авторизація |
|-------|----------|------|-------------|
| GET | `/api/reviews/` | Список відгуків | ❌ |
| POST | `/api/borsches/{id}/reviews/` | Створити відгук | ✅ |
| PATCH | `/api/reviews/{id}/` | Оновити відгук | ✅ |
| DELETE | `/api/reviews/{id}/` | Видалити відгук | ✅ |

**Обов'язковий параметр для GET /reviews/:**
- `borsch_id` — ID борщу для фільтрації

### Profile (Профіль користувача)

| Метод | Endpoint | Опис | Авторизація |
|-------|----------|------|-------------|
| GET | `/api/profile/me/` | Отримати профіль | ✅ |
| PATCH | `/api/profile/me/` | Оновити профіль | ✅ |

### Favorites (Обрані борщі)

| Метод | Endpoint | Опис | Авторизація |
|-------|----------|------|-------------|
| GET | `/api/favorites/` | Список обраних | ✅ |
| POST | `/api/favorites/` | Додати до обраних | ✅ |
| DELETE | `/api/favorites/{id}/` | Видалити з обраних | ✅ |

### Place Types (Типи закладів)

| Метод | Endpoint | Опис | Авторизація |
|-------|----------|------|-------------|
| GET | `/api/place-types/` | Список типів | ❌ |

### Users (Користувачі)

| Метод | Endpoint | Опис | Авторизація |
|-------|----------|------|-------------|
| GET | `/api/users/` | Список користувачів | ❌ |
| GET | `/api/users/{id}/` | Деталі користувача | ❌ |

---

## 🔐 Авторизація

### Як це працює

Більшість ендпоінтів для **створення**, **оновлення** та **видалення** вимагають авторизації.

**Публічні ендпоінти (GET):**
- Отримання списків закладів, борщів, відгуків
- Перегляд типів закладів та користувачів

**Приватні ендпоінти (POST, PATCH, DELETE):**
- Створення/оновлення/видалення закладів, борщів, відгуків
- Управління профілем та обраними борщами

### Формат токена

Якщо використовується токенна авторизація, додавайте заголовок:

```
Authorization: Bearer <your-token>
```

### Примітка для фронтенду

На даний момент авторизація реалізована через Django session/auth. Для Google OAuth інтеграції потрібно буде додати додатковий ендпоінт `/api/auth/google/` (планується).

---

## 📝 Приклади запитів (cURL)

### Отримати список закладів

```bash
curl -X GET "http://localhost:8000/api/places/?search=Пузата&city=Київ"
```

**Відповідь:**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "results": [
    {
      "id": "c4f2d26e-9b1b-4a21-9c8a-1a6d3c251234",
      "name": "Пузата Хата",
      "address": "Хрещатик, 25",
      "location_lat": "50.450001",
      "location_lng": "30.523333",
      "country": "Україна",
      "city": "Київ",
      "type": "RESTAURANT",
      "type_label": "Ресторан",
      "created_at": "2025-03-12T10:15:00Z",
      "updated_at": "2025-03-12T10:15:00Z"
    }
  ]
}
```

### Створити новий заклад

```bash
curl -X POST "http://localhost:8000/api/places/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "name": "Пузата Хата",
    "address": "Хрещатик, 25",
    "location_lat": 50.450001,
    "location_lng": 30.523333,
    "country": "Україна",
    "city": "Київ",
    "type": "RESTAURANT"
  }'
```

### Отримати список борщів

```bash
curl -X GET "http://localhost:8000/api/borsches/?place_id=c4f2d26e-9b1b-4a21-9c8a-1a6d3c251234&type_meat=pork"
```

### Створити новий борщ

```bash
curl -X POST "http://localhost:8000/api/borsches/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "place": "c4f2d26e-9b1b-4a21-9c8a-1a6d3c251234",
    "name": "Борщ з пампушками",
    "type_meat": "pork",
    "price_uah": 350.00,
    "weight_grams": 600,
    "photo_urls": []
  }'
```

### Створити відгук

```bash
curl -X POST "http://localhost:8000/api/borsches/b1a2c3d4-5e6f-7a8b-9c0d-1e2f3a4b5c6d/reviews/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "message": "Дуже смачний борщ! Рекомендую.",
    "rating_salt": 9,
    "rating_meat": 8,
    "rating_beet": 9,
    "rating_density": 10,
    "rating_aftertaste": 8,
    "rating_serving": 10,
    "overall_rating": 9
  }'
```

**Важливо:** Усі 6 оцінок (`rating_*`) та `overall_rating` є **обов'язковими**. Діапазон: 0–10.

### Отримати відгуки для борщу

```bash
curl -X GET "http://localhost:8000/api/reviews/?borsch_id=b1a2c3d4-5e6f-7a8b-9c0d-1e2f3a4b5c6d&page=1&page_size=10"
```

### Отримати профіль користувача

```bash
curl -X GET "http://localhost:8000/api/profile/me/" \
  -H "Authorization: Bearer <token>"
```

### Оновити профіль користувача

```bash
curl -X PATCH "http://localhost:8000/api/profile/me/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "given_name": "Марта",
    "email": "newemail@gmail.com",
    "country": "Україна"
  }'
```

### Додати борщ до обраних

```bash
curl -X POST "http://localhost:8000/api/favorites/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "borsch": "b1a2c3d4-5e6f-7a8b-9c0d-1e2f3a4b5c6d"
  }'
```

---

## 📸 Завантаження фото борщу

### Endpoint

```
POST /api/borsches/{id}/upload_photo/
```

### Формат запиту

**Content-Type:** `multipart/form-data`

**Параметри:**
- `photo` (file) — файл зображення (PNG, JPG, WEBP)

### Приклад cURL

```bash
curl -X POST "http://localhost:8000/api/borsches/b1a2c3d4-5e6f-7a8b-9c0d-1e2f3a4b5c6d/upload_photo/" \
  -H "Authorization: Bearer <token>" \
  -F "photo=@/path/to/borsch-photo.png"
```

### Відповідь

```json
{
  "photo_url": "/media/borsches/b1a2c3d4/photos/abc123.png",
  "message": "Фото успішно завантажено"
}
```

### Інтеграція з React (приклад)

```javascript
async function uploadBorschPhoto(borschId, file) {
  const formData = new FormData();
  formData.append('photo', file);
  
  const response = await fetch(
    `http://localhost:8000/api/borsches/${borschId}/upload_photo/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
        // Не встановлюйте Content-Type для FormData!
      },
      body: formData
    }
  );
  
  const data = await response.json();
  return data.photo_url;
}
```

### Важливі нотатки

1. **Авторизація обов'язкова** — тільки авторизовані користувачі можуть завантажувати фото
2. **Формати файлів** — PNG, JPG, WEBP
3. **URL зберігається** — після завантаження URL додається до масиву `photo_urls` борщу
4. **Повна URL** — для відображення використовуйте `${API_URL}${data.photo_url}`

---

## 📊 Структури даних

### Place (Заклад)

```json
{
  "id": "uuid",
  "name": "string",
  "address": "string",
  "location_lat": "decimal",
  "location_lng": "decimal",
  "country": "string",
  "city": "string",
  "type": "string (код типу)",
  "type_label": "string (назва типу)",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Borsch (Борщ)

```json
{
  "id": "uuid",
  "place": "uuid (ID закладу)",
  "place_name": "string",
  "name": "string",
  "type_meat": "string (no_meat|chicken|pork|beef|other)",
  "price_uah": "decimal",
  "weight_grams": "integer",
  "photo_urls": ["string (URL)"],
  "rating_salt": "decimal (0-10)",
  "rating_meat": "decimal (0-10)",
  "rating_beet": "decimal (0-10)",
  "rating_density": "decimal (0-10)",
  "rating_aftertaste": "decimal (0-10)",
  "rating_serving": "decimal (0-10)",
  "overall_rating": "decimal (0-10)",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Review (Відгук)

```json
{
  "id": "uuid",
  "borsch": "uuid (ID борщу)",
  "borsch_name": "string",
  "user": "integer (ID користувача)",
  "author_username": "string",
  "temp_user_id": "string",
  "message": "string",
  "rating_salt": "decimal (0-10)",
  "rating_meat": "decimal (0-10)",
  "rating_beet": "decimal (0-10)",
  "rating_density": "decimal (0-10)",
  "rating_aftertaste": "decimal (0-10)",
  "rating_serving": "decimal (0-10)",
  "overall_rating": "decimal (0-10)",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### UserProfile (Профіль)

```json
{
  "user": "integer",
  "username": "string",
  "email": "string (email)",
  "google_id": "string",
  "given_name": "string",
  "surname": "string",
  "country": "string",
  "locale": "string",
  "avatar_url": "string (URL)",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

---

## ❌ Коди помилок

| Код | Опис | Приклад |
|-----|------|---------|
| 200 | Успішний запит | — |
| 201 | Ресурс створено | Після POST |
| 204 | Ресурс видалено | Після DELETE |
| 400 | Помилка валідації | `{"error": "Поле 'name' є обов'язковим"}` |
| 401 | Потрібна авторизація | `{"error": "Потрібна авторизація"}` |
| 403 | Недостатньо прав | `{"error": "Ви можете редагувати тільки власні відгуки"}` |
| 404 | Ресурс не знайдено | `{"error": "Ресурс не знайдено"}` |
| 500 | Помилка сервера | `{"error": "Внутрішня помилка сервера"}` |

---

## 🔗 Корисні посилання

- [OpenAPI специфікація](openapi.yaml) — повна документація у форматі OpenAPI 3.1
- [API Architecture Document](API_ARCHITECTURE_DOCUMENT.md) — архітектура та моделі даних

---

## 💡 Поради для фронтенд-розробника

1. **Використовуйте пагінацію** — для великих списків додавайте `?page=2&page_size=20`
2. **Обробляйте помилки** — завжди перевіряйте статус відповіді та поле `error`
3. **Кешуйте довідники** — типи закладів (`/api/place-types/`) змінюються рідко
4. **Слідкуйте за рейтингами** — після створення/оновлення/видалення відгуку рейтинги борщу перераховуються автоматично
5. **Фото завантажуйте через FormData** — не встановлюйте `Content-Type` вручну для `multipart/form-data`
