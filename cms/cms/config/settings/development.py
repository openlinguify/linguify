# config/settings/development.py

"""
Configuration pour l'environnement de DÉVELOPPEMENT.
Utiliser : python manage.py runserver --settings=config.settings.development
"""

from .base import *
import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECRET_KEY pour dev (pas grave si elle est exposée)
SECRET_KEY = 'django-insecure-dev-key-change-this-in-production-123456789'

# Hosts autorisés en développement
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
]

# Base de données - SQLite pour développement (simple et rapide)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# OU PostgreSQL local si vous préférez
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'language_learning_dev',
#         'USER': 'postgres',
#         'PASSWORD': 'postgres',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }

# Cache - Simple en mémoire pour dev
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Email - Console backend (affiche les emails dans la console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CORS - Très permissif en dev
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Static files - Servir directement par Django (pas optimal mais simple)
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Django Debug Toolbar (super utile en dev)
INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = [
    '127.0.0.1',
]

# Logging plus verbeux en dev
LOGGING['root']['level'] = 'DEBUG'

# Désactiver certaines sécurités pour faciliter le dev
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Django Extensions (shell_plus, runserver_plus, etc.)
INSTALLED_APPS += [
    'django_extensions',
]

# Afficher les requêtes SQL dans la console (utile pour debug)
LOGGING['loggers'] = {
    'django.db.backends': {
        'level': 'DEBUG',
        'handlers': ['console'],
    }
}

print("🔧 Mode DÉVELOPPEMENT activé")
print(f"📁 BASE_DIR: {BASE_DIR}")
print(f"🗄️  Database: SQLite (db.sqlite3)")