 
from django.test import TestCase, Client
from accounts.models import User


class StaffTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin1',
            password='adminpass123',
            full_name='Admin User',
            role='admin',
        )
        self.client.login(username='admin1', password='adminpass123')

    def test_teacher_list(self):
        response = self.client.get('/teachers/')
        self.assertEqual(response.status_code, 200)

    def test_guardian_list(self):
        response = self.client.get('/guardians/')
        self.assertEqual(response.status_code, 200)

    def test_hod_list(self):
        response = self.client.get('/hods/')
        self.assertEqual(response.status_code, 200)