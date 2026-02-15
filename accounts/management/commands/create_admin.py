from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = 'Create default admin user'

    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@smsportal.com',
                password='Admin@123456',
                full_name='System Administrator',
                role='admin',
            )
            self.stdout.write(self.style.SUCCESS(
                'Admin created: admin / Admin@123456'
            ))
        else:
            self.stdout.write(self.style.WARNING('Admin already exists'))