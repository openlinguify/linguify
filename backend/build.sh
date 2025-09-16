#!/bin/bash
set -e

echo "==> Backend Build Script Starting..."
echo "==> Python version: $(python3 --version)"
echo "==> Current directory: $(pwd)"

# Upgrade pip first
echo "==> Upgrading pip..."
python3 -m pip install --upgrade pip

# Install dependencies directly from requirements.txt
echo "==> Installing dependencies from requirements.txt..."
python3 -m pip install -r requirements.txt

# Set Django settings module
export DJANGO_SETTINGS_MODULE=core.settings

# Verify Django installation
echo "==> Verifying Django installation..."
python3 -c "import django; print(f'Django {django.get_version()} imported successfully')"

# Verify critical dependencies
echo "==> Verifying critical dependencies..."
python3 -c "import stripe; print('✅ Stripe installed')"
python3 -c "import environ; print('✅ django-environ installed')"
python3 -c "import gunicorn; print('✅ Gunicorn installed')"

# Check Django configuration
echo "==> Checking Django configuration..."
python3 manage.py check --verbosity=2

# Compile translation messages
echo "==> Compiling translation messages..."
python3 manage.py compilemessages --verbosity=1

# Collect static files
echo "==> Collecting static files..."
rm -rf staticfiles/*
python3 manage.py collectstatic --noinput --verbosity=1

# Run migrations
echo "==> Running database migrations..."
python3 manage.py migrate --fake-initial

echo "==> Backend build completed successfully!"