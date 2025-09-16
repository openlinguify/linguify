#!/bin/bash
# Build script for Render deployment

echo "🚀 Starting Render build process..."

# Set Django settings module for production
export DJANGO_SETTINGS_MODULE=core.settings

# Install Poetry if not available
echo "📝 Setting up Poetry..."
pip install poetry

# Configure Poetry for Render
echo "⚙️ Configuring Poetry..."
poetry config virtualenvs.create false
poetry config virtualenvs.in-project false

# Install dependencies with Poetry
echo "📦 Installing dependencies with Poetry..."
poetry install --only=main --no-root

# Verify Django is installed
echo "🔍 Verifying Django installation..."
python -c "import django; print(f'Django {django.get_version()} installed successfully')"

# Compile translations
echo "🌍 Compiling translations..."
python manage.py compilemessages

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Make migrations (don't assume they exist)
echo "🗂️ Making migrations..."
python manage.py makemigrations

# Run migrations with fake-initial for first deploy
echo "🗄️ Running migrations..."
python manage.py migrate --fake-initial

echo "✅ Build complete!"