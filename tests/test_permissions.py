 
from django.test import TestCase, Client
from accounts.models import User


class PermissionTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin1', password='adminpass123',
            full_name='Admin User', role='admin',
        )
        self.teacher = User.objects.create_user(
            username='teacher1', password='teacherpass123',
            full_name='Teacher User', role='teacher',
        )

    def test_teacher_cannot_access_admin_panel(self):
        self.client.login(username='teacher1', password='teacherpass123')
        response = self.client.get('/admin-panel/')
        self.assertEqual(response.status_code, 302)

    def test_admin_can_access_admin_panel(self):
        self.client.login(username='admin1', password='adminpass123')
        response = self.client.get('/admin-panel/')
        self.assertEqual(response.status_code, 200)