#!/bin/bash

echo "=== Collecting Static Files ==="
python manage.py collectstatic --noinput || echo "Collectstatic failed, continuing..."

echo "=== Running Migrations ==="
python manage.py migrate

echo "=== Creating Admin ==="
python manage.py create_admin && echo "Admin OK" || echo "Admin failed, continuing..."

echo "=== Testing WSGI Import ==="
python -c "from sms_project.wsgi import application; print('WSGI OK')"

echo "=== Starting Gunicorn ==="
exec gunicorn sms_project.wsgi:application \
    --bind 0.0.0.0:${PORT:-8080} \
    --workers 1 \
    --timeout 120 \
    --log-level debug \
    --access-logfile - \
    --error-logfile -
