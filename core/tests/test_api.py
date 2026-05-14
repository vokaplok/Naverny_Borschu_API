"""
API тести для основних endpoint-ів Core.

Покриття:
- POST (створення об'єкта)
- GET list + pagination
- GET detail by id
- PUT/PATCH (оновлення)
- DELETE (видалення)
- upload_photo (multipart upload)
"""

import shutil
import tempfile
from decimal import Decimal

from django.urls import reverse
from django.test import override_settings
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from core.models import PlaceType, Place, Borsch


class TestCoreAPI(APITestCase):
    """Набір інтеграційних тестів для API."""

    @classmethod
    def setUpTestData(cls):
        # Фікстура: тип закладу
        cls.place_type = PlaceType.objects.create(
            code="RESTAURANT",
            label="Ресторан",
        )

        # Фікстура: базовий заклад
        cls.place = Place.objects.create(
            name="Пузата Хата",
            address="Хрещатик, 25",
            location_lat=Decimal("50.450100"),
            location_lng=Decimal("30.523400"),
            country="Україна",
            city="Київ",
            type=cls.place_type,
        )

        # Фікстура: базовий борщ для upload_photo
        cls.borsch = Borsch.objects.create(
            place=cls.place,
            name="Борщ Київський",
            type_meat="beef",
            price_uah=Decimal("150.00"),
            weight_grams=400,
            photo_urls=[],
        )

    def setUp(self):
        # Фікстура: авторизований користувач для модифікуючих запитів
        self.user = User.objects.create_user(
            username="test_user",
            email="test@example.com",
            password="StrongPassword123!",
        )

        # Тимчасова директорія для upload_photo тестів
        self._media_dir = tempfile.mkdtemp(prefix="test_media_")
        self._media_override = override_settings(MEDIA_ROOT=self._media_dir, MEDIA_URL="/media/")
        self._media_override.enable()

    def tearDown(self):
        self._media_override.disable()
        shutil.rmtree(self._media_dir, ignore_errors=True)

    def _place_payload(self, **overrides):
        """Фікстура payload для створення/оновлення Place."""
        payload = {
            "name": "Тестовий заклад",
            "address": "вул. Тестова, 1",
            "location_lat": "49.839700",
            "location_lng": "24.029700",
            "country": "Україна",
            "city": "Львів",
            "type": self.place_type.id,
        }
        payload.update(overrides)
        return payload

    def _auth(self):
        """Авторизація тестового користувача в APIClient."""
        self.client.force_authenticate(user=self.user)

    def test_create_place_post(self):
        """POST /api/places/ - створення об'єкта."""
        self._auth()
        url = reverse("place-list")
        payload = self._place_payload()

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Place.objects.count(), 2)
        created = Place.objects.get(name="Тестовий заклад")
        self.assertEqual(created.city, "Львів")

    def test_get_places_list_with_pagination(self):
        """GET /api/places/ - список з пагінацією."""
        for idx in range(1, 5):
            Place.objects.create(
                name=f"Заклад {idx}",
                address=f"Адреса {idx}",
                location_lat=Decimal("50.450100"),
                location_lng=Decimal("30.523400"),
                country="Україна",
                city="Київ",
                type=self.place_type,
            )

        url = reverse("place-list")
        response = self.client.get(url, {"page": 1, "page_size": 2}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)
        self.assertIn("total_pages", response.data)
        self.assertEqual(response.data["page"], 1)
        self.assertEqual(response.data["page_size"], 2)
        self.assertEqual(len(response.data["results"]), 2)

    def test_get_place_detail_by_id(self):
        """GET /api/places/{id}/ - отримання одного об'єкта."""
        url = reverse("place-detail", kwargs={"pk": self.place.id})
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(response.data["id"]), str(self.place.id))
        self.assertEqual(response.data["name"], self.place.name)

    def test_update_place_with_patch(self):
        """PATCH /api/places/{id}/ - часткове оновлення."""
        self._auth()
        url = reverse("place-detail", kwargs={"pk": self.place.id})
        payload = {"city": "Одеса", "name": "Оновлена назва"}

        response = self.client.patch(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.place.refresh_from_db()
        self.assertEqual(self.place.city, "Одеса")
        self.assertEqual(self.place.name, "Оновлена назва")

    def test_update_place_with_put(self):
        """PUT /api/places/{id}/ - повне оновлення."""
        self._auth()
        url = reverse("place-detail", kwargs={"pk": self.place.id})
        payload = self._place_payload(
            name="PUT заклад",
            address="вул. Нова, 99",
            city="Дніпро",
        )

        response = self.client.put(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.place.refresh_from_db()
        self.assertEqual(self.place.name, "PUT заклад")
        self.assertEqual(self.place.address, "вул. Нова, 99")
        self.assertEqual(self.place.city, "Дніпро")

    def test_delete_place(self):
        """DELETE /api/places/{id}/ - видалення об'єкта."""
        self._auth()
        place_to_delete = Place.objects.create(
            name="На видалення",
            address="вул. Тимчасова, 2",
            location_lat=Decimal("50.450100"),
            location_lng=Decimal("30.523400"),
            country="Україна",
            city="Київ",
            type=self.place_type,
        )
        url = reverse("place-detail", kwargs={"pk": place_to_delete.id})

        response = self.client.delete(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Place.objects.filter(id=place_to_delete.id).exists())

    def test_upload_photo_endpoint(self):
        """POST /api/borsches/{id}/upload_photo/ - завантаження фото."""
        self._auth()
        url = f"/api/borsches/{self.borsch.id}/upload_photo/"
        photo = SimpleUploadedFile(
            "borsch.jpg",
            b"fake-image-content",
            content_type="image/jpeg",
        )

        response = self.client.post(url, {"photo": photo}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("photo_url", response.data)
        self.assertIn("/media/", response.data["photo_url"])
        self.assertIn("borsches", response.data["photo_url"])
        self.borsch.refresh_from_db()
        self.assertEqual(len(self.borsch.photo_urls), 1)

