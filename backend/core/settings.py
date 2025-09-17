# backend/core/settings.py
import sys
from pathlib import Path
import os
import environ
from datetime import timedelta
import logging
logger = logging.getLogger(__name__)


sys.path.insert(0, os.path.join(Path(__file__).resolve().parent.parent, 'apps'))
BASE_DIR = Path(__file__).resolve().parent.parent


# Initialiser environ.Env
env = environ.Env()

# Lire le fichier .env avec encodage UTF-8
environ.Env.read_env(os.path.join(BASE_DIR, '.env'), encoding='utf-8')

if not env('SECRET_KEY', default=None):
    raise ValueError("SECRET_KEY must be set in environment variables or .env file")

SECRET_KEY = env('SECRET_KEY')
DEBUG = env.bool('DEBUG', default=False)

# Security settings for production
if not DEBUG:
    # SSL/HTTPS Security
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Cookie Security
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

# Development authentication bypass for JWT issues
BYPASS_AUTH_FOR_DEVELOPMENT = env.bool('BYPASS_AUTH_FOR_DEVELOPMENT', default=DEBUG)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])
if not DEBUG:
    if not ALLOWED_HOSTS:
        raise ValueError("ALLOWED_HOSTS must be set in environment variables or .env file when DEBUG is False")

# Paramètres de base - URLs principales
if DEBUG:
    # Développement local
    BACKEND_URL = env.str('BACKEND_URL', default='http://localhost:8000')
    BASE_URL = BACKEND_URL
    PORTAL_URL = env.str('PORTAL_URL', default='http://localhost:8080')
else:
    # Production
    BACKEND_URL = env.str('BACKEND_URL', default='https://www.openlinguify.com')
    BASE_URL = BACKEND_URL
    PORTAL_URL = env.str('PORTAL_URL', default='https://openlinguify.com')

# PostgreSQL settings (local only)
# All database configuration is now in DATABASES section below

# normally Allowed hosts should be set to the domain name of the website
# but for development purposes we can set it to all
# normally, ALLOWED_HOSTS = ['yourdomain.com'] or empty in development mode
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1', 'testserver'])
if not DEBUG and not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ['linguify.onrender.com', 'openlinguify.com', 'www.openlinguify.com']

# SEO Settings - Prevent automatic www prepending
PREPEND_WWW = False
APPEND_SLASH = True    

# Application definition

# Auto-discovery of Django apps in the apps/ directory
from .utils import get_installed_apps

# INSTALLED_APPS is now automatically generated
# All apps in backend/apps/ with an apps.py file are automatically included
# To exclude an app, add it to the exclude_from_discovery list in utils.py
INSTALLED_APPS = get_installed_apps()

# Manual INSTALLED_APPS configuration (for reference - now automated)
# INSTALLED_APPS = [
#     'django.contrib.admin',
#     'django.contrib.auth',
#     'django.contrib.contenttypes',
#     'django.contrib.sessions',
#     'django.contrib.messages',
#     'django.contrib.staticfiles',
#     'django.contrib.humanize',
#     'django_extensions',
#     'django_filters',
#     'channels',
#     'drf_spectacular',
# 
#     # Project django_apps (now auto-discovered)
#     'apps.authentication',
#     'apps.chat',
#     # 'apps.coaching',        # Excluded in utils.py
#     'apps.community',
#     'apps.course',
#     'apps.data',
#     'apps.documents',
#     'apps.language_ai',
#     # 'apps.payments',        # Excluded in utils.py
#     'apps.revision',
#     'apps.notebook',
#     # 'apps.task',            # Excluded in utils.py
#     'apps.notification',
#     # 'apps.subscription',    # Excluded in utils.py
#     'apps.quizz',
#     'apps.teaching',
#     'apps.todo',
#     'apps.cms_sync',
#     'apps.calendar_app',
#     
#     # Other modules
#     'app_manager',
#     'saas_web',
#     'core.apps.CoreConfig',
#     'rest_framework',
#     'rest_framework.authtoken',
#     'corsheaders',
# ]

AUTH_USER_MODEL = 'authentication.User'

# URLs d'authentification
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# App config declarations in individual apps

AUTHENTICATION_BACKENDS = [
    'apps.authentication.backends.EmailOrUsernameModelBackend',  # Custom backend for email or username login
    'django.contrib.auth.backends.ModelBackend',  # Fallback to default
    'django.contrib.auth.backends.RemoteUserBackend',
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',        # Utilisateurs anonymes: 100 requêtes par heure
        'user': '1000/hour',       # Utilisateurs authentifiés: 1000 requêtes par heure
        'upload': '100/hour',       # Uploads (photos, etc.): 10 par heure
        'stats': '60/hour',        # Statistiques: 60 par heure
        'create': '100/hour',      # Création d'objets: 100 par heure
    },
}

CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[
    "http://localhost:8000",
    "https://openlinguify.com",
    "https://www.openlinguify.com"
])

# No additional origin regexes needed for Django frontend
CORS_ALLOWED_ORIGIN_REGEXES = []

# In production, use specific origins. In dev, allow all.
CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://openlinguify.com",
    "https://www.openlinguify.com",
])

# Add all Vercel preview URLs to CSRF trusted origins if in production
if not DEBUG:
    import re
    # This will be populated dynamically if needed
    pass

# En développement
if DEBUG:
    CSRF_USE_SESSIONS = False
    CSRF_COOKIE_HTTPONLY = False
    CSRF_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_HTTPONLY = True



# TEMPORARY: Enable auth bypass for development debugging
# REMOVE THIS IN PRODUCTION!
if DEBUG:
    BYPASS_AUTH_FOR_DEVELOPMENT = False  # Use real authentication
    # print("WARNING: Authentication bypass is enabled for development!")
    # print("This should NEVER be used in production!")


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}
# Configuration de session - temporarily using DB for debugging
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Changed from cache to db for debugging
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_NAME = 'sessionid'  # Changed back to default for debugging
SESSION_COOKIE_AGE = 86400  # 1 jour en secondes
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Configuration de cache pour Auth0
AUTH0_TOKEN_CACHE_TIMEOUT = 3600  # 1 heure en secondes
AUTH0_USERINFO_CACHE_TIMEOUT = 3600  # 1 heure en secondes 

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # Language detection
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'apps.authentication.middleware.middleware.JWTMiddleware',  # Disabled - using Django sessions
    'apps.authentication.middleware.language_middleware.UserLanguageMiddleware',  # User language preference
    'apps.authentication.middleware.terms_middleware.TermsAcceptanceMiddleware',  # Check terms acceptance
    # 'core.jobs.middleware.JobsErrorHandlingMiddleware',  # Jobs error handling - moved to portal
    # SEO Optimization Middleware (simplified version)
    'core.seo.middleware.simple.SimpleSEOMiddleware',
    # 'core.seo.middleware.optimization.SEOOptimizationMiddleware',  # Disabled temporarily
    # 'core.seo.middleware.optimization.PreloadMiddleware',
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'Access-Control-Allow-Origin',
    'Access-Control-Allow-Headers',
]

CORS_EXPOSE_HEADERS = [
    'access-control-allow-origin',
    'access-control-allow-credentials',
]

CORS_PREFLIGHT_MAX_AGE = 86400

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR.joinpath('templates'),
            BASE_DIR.joinpath('apps/authentication/templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'app_manager.context_processors.current_app_context',
                'apps.authentication.context_processors.auth_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'
# Database - PostgreSQL ONLY
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# Configuration automatique basée sur DJANGO_ENV
django_env = env('DJANGO_ENV', default='development')

# Check for Render Database URL first (automatically provided in cloud)
database_url = env('DATABASE_URL', default=None)

# Check if we're in Render environment (production)
is_render = env('RENDER', default=False, cast=bool)
if is_render and not django_env == 'test':
    django_env = 'production'
    print("Detected Render environment - setting django_env to production")

if database_url:
    # Use Render PostgreSQL (automatically configured)
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(database_url)
    }
    print("Using Render PostgreSQL (Cloud)")
    
elif django_env == 'production' or django_env == 'staging' or is_render:
    # PRODUCTION/STAGING : PostgreSQL local (plus de Supabase !)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('PROD_DB_NAME', default='db_linguify_prod'),
            'USER': env('PROD_DB_USER', default='postgres'),
            'PASSWORD': env('PROD_DB_PASSWORD', default='azerty'),
            'HOST': env('PROD_DB_HOST', default='localhost'),
            'PORT': env('PROD_DB_PORT', default='5432'),
        }
    }
    print(f"Using LOCAL PostgreSQL for {django_env.upper()}")
    
elif django_env == 'development':
    # DEVELOPMENT : PostgreSQL local uniquement
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('DEV_DB_NAME'),
            'USER': env('DEV_DB_USER'),
            'PASSWORD': env('DEV_DB_PASSWORD'),
            'HOST': env('DEV_DB_HOST'),
            'PORT': env('DEV_DB_PORT'),
        }
    }
    print("Using PostgreSQL local for development")
    
elif os.environ.get('TEST_MODE') == 'True' or django_env == 'test':
    # Tests : PostgreSQL temporaire en mémoire
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('TEST_DB_NAME', default='db_linguify_test'),
            'USER': env('TEST_DB_USER', default='postgres'),
            'PASSWORD': env('TEST_DB_PASSWORD', default='azerty'),
            'HOST': env('TEST_DB_HOST', default='localhost'),
            'PORT': env('TEST_DB_PORT', default='5432'),
            'TEST': {
                'NAME': 'test_linguify_temp',
            },
        }
    }
    print("Using PostgreSQL for testing")
    
else:
    # FALLBACK : PostgreSQL local (utilise la config développement)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('DEV_DB_NAME', default='db_linguify_dev'),
            'USER': env('DEV_DB_USER', default='postgres'),
            'PASSWORD': env('DEV_DB_PASSWORD', default='azerty'),
            'HOST': env('DEV_DB_HOST', default='localhost'),
            'PORT': env('DEV_DB_PORT', default='5432'),
        }
    }
    print("Using local PostgreSQL (fallback)")
# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en'  # Changed to English to fix Unicode error
TIME_ZONE = 'Europe/Paris'

USE_I18N = True  # Re-enabled with English as default
USE_L10N = True
USE_TZ = True

# Supported languages - Focus on business value with 4 main languages
LANGUAGES = [
    ('en', 'English'),
    ('fr', 'Français'),
    ('es', 'Español'),
    ('nl', 'Nederlands'),
]

# Locale paths - for internationalization
LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'apps/authentication/locale'),
    os.path.join(BASE_DIR, 'apps/notification/locale'),
    os.path.join(BASE_DIR, 'saas_web/locale'),
    os.path.join(BASE_DIR, 'apps/course/i18n'),
    os.path.join(BASE_DIR, 'apps/revision/i18n'),
    os.path.join(BASE_DIR, 'apps/notebook/i18n'),
    os.path.join(BASE_DIR, 'apps/quizz/i18n'),
    os.path.join(BASE_DIR, 'apps/language_ai/i18n'),
    # os.path.join(BASE_DIR, 'locale'),
]

# Translation middleware already added in MIDDLEWARE list
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = []

# WhiteNoise settings for static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Profile pictures settings - Style réseau social
PROFILE_PICTURES_ROOT = os.path.join(MEDIA_ROOT, 'profiles')
PROFILE_PICTURES_URL = f'{MEDIA_URL}profiles/'

# Tailles d'images pour différents contextes
PROFILE_PICTURE_SIZES = {
    'small': (50, 50),       # Pour commentaires, notifications
    'medium': (150, 150),    # Pour les cartes profil
    'large': (300, 300),     # Pour la page profil
}

# Paramètres de qualité et format
PROFILE_PICTURE_QUALITY = 85       # Qualité JPEG (1-100)
PROFILE_PICTURE_FORMAT = 'JPEG'    # Format par défaut pour les images converties
PROFILE_PICTURE_MAX_DISPLAY_SIZE = (800, 800)  # Dimensions max pour la version d'affichage

# Validation des images téléchargées
PROFILE_PICTURE_MAX_SIZE = 5 * 1024 * 1024  # Taille max 5MB
PROFILE_PICTURE_MIN_WIDTH = 200    # Largeur minimale en pixels
PROFILE_PICTURE_MIN_HEIGHT = 200   # Hauteur minimale en pixels

# Comportement de stockage
PROFILE_PICTURE_KEEP_ORIGINALS = True     # Conserver les fichiers originaux
PROFILE_PICTURE_MAX_VERSIONS = 5          # Nombre de versions historiques à conserver

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

APPEND_SLASH = True

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
    # os.path.join(BASE_DIR, 'public_web', 'static'), # Moved to portal
    os.path.join(BASE_DIR, 'saas_web', 'static'),
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'compressor.finders.CompressorFinder',
    # 'sass_processor.finders.CssFinder',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Django Compressor settings (disabled for now)
# COMPRESS_ENABLED = True
# COMPRESS_CSS_FILTERS = [
#     'compressor.filters.css_default.CssAbsoluteFilter',
#     'sass_processor.compressor.SassCompiler',
# ]
# COMPRESS_JS_FILTERS = [
#     'compressor.filters.jsmin.JSMinFilter',
# ]



ASGI_APPLICATION = 'core.asgi.application'

# Use in-memory channel layer for testing
if os.environ.get('TEST_MODE') == 'True' or 'test' in sys.argv:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer"
        }
    }
else:
    # Try Redis first, fallback to in-memory if Redis is not available
    try:
        import redis
        redis_client = redis.Redis(
            host=os.environ.get('REDIS_HOST', '127.0.0.1'),
            port=int(os.environ.get('REDIS_PORT', 6379)),
            socket_connect_timeout=1
        )
        redis_client.ping()
        CHANNEL_LAYERS = {
            'default': {
                'BACKEND': 'channels_redis.core.RedisChannelLayer',
                'CONFIG': {
                    "hosts": [(
                        os.environ.get('REDIS_HOST', '127.0.0.1'),
                        int(os.environ.get('REDIS_PORT', 6379))
                    )],
                },
            },
        }
    except Exception:
        # Fallback to in-memory layer if Redis is not available
        CHANNEL_LAYERS = {
            "default": {
                "BACKEND": "channels.layers.InMemoryChannelLayer"
            }
        }


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {name} {message}',
            'style': '{',
        },
        'profile_picture': {
            'format': '[ProfilePicture] {levelname} {asctime} {name} - {message}',
            'style': '{',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'profile_console': {
            'class': 'logging.StreamHandler',
            'formatter': 'profile_picture',
        },
    },
    'loggers': {
        'apps.authentication': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'security.authentication': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'saas_web.views': {
            'handlers': ['profile_console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'apps.authentication.storage': {
            'handlers': ['profile_console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}



# Configuration email pour l'envoi depuis les formulaires de contact
if os.environ.get('TEST_MODE') == 'True' or os.environ.get('EMAIL_DEBUG') == 'True':
    # Use console backend for testing
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    DEFAULT_FROM_EMAIL = 'test@example.com'
    print("[DEBUG] Mode EMAIL DEBUG activé - emails affichés en console")
else:
    # Use SMTP for production/development
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = env('EMAIL_HOST')
    EMAIL_PORT = env.int('EMAIL_PORT')
    EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS')
    EMAIL_HOST_USER = env('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
    DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')

def generate_api_schema_tags():
    """
    Génère la structure des tags pour l'API schema basée sur les applications installées
    et ajoute les endpoints spécifiques pour chaque application.
    """
    tags = []
    
    # Mappage entre les applications et leurs endpoints associés
    app_endpoints = {
        'authentication': [
            {'name': 'Auth: User Profile', 'description': 'User profile management endpoints'},
            {'name': 'Auth: User Settings', 'description': 'User settings and preferences'},
        ],
        'course': [
            {'name': 'Lessons', 'description': 'Lesson endpoints for course content'},
            {'name': 'Content', 'description': 'Learning content and materials'},
        ],
        'data': [],
        'revision': [
            {'name': 'Flashcards', 'description': 'Flashcard creation and management'},
            {'name': 'Decks', 'description': 'Flashcard deck organization'},
        ],
        'notebook': [
            {'name': 'Notes', 'description': 'Note creation and management'},
            {'name': 'Categories', 'description': 'Note categorization'},
        ],
        'progress': [
            {'name': 'Statistics', 'description': 'Learning statistics and analytics'},
        ],
    }
    
    # Descriptions par défaut pour les applications
    app_descriptions = {
        'authentication': 'Authentication management and functionality',
        'course': 'Course management and functionality',
        'data': 'Data management and functionality',
        'revision': 'Revision management and functionality',
        'notebook': 'Notebook management and functionality',
        'progress': 'User learning progress tracking',
    }
    
    # Parcourir les applications installées
    for app in INSTALLED_APPS:
        if app.startswith('apps.'):
            app_name = app.replace('apps.', '')
            
            # Vérifier si cette application est dans notre mappage
            if app_name in app_endpoints:
                # Ajouter le tag principal pour l'application
                app_display_name = app_name.capitalize()
                tags.append({
                    'name': app_display_name,
                    'description': app_descriptions.get(app_name, f"{app_display_name} management and functionality")
                })
                
                # Ajouter les endpoints associés à cette application
                tags.extend(app_endpoints[app_name])
    
    return tags

SPECTACULAR_SETTINGS = {
    'TITLE': 'Linguify API',
    'DESCRIPTION': 'API documentation for Linguify',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'CONTACT': {
        'name': 'Linguify Support', 
        'email': 'dev@linguify.com',
        'url': 'https://linguify.com/support',
    },
    'LICENSE': {
        'name': 'LGPLv3',
        'url': 'https://www.gnu.org/licenses/lgpl-3.0.html',
    },
    # Interface Swagger personnalisée
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': False,
    },
    
    # Organiser les endpoints par tags
    'TAGS': generate_api_schema_tags(),
    
    # Performance and organization settings
    'COMPONENT_SPLIT_REQUEST': True,
    'COMPONENT_SPLIT_RESPONSE': True,
    'SCHEMA_PATH_PREFIX': r'/api/v[0-9]',
    'SCHEMA_PATH_PREFIX_TRIM': True,
}

# =====================================================================
# SEO CONFIGURATION SETTINGS
# =====================================================================

# Enable SEO optimizations
SEO_ENABLE_COMPRESSION = True
SEO_ENABLE_STRUCTURED_DATA = True
SEO_ENABLE_META_OPTIMIZATION = True

# Domain configuration (consistent with your setup)
SEO_DOMAIN = 'openlinguify.com'
SEO_PROTOCOL = 'https'
SEO_BASE_URL = f'{SEO_PROTOCOL}://{SEO_DOMAIN}'

# Sitemap settings
SITEMAP_USE_GZIP = True
SITEMAP_CACHE_TIMEOUT = 3600  # 1 hour
SITEMAP_PING_GOOGLE = True
SITEMAP_PING_BING = True
SITEMAP_PING_YANDEX = True

# Social media settings
FACEBOOK_APP_ID = env.str('FACEBOOK_APP_ID', default='')
FACEBOOK_ADMINS = env.str('FACEBOOK_ADMINS', default='')
TWITTER_HANDLE = '@openlinguify'

# Default SEO meta
DEFAULT_SEO_TITLE = 'OpenLinguify - Learn Languages Online with AI'
DEFAULT_SEO_DESCRIPTION = 'Master new languages with OpenLinguify\'s AI-powered lessons, interactive flashcards, and personalized learning paths. Start learning for free today!'
DEFAULT_SEO_KEYWORDS = 'language learning, learn languages online, AI language tutor, interactive language lessons, language learning app'

# Structured data settings
STRUCTURED_DATA_ORGANIZATION = {
    'name': 'OpenLinguify',
    'url': SEO_BASE_URL,
    'logo': f'{SEO_BASE_URL}/static/images/logo.png',
    'description': 'OpenLinguify is an open source educational platform dedicated to language learning with specialized apps for interactive education, AI-powered lessons, and personalized learning experiences.',
    'foundingDate': '2024',
    'contactEmail': 'info@openlinguify.com',
    'educationalOrganization': True,
    'category': [
        'Educational Technology',
        'Productivity',
        'Language Learning',
        'AI Education',
        'E-Learning'
    ],
    'applicationCategory': 'Education',
    'operatingSystem': 'Web-based',
    'sameAs': [
        'https://www.facebook.com/openlinguify',
        'https://twitter.com/openlinguify',
        'https://www.linkedin.com/company/openlinguify',
        'https://www.youtube.com/openlinguify',
        'https://www.instagram.com/openlinguify',
        'https://github.com/openlinguify'
    ]
}

# =====================================================================
# STRIPE CONFIGURATION SETTINGS
# =====================================================================

# Stripe keys (à ajouter dans .env)
STRIPE_PUBLIC_KEY = env('STRIPE_PUBLIC_KEY', default='')
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY', default='')
STRIPE_WEBHOOK_SECRET = env('STRIPE_WEBHOOK_SECRET', default='')

# Configuration Stripe
STRIPE_LIVE_MODE = env.bool('STRIPE_LIVE_MODE', default=False)  # False = test mode
