 
from django.test import TestCase, Client
from accounts.models import User


class StudentTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin1',
            password='adminpass123',
            full_name='Admin User',
            role='admin',
        )
        self.client.login(username='admin1', password='adminpass123')

    def test_file_list_page(self):
        response = self.client.get('/files/')
        self.assertEqual(response.status_code, 200)

    def test_upload_page(self):
        response = self.client.get('/upload/')
        self.assertEqual(response.status_code, 200)