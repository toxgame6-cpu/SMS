 
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User


class LoginTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testadmin',
            password='testpass123',
            full_name='Test Admin',
            role='admin',
        )

    def test_login_page_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        response = self.client.post('/', {
            'username': 'testadmin',
            'password': 'testpass123',
            'role': 'admin',
        })
        self.assertEqual(response.status_code, 302)

    def test_login_wrong_password(self):
        response = self.client.post('/', {
            'username': 'testadmin',
            'password': 'wrongpass',
            'role': 'admin',
        })
        self.assertEqual(response.status_code, 200)

    def test_login_wrong_role(self):
        response = self.client.post('/', {
            'username': 'testadmin',
            'password': 'testpass123',
            'role': 'teacher',
        })
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        self.client.login(username='testadmin', password='testpass123')
        response = self.client.get('/logout/')
        self.assertEqual(response.status_code, 302)

    def test_unauthenticated_redirect(self):
        response = self.client.get('/admin-panel/')
        self.assertEqual(response.status_code, 302)