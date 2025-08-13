#!/bin/bash
set -e

echo "==> Portal Build Script Starting..."

# Install Poetry if not available
if ! command -v poetry &> /dev/null; then
    echo "==> Installing Poetry..."
    pip install --upgrade pip
    pip install poetry
fi

# Configure Poetry
echo "==> Configuring Poetry..."
poetry config virtualenvs.create false
poetry config virtualenvs.in-project false

# Install dependencies
echo "==> Installing dependencies..."
poetry install --no-dev --no-interaction --no-ansi

# Set Django settings
export DJANGO_SETTINGS_MODULE=portal.settings

# Validate environment variables
echo "==> Validating environment..."
python validate_env.py

# Verify Django can import
echo "==> Verifying Django installation..."
python -c "import django; print(f'Django {django.get_version()} imported successfully')"

# Verify Django configuration
echo "==> Verifying Django configuration..."
python manage.py check --deploy --verbosity=1

# Run Django management commands
echo "==> Collecting static files..."
python manage.py collectstatic --noinput --verbosity=2

echo "==> Running database migrations..."
python manage.py migrate --verbosity=2

echo "==> Portal build completed successfully!"