from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()


class UserRegistrationTest(APITestCase):
    def test_user_registration(self):
        url = reverse('api:users-list')
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpassword'
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())
        self.assertIn('email', response.data)


class UserAuthenticationTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='testuser@example.com', password='testpassword', username='tessst')
        self.url = reverse('api:login')

    def test_user_authentication(self):
        data = {
            'email': 'testuser@example.com',
            'password': 'testpassword'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('auth_token', response.data)


class PasswordChangeTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='old_password')
        self.user.save()
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def test_password_change(self):
        url = reverse('api:users-set-password')

        data = {
            'current_password': 'old_password',
            'new_password': 'new_password123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('new_password123'))


class UserListTest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser1', email='testuser1@example.com',
                                              password='password123')
        self.user2 = User.objects.create_user(username='testuser2', email='testuser2@example.com',
                                              password='password123')
        self.token = Token.objects.create(user=self.user1)
        self.api_authentication()

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_user_list(self):
        url = reverse('api:users-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)
