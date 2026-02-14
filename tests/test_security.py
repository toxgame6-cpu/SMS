 
from django.test import TestCase, Client
from accounts.models import User, AccountLockout


class SecurityTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123',
            full_name='Test User', role='admin',
        )

    def test_account_lockout_after_failed_attempts(self):
        for i in range(5):
            self.client.post('/', {
                'username': 'testuser',
                'password': 'wrongpassword',
                'role': 'admin',
            })

        lockout = AccountLockout.objects.get(username='testuser')
        self.assertEqual(lockout.failed_attempts, 5)
        self.assertIsNotNone(lockout.locked_until)

    def test_lockout_resets_on_success(self):
        # Create some failed attempts
        for i in range(3):
            self.client.post('/', {
                'username': 'testuser',
                'password': 'wrongpassword',
                'role': 'admin',
            })

        # Successful login
        self.client.post('/', {
            'username': 'testuser',
            'password': 'testpass123',
            'role': 'admin',
        })

        lockout = AccountLockout.objects.get(username='testuser')
        self.assertEqual(lockout.failed_attempts, 0)