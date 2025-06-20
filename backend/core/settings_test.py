"""
Django settings for testing
"""
import os

# Set DJANGO_ENV to 'test' to avoid fallback configuration
os.environ.setdefault('DJANGO_ENV', 'test')

# Set required environment variables for testing BEFORE importing settings
os.environ.setdefault('SECRET_KEY', 'test-secret-key-for-testing-only')
os.environ.setdefault('DEBUG', 'True')
os.environ.setdefault('ALLOWED_HOSTS', 'localhost,127.0.0.1,testserver')
os.environ.setdefault('DB_NAME', 'db_linguify_test')
os.environ.setdefault('DB_USER', 'postgres')
os.environ.setdefault('DB_PASSWORD', 'azerty')
os.environ.setdefault('DB_HOST', 'localhost')
os.environ.setdefault('DB_PORT', '5432')

# Supabase test configuration
os.environ.setdefault('SUPABASE_URL', 'https://test.supabase.co')
os.environ.setdefault('SUPABASE_ANON_KEY', 'test-anon-key')
os.environ.setdefault('SUPABASE_SERVICE_ROLE_KEY', 'test-service-role-key')
os.environ.setdefault('SUPABASE_PROJECT_ID', 'test-project-id')
os.environ.setdefault('SUPABASE_JWT_SECRET', 'test-jwt-secret')

# Supabase Database test configuration
os.environ.setdefault('USE_SUPABASE_DB', 'False')  # Force SQLite for tests
os.environ.setdefault('SUPABASE_DB_NAME', 'postgres')
os.environ.setdefault('SUPABASE_DB_USER', 'test-user')
os.environ.setdefault('SUPABASE_DB_PASSWORD', 'test-password')
os.environ.setdefault('SUPABASE_DB_HOST', 'localhost')
os.environ.setdefault('SUPABASE_DB_PORT', '6543')

# Auth0 configuration removed - using Django authentication only

# Other optional environment variables
os.environ.setdefault('REDIS_URL', 'redis://localhost:6379/1')
os.environ.setdefault('OPENAI_API_KEY', 'test-openai-key')
os.environ.setdefault('STRIPE_PUBLIC_KEY', 'pk_test_123')
os.environ.setdefault('STRIPE_SECRET_KEY', 'sk_test_123')
os.environ.setdefault('EMAIL_HOST', 'localhost')
os.environ.setdefault('EMAIL_PORT', '587')
os.environ.setdefault('EMAIL_HOST_USER', 'test@example.com')
os.environ.setdefault('EMAIL_HOST_PASSWORD', 'test-password')
os.environ.setdefault('EMAIL_USE_TLS', 'True')
os.environ.setdefault('DEFAULT_FROM_EMAIL', 'noreply@test.com')
os.environ.setdefault('FRONTEND_URL', 'http://localhost:3000')
os.environ.setdefault('BACKEND_URL', 'http://localhost:8000')

from .settings import *

# Use PostgreSQL for tests to match production environment
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'db_linguify_test'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'azerty'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'ATOMIC_REQUESTS': True,
        'TEST': {
            'NAME': 'test_linguify_temp',
        },
    }
}

# Ensure ATOMIC_REQUESTS is set for all databases
for db_config in DATABASES.values():
    db_config.setdefault('ATOMIC_REQUESTS', True)

# Keep migrations enabled for PostgreSQL tests to ensure proper schema

# Speed up password hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Use locmem cache for tests to support sessions
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'test-cache',
    }
}

# Use database session backend for tests
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Disable email backend for tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Use a simple secret key for tests
SECRET_KEY = 'test-secret-key-for-testing-only'

# Disable debug toolbar and other dev tools for tests
INSTALLED_APPS = [app for app in INSTALLED_APPS if 'debug_toolbar' not in app]

# Disable logging during tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
    },
}

# Disable i18n for faster tests
USE_I18N = False
USE_L10N = False

# Remove whitenoise middleware for tests to avoid import errors
MIDDLEWARE = [m for m in MIDDLEWARE if 'whitenoise' not in m.lower()]

# Simplified static files configuration for tests
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Test specific settings
TEST_RUNNER = 'django.test.runner.DiscoverRunner'
TEST_CHARSET = None
TEST_COLLATION = None
TEST_DEPENDENCIES = {}
TEST_MIRROR = None
TEST_NAME = None
TEST_SERIALIZE = True
TEST_CREATE_DB = True