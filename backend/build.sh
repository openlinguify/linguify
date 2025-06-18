#!/bin/bash
# Build script for Render deployment

echo "🚀 Starting Render build process..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Compile translations
echo "🌍 Compiling translations..."
python manage.py compilemessages

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
echo "🗄️ Running migrations..."
python manage.py migrate

echo "✅ Build complete!"