 
from django.test import TestCase, Client
from accounts.models import User


class NotificationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin1', password='adminpass123',
            full_name='Admin User', role='admin',
        )

    def test_notification_list(self):
        self.client.login(username='admin1', password='adminpass123')
        response = self.client.get('/notifications/')
        self.assertEqual(response.status_code, 200)