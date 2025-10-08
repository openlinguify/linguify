# config/settings/production.py

"""
Configuration pour l'environnement de PRODUCTION.
⚠️ NE JAMAIS committer les valeurs sensibles !
Utiliser des variables d'environnement.
"""

from .base import *
import os

# SECURITY: Debug MUST be False in production
DEBUG = False

# SECRET_KEY depuis variable d'environnement
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY environment variable must be set!")

# Hosts autorisés - TRÈS IMPORTANT pour la sécurité
ALLOWED_HOSTS = [
    'votre-domaine.com',
    'www.votre-domaine.com',
    'api.votre-domaine.com',
]

# Base de données - PostgreSQL en production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'CONN_MAX_AGE': 600,  # Connexions persistantes
        'OPTIONS': {
            'sslmode': 'require',  # SSL obligatoire
        }
    }
}

# Cache - Redis en production (performance)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
        }
    }
}

# Sessions dans Redis (plus rapide que DB)
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Email - SMTP réel en production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')

# CORS - Restreint aux domaines autorisés
CORS_ALLOWED_ORIGINS = [
    'https://votre-domaine.com',
    'https://www.votre-domaine.com',
]
CORS_ALLOW_CREDENTIALS = True

# Static files - Servir par CDN ou serveur web (Nginx)
STATIC_ROOT = '/var/www/static/'
STATIC_URL = 'https://cdn.votre-domaine.com/static/'

MEDIA_ROOT = '/var/www/media/'
MEDIA_URL = 'https://cdn.votre-domaine.com/media/'

# Whitenoise pour servir les static files (si pas de CDN)
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# SÉCURITÉ - TRÈS IMPORTANT EN PRODUCTION
SECURE_SSL_REDIRECT = True  # Rediriger HTTP vers HTTPS
SESSION_COOKIE_SECURE = True  # Cookies HTTPS uniquement
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # HSTS pour 1 an
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'

# Logging en production - Fichiers + Sentry
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/django/app.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/django/error.log',
            'maxBytes': 1024 * 1024 * 15,
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Sentry pour tracking des erreurs (optionnel mais recommandé)
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,  # 10% des transactions
    send_default_pii=False,  # Ne pas envoyer d'infos personnelles
    environment='production',
)

# Performance
CONN_MAX_AGE = 600  # Connexions DB persistantes
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB max upload

print("🚀 Mode PRODUCTION activé")
print(f"🌐 ALLOWED_HOSTS: {ALLOWED_HOSTS}")
print(f"🗄️  Database: PostgreSQL")
print(f"⚡ Cache: Redis")