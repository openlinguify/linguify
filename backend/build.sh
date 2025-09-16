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