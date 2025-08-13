#!/bin/bash
set -e

echo "==> Fallback Build Script (pip-only) Starting..."
echo "==> Python version: $(python3 --version)"
echo "==> Current directory: $(pwd)"

# Upgrade pip first
echo "==> Upgrading pip..."
python3 -m pip install --upgrade pip

# Install dependencies from requirements.txt
echo "==> Installing dependencies from requirements.txt..."
python3 -m pip install -r requirements.txt

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

# Run database migrations
echo "==> Running database migrations..."
python3 manage.py migrate --verbosity=1

echo "==> Fallback build completed successfully!"