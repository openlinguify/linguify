#!/bin/bash
# Build script for Render deployment

echo "🚀 Starting Render build process..."

# Set Django settings module for production
export DJANGO_SETTINGS_MODULE=core.settings

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Compile translations
echo "🌍 Compiling translations..."
python manage.py compilemessages --settings=core.settings

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --settings=core.settings

# Run migrations
echo "🗄️ Running migrations..."
python manage.py migrate --settings=core.settings

echo "✅ Build complete!"