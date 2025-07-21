"""
Django settings for portal project.
"""

import os
from pathlib import Path

print("🌐 Loading Portal Settings...")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-portal-change-this-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '.openlinguify.com']

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
    'docs',       # Documentation intégrée
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
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

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'db_linguify_portal',
        'USER': 'postgres',
        'PASSWORD': 'azerty',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Internationalization
LANGUAGE_CODE = 'fr'

LANGUAGES = [
    ('fr', 'Français'),
    ('en', 'English'),
    ('es', 'Español'),
    ('nl', 'Nederlands'),
]

TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# URLs des différents produits Linguify
LINGUIFY_PRODUCTS = {
    'backend': {
        'name': 'Linguify Particulier',
        'description': 'Pour les apprenants individuels',
        'dev_url': 'http://127.0.0.1:8000',
        'prod_url': 'https://app.openlinguify.com',
        'icon': 'fas fa-user',
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