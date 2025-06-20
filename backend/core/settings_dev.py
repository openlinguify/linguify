# Development settings override
import os
from .settings import *

# TEMPORARY: Enable authentication bypass for development
BYPASS_AUTH_FOR_DEVELOPMENT = True

# This will make the Supabase authentication return a fake user
# Remove this in production!
print("⚠️  WARNING: Authentication bypass is enabled for development!")
print("⚠️  This should NEVER be used in production!")

# ===== IMPORTANT: Database Configuration =====
# Use local PostgreSQL for development instead of production Supabase
if os.environ.get('USE_LOCAL_DB', 'True') == 'True':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('LOCAL_DB_NAME', 'linguify_dev'),
            'USER': os.environ.get('LOCAL_DB_USER', 'postgres'),
            'PASSWORD': os.environ.get('LOCAL_DB_PASSWORD', 'postgres'),
            'HOST': os.environ.get('LOCAL_DB_HOST', 'localhost'),
            'PORT': os.environ.get('LOCAL_DB_PORT', '5432'),
        }
    }
    print("🔧 Using LOCAL database for development")
else:
    print("⚠️  Using PRODUCTION database - Be careful!")

# ===== Development-Only Apps =====
# Apps that should NOT be available in production yet
DEVELOPMENT_ONLY_APPS = [
    'apps.community',  # Still in development - DO NOT DEPLOY
]

# Feature flags for apps in development
FEATURE_FLAGS = {
    'COMMUNITY_ENABLED': True,  # Only in dev
    'SOCIAL_FEATURES': True,    # Only in dev
}

# ===== Debug Configuration =====
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver', '.ngrok.io']

# ===== Email Configuration for Dev =====
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ===== Disable Caching in Development =====
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# ===== Media Files =====
MEDIA_ROOT = os.path.join(BASE_DIR, 'media_dev')  # Separate from production
MEDIA_URL = '/media/'

# ===== Debug Toolbar (if installed) =====
if 'debug_toolbar' in INSTALLED_APPS:
    INTERNAL_IPS = ['127.0.0.1', 'localhost']

print("="*50)
print("🚀 DEVELOPMENT ENVIRONMENT ACTIVE")
print("📊 Database:", DATABASES['default']['NAME'])
print("🔧 Debug Mode:", DEBUG)
print("⚠️  Community App:", 'ENABLED' if 'apps.community' in INSTALLED_APPS else 'DISABLED')
print("="*50)