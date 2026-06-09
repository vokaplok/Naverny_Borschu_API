from unittest.mock import patch

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.google_auth import GoogleAuthError, GoogleIdentity
from core.models import AppUser


class GoogleAuthViewTests(APITestCase):
    def test_requires_token_payload(self):
        response = self.client.post(reverse('auth-google'), {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    @patch('core.viewsets.fetch_google_identity')
    def test_creates_app_user_from_google_id_token(self, fetch_google_identity_mock):
        fetch_google_identity_mock.return_value = GoogleIdentity(
            sub='google-sub-1',
            email='marta@example.com',
            email_verified=True,
            given_name='Marta',
            family_name='Valerie',
            full_name='Marta Valerie',
            picture='https://example.com/avatar.png',
            locale='uk',
            aud='client-id-1',
            azp='client-id-1',
        )

        response = self.client.post(
            reverse('auth-google'),
            {'id_token': 'fake-google-token'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_new_user'])
        self.assertTrue(response.data['session_authenticated'])
        self.assertEqual(response.data['user']['email'], 'marta@example.com')
        self.assertTrue(AppUser.objects.filter(email='marta@example.com').exists())
        self.assertTrue(User.objects.filter(username='marta@example.com').exists())

    @patch('core.viewsets.fetch_google_identity')
    def test_updates_existing_app_user(self, fetch_google_identity_mock):
        AppUser.objects.create(
            email='marta@example.com',
            name='Old',
            surname='Name',
            photo_url='https://example.com/old.png',
        )

        fetch_google_identity_mock.return_value = GoogleIdentity(
            sub='google-sub-1',
            email='marta@example.com',
            email_verified=True,
            given_name='Marta',
            family_name='Valerie',
            full_name='Marta Valerie',
            picture='https://example.com/new.png',
            locale='uk',
            aud='client-id-1',
            azp='client-id-1',
        )

        response = self.client.post(
            reverse('auth-google'),
            {'id_token': 'fake-google-token'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_new_user'])

        user = AppUser.objects.get(email='marta@example.com')
        self.assertEqual(user.name, 'Marta')
        self.assertEqual(user.surname, 'Valerie')
        self.assertEqual(user.photo_url, 'https://example.com/new.png')

    @patch('core.viewsets.fetch_google_identity')
    def test_returns_400_when_google_validation_fails(self, fetch_google_identity_mock):
        fetch_google_identity_mock.side_effect = GoogleAuthError('Google token audience is not allowed')

        response = self.client.post(
            reverse('auth-google'),
            {'id_token': 'bad-token'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Google token audience is not allowed')
