#!/bin/bash

echo "=== Collecting Static Files ==="
python manage.py collectstatic --noinput

echo "=== Running Migrations ==="
python manage.py migrate

echo "=== Creating Admin ==="
python manage.py create_admin && echo "Admin created" || echo "Admin creation failed, continuing..."

echo "=== Starting Gunicorn on port ${PORT:-8080} ==="
exec gunicorn sms_project.wsgi:application \
    --bind 0.0.0.0:${PORT:-8080} \
    --workers 2 \
    --timeout 120 \
    --log-level info \
    --access-logfile - \
    --error-logfile -