from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from app.logger import log

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')

TOKEN_URL = reverse('user:token')


def create_user(**params):
    log.debug(params)
    return get_user_model().objects.create_user(**params)


class PublicUserAPITest(TestCase):
    """ wat """

    def setUp(self):
        self.client = APIClient()
        self.std_payload = {
            'email': 'wat@wat.com',
            'password': 'pwd1234',
            'name': 'Test User'
        }

    def test_create_valid_user(self):
        payload = {
            'email': 'wat@wat2.com',
            'password': 'pwd111',
            'name': 'Test User'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_no_dup_user_creation(self):
        payload = {
            'email': 'wat@wat.com',
            'password': 'pwd76765',
            'name': 'Test User'
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        payload = {
            'email': 'wat1@wat.com',
            'password': 'pwd',
            'name': 'Test User'
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        # create_user(email='wat@wat.com',password='pass234')
        res = self.client.post(CREATE_USER_URL, self.std_payload)
        res = self.client.post(TOKEN_URL, self.std_payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_create_token_for_user_bad_cred(self):
        create_user(email='wat@wat.com', password='testpass')
        res = self.client.post(TOKEN_URL, self.std_payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_for_no_user(self):
        res = self.client.post(TOKEN_URL, self.std_payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_for_user_missing_data(self):
        create_user(email='wat@wat.com', password='testpass')
        res = self.client.post(TOKEN_URL, {'email:': 'oone', 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
