#!/bin/bash
set -e

echo "=== Starting Application ==="
echo "PORT = $PORT"

echo "=== Running Migrations ==="
python manage.py migrate 2>&1 || echo "Migration failed but continuing..."

echo "=== Creating Admin ==="
python manage.py create_admin 2>&1 || echo "Create admin failed but continuing..."

echo "=== Starting Gunicorn on port ${PORT:-8080} ==="
exec gunicorn sms_project.wsgi:application \
    --bind 0.0.0.0:${PORT:-8080} \
    --workers 2 \
    --timeout 120 \
    --log-level info \
    --access-logfile - \
    --error-logfile -