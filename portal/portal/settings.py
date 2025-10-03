"""
Django settings for portal project.
"""

import os
import sys
from pathlib import Path
import environ

# Add backend to Python path to access authentication app
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent / 'backend'
if BACKEND_DIR.exists():
    sys.path.insert(0, str(BACKEND_DIR))
    # Also add backend/apps to access authentication directly
    sys.path.insert(0, str(BACKEND_DIR / 'apps'))

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Add portal base directory to Python path for core apps
sys.path.insert(0, str(BASE_DIR))

# Initialize environ
env = environ.Env(
    DEBUG=(bool, False),
)

# Read environment variables from .env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'), encoding='utf-8')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='django-insecure-portal-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=True)

# Environment detection
django_env = env('DJANGO_ENV', default='development')
is_production = django_env == 'production'

# Force production settings if DEBUG=False
if not DEBUG:
    is_production = True

if is_production:
    ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['openlinguify.com', 'www.openlinguify.com', 'linguify-kdot.onrender.com'])
else:
    ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '.openlinguify.com', 'testserver']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',  # For SEO sitemap generation
    'authentication',  # Custom User model from backend (read-only access)
    'core.seo',        # SEO management system
    'public_web',  # Notre app principale pour le portail
    'core.blog',       # App blog déplacée du backend
    'core.jobs',       # App jobs déplacée du backend
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.gzip.GZipMiddleware',  # Compression gzip
    'public_web.middleware.CacheControlMiddleware',  # Cache headers
    'public_web.middleware.SecurityHeadersMiddleware',  # Security headers
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'public_web.middleware.BackendSessionMiddleware',  # Détection session backend
]

ROOT_URLCONF = 'portal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'public_web.context_processors.app_urls',
                'public_web.context_processors.backend_user',
            ],
        },
    },
]

WSGI_APPLICATION = 'portal.wsgi.application'

# Database configuration
database_url = env('DATABASE_URL', default=None)

if database_url:
    # Production - Use DATABASE_URL from Render
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(database_url)
    }
else:
    # Development - Local PostgreSQL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('DB_NAME'),
            'USER': env('DB_USER'),
            'PASSWORD': env('DB_PASSWORD'),
            'HOST': env('DB_HOST'),
            'PORT': env('DB_PORT'),
        }
    }

# Authentication - Use same custom User model as backend
AUTH_USER_MODEL = 'authentication.User'

# Internationalization
LANGUAGE_CODE = 'en'

LANGUAGES = [
    ('en', 'English'),
    ('fr', 'Français'),
    ('es', 'Español'),
    ('nl', 'Nederlands'),
]

LOCALE_PATHS = [
    BASE_DIR / 'public_web' / 'i18n',
]

TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    # BASE_DIR / 'static',  # This directory doesn't exist, removed to fix warnings
]

# Static files finders (ensure app static files are found)
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# WhiteNoise configuration for production
if is_production:
    # Use StaticFilesStorage to avoid compression issues causing 0-byte files
    STATICFILES_STORAGE = 'whitenoise.storage.StaticFilesStorage'

    # WhiteNoise settings to ensure proper file serving
    WHITENOISE_USE_FINDERS = True
    WHITENOISE_AUTOREFRESH = True

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Cache configuration for performance
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# Cache middleware settings
CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 600  # 10 minutes
CACHE_MIDDLEWARE_KEY_PREFIX = 'portal'

# Session optimization
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_NAME = 'sessionid'
SESSION_COOKIE_AGE = 86400  # 1 jour
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
# Share cookies across all openlinguify.com subdomains (app, www, etc.)
if not DEBUG:
    SESSION_COOKIE_DOMAIN = '.openlinguify.com'
    CSRF_COOKIE_DOMAIN = '.openlinguify.com'

# URLs des différents produits Linguify
LINGUIFY_PRODUCTS = {
    'backend': {
        'name': 'Linguify Particulier',
        'description': 'For all students',
        'dev_url': 'http://127.0.0.1:8081',
        'prod_url': 'https://app.openlinguify.com',
        'icon': 'fas fa-user',
    },
    'cms': {
        'name': 'Linguify Professionnel',
        'description': 'Pour les enseignants et créateurs de contenu',
        'dev_url': 'http://127.0.0.1:8002',
        'prod_url': 'https://cms.openlinguify.com',
        'icon': 'fas fa-chalkboard-teacher',
    },
    'lms': {
        'name': 'Linguify LMS',
        'description': 'Pour les institutions éducatives',
        'dev_url': 'http://127.0.0.1:8001',
        'prod_url': 'https://lms.openlinguify.com',
        'icon': 'fas fa-university',
    },
    # Futurs produits peuvent être ajoutés ici
    # 'enterprise': {
    #     'name': 'Linguify Enterprise',
    #     'description': 'Pour les entreprises',
    #     'dev_url': 'http://127.0.0.1:8002',
    #     'prod_url': 'https://enterprise.openlinguify.com',
    #     'icon': 'fas fa-building',
    # },
}

# Email configuration
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')
CONTACT_EMAIL = env('CONTACT_EMAIL')

# Email backend for development/production
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = env('EMAIL_HOST', default='')
    EMAIL_PORT = env.int('EMAIL_PORT', default=587)
    EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
    EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)