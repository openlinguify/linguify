#!/bin/bash
set -e

echo "==> Portal Build Script Starting..."
echo "==> Python version: $(python3 --version)"
echo "==> Current directory: $(pwd)"
echo "==> Available environment variables:"
env | grep -E "(PYTHON|DJANGO|DEBUG|SECRET|DATABASE|ALLOWED)" | sort

# Upgrade pip first
echo "==> Upgrading pip..."
python3 -m pip install --upgrade pip

# Try Poetry first, fallback to pip if needed
if command -v poetry &> /dev/null; then
    echo "==> Poetry found, using Poetry for dependencies..."
    
    # Configure Poetry for Render
    poetry config virtualenvs.create false
    poetry config virtualenvs.in-project false
    
    # Install dependencies with Poetry
    poetry install --only=main --no-interaction --no-ansi
else
    echo "==> Poetry not found, installing via pip..."
    python3 -m pip install poetry
    
    # Configure Poetry
    poetry config virtualenvs.create false
    poetry config virtualenvs.in-project false
    
    # Try Poetry install, fallback to requirements.txt
    if ! poetry install --only=main --no-interaction --no-ansi; then
        echo "==> Poetry install failed, falling back to requirements.txt..."
        python3 -m pip install -r requirements.txt
    fi
fi

# Set Django settings module
export DJANGO_SETTINGS_MODULE=portal.settings

# Validate environment variables
echo "==> Validating environment..."
python3 validate_env.py

# Verify Django installation and configuration
echo "==> Verifying Django installation..."
python3 -c "import django; print(f'Django {django.get_version()} imported successfully')"

echo "==> Verifying Django configuration..."
python3 manage.py check --verbosity=2

# Only run deployment checks if not in development
if [ "$DJANGO_ENV" = "production" ]; then
    echo "==> Running deployment-specific checks..."
    python3 manage.py check --deploy --verbosity=1
fi

# Collect static files
echo "==> Collecting static files..."
python3 manage.py collectstatic --noinput --verbosity=1

# Skip migrations - database is managed by backend service
echo "==> Skipping database migrations (managed by backend service)..."

# Verify the build worked
echo "==> Final verification..."
python3 -c "
import django
django.setup()
from django.conf import settings
print(f'DEBUG: {settings.DEBUG}')
print(f'ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}')
print(f'DATABASES configured: {bool(settings.DATABASES)}')
print('✅ Django configuration verified')
"

echo "==> Portal build completed successfully!"