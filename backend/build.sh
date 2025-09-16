#!/bin/bash
# Build script for Render deployment

echo "🚀 Starting Render build process..."

# Set Django settings module for production
export DJANGO_SETTINGS_MODULE=core.settings

# Skip Poetry completely and use requirements.txt directly
echo "📦 Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Double-check critical dependencies
echo "🔧 Ensuring critical dependencies are installed..."
pip install --upgrade stripe==11.1.0 gunicorn==23.0.0 Django==5.1.10

# Verify key dependencies are installed
echo "🔍 Verifying critical dependencies..."
python -c "import django; print(f'✅ Django {django.get_version()} installed successfully')"
python -c "import stripe; print(f'✅ Stripe {stripe.__version__} installed successfully')"
python -c "import gunicorn; print(f'✅ Gunicorn installed successfully')"

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