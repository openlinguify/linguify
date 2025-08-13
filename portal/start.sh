#!/bin/bash
set -e

echo "==> Portal Start Script Starting..."
echo "==> PORT: $PORT"
echo "==> DJANGO_ENV: $DJANGO_ENV"

# Set Django settings
export DJANGO_SETTINGS_MODULE=portal.settings

# Verify Django can start
echo "==> Verifying Django configuration..."
python3 manage.py check

# Only run deployment checks in production
if [ "$DJANGO_ENV" = "production" ]; then
    echo "==> Running production deployment checks..."
    python3 manage.py check --deploy
fi

# Calculate workers based on available CPU (with min 1, max 4)
WORKERS=$(python3 -c "import os; print(max(1, min(4, (os.cpu_count() or 1) * 2 + 1)))")
echo "==> Starting Gunicorn with $WORKERS workers..."

# Start Gunicorn with improved configuration
exec gunicorn portal.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers $WORKERS \
    --worker-class sync \
    --worker-connections 1000 \
    --timeout 120 \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --preload \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --capture-output