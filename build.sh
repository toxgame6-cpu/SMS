#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "===== Installing dependencies ====="
pip install -r requirements.txt

echo "===== Collecting static files ====="
python manage.py collectstatic --noinput

echo "===== Running migrations ====="
python manage.py migrate

echo "===== Creating superuser if needed ====="
python manage.py shell -c "
from accounts.models import User
if not User.objects.filter(role='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@smsportal.com',
        password='Admin@123456',
        full_name='System Administrator',
        role='admin'
    )
    print('Admin user created: admin / Admin@123456')
else:
    print('Admin user already exists')
" || echo "Superuser creation skipped"

echo "===== Build complete ====="