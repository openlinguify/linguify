"""
Django settings for portal project.
"""

import os
from pathlib import Path
import environ

print("🌐 Loading Portal Settings...")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

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
    'public_web',  # Notre app principale pour le portail
    'blog',       # App blog déplacée du backend
    'jobs',       # App jobs déplacée du backend
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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
    print("📊 Using Render PostgreSQL (Portal)")
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
    print("📊 Using local PostgreSQL (Portal)")

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

# URLs des différents produits Linguify
LINGUIFY_PRODUCTS = {
    'backend': {
        'name': 'Linguify Particulier',
        'description': 'For all students',
        'dev_url': 'http://127.0.0.1:8000',
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