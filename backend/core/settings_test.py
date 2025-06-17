"""
Django settings for testing
"""
import os

# Set required environment variables for testing BEFORE importing settings
os.environ.setdefault('SECRET_KEY', 'test-secret-key-for-testing-only')
os.environ.setdefault('DEBUG', 'True')
os.environ.setdefault('ALLOWED_HOSTS', 'localhost,127.0.0.1')
os.environ.setdefault('DB_NAME', 'test_db')
os.environ.setdefault('DB_USER', 'postgres')
os.environ.setdefault('DB_PASSWORD', 'postgres')
os.environ.setdefault('DB_HOST', 'localhost')
os.environ.setdefault('DB_PORT', '5432')

# Supabase test configuration
os.environ.setdefault('SUPABASE_URL', 'https://test.supabase.co')
os.environ.setdefault('SUPABASE_ANON_KEY', 'test-anon-key')
os.environ.setdefault('SUPABASE_SERVICE_ROLE_KEY', 'test-service-role-key')
os.environ.setdefault('SUPABASE_PROJECT_ID', 'test-project-id')
os.environ.setdefault('SUPABASE_JWT_SECRET', 'test-jwt-secret')

# Auth0 test configuration
os.environ.setdefault('AUTH0_DOMAIN', 'test.auth0.com')
os.environ.setdefault('AUTH0_CLIENT_ID', 'test-client-id')
os.environ.setdefault('AUTH0_CLIENT_SECRET', 'test-client-secret')
os.environ.setdefault('AUTH0_AUDIENCE', 'https://test-api')

# Other optional environment variables
os.environ.setdefault('REDIS_URL', 'redis://localhost:6379/1')
os.environ.setdefault('OPENAI_API_KEY', 'test-openai-key')
os.environ.setdefault('STRIPE_PUBLIC_KEY', 'pk_test_123')
os.environ.setdefault('STRIPE_SECRET_KEY', 'sk_test_123')
os.environ.setdefault('EMAIL_HOST', 'localhost')
os.environ.setdefault('EMAIL_PORT', '587')
os.environ.setdefault('EMAIL_HOST_USER', 'test@example.com')
os.environ.setdefault('EMAIL_HOST_PASSWORD', 'test-password')
os.environ.setdefault('DEFAULT_FROM_EMAIL', 'noreply@test.com')
os.environ.setdefault('FRONTEND_URL', 'http://localhost:3000')
os.environ.setdefault('BACKEND_URL', 'http://localhost:8000')

from .settings import *

# Use in-memory SQLite for tests to avoid PostgreSQL issues
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Speed up password hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable caching for tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

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

# Test specific settings
TEST_RUNNER = 'django.test.runner.DiscoverRunner'
TEST_CHARSET = None
TEST_COLLATION = None
TEST_DEPENDENCIES = {}
TEST_MIRROR = None
TEST_NAME = None
TEST_SERIALIZE = True
TEST_CREATE_DB = True