#!/bin/bash
set -e

echo "==> Portal Start Script Starting..."

# Set Django settings
export DJANGO_SETTINGS_MODULE=portal.settings

# Verify Django can start
echo "==> Verifying Django configuration..."
python manage.py check --deploy

# Start Gunicorn
echo "==> Starting Gunicorn server..."
exec gunicorn portal.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --timeout 60 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --preload \
    --access-logfile - \
    --error-logfile -