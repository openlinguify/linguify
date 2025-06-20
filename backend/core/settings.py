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

# Lire le fichier .env
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

if not env('SECRET_KEY', default=None):
    raise ValueError("SECRET_KEY must be set in environment variables or .env file")

SECRET_KEY = env('SECRET_KEY')
DEBUG = env.bool('DEBUG', default=False)

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
else:
    # Production
    BACKEND_URL = env.str('BACKEND_URL', default='https://www.openlinguify.com')
    BASE_URL = BACKEND_URL

# DEPRECATED: FRONTEND_URL sera supprimé avec le frontend Next.js
# Pour la compatibilité temporaire uniquement
FRONTEND_URL = env.str('FRONTEND_URL', default=BASE_URL)

# Supabase settings
SUPABASE_URL = env.str('SUPABASE_URL', default='')
SUPABASE_ANON_KEY = env.str('SUPABASE_ANON_KEY', default='')
SUPABASE_SERVICE_ROLE_KEY = env.str('SUPABASE_SERVICE_ROLE_KEY', default='')
SUPABASE_PROJECT_ID = env.str('SUPABASE_PROJECT_ID', default='')
SUPABASE_JWT_SECRET = env.str('SUPABASE_JWT_SECRET', default='')

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

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_extensions',
    'django_filters',
    'channels',
    'drf_spectacular',

    # Core project modules
    'core.apps.CoreConfig',
    'core.jobs',

    # Project django_apps
    'apps.authentication',
    # 'apps.chat',
    # 'apps.coaching',
    'apps.community',
    'apps.course',
    'apps.data',
    # 'apps.flashcard',
    'apps.language_ai',
    # 'apps.payments',
    # 'apps.quiz',
    'apps.revision',
    'apps.notebook',
    # 'apps.task',
    'apps.notification',
    #'subscription',
    'app_manager',
    'apps.quizz',
    
    # Web interfaces
    'public_web',
    'saas_web',
    # 'admin_tools',  # Admin tools for managing the platform
    # Django REST framework modules
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    
    # Frontend integration
    # 'compressor',
    # 'sass_processor',

    # test
    'pytest_django',
]

AUTH_USER_MODEL = 'authentication.User'

# URLs d'authentification
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# App config declarations in individual apps

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
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
    BYPASS_AUTH_FOR_DEVELOPMENT = False  # Disabled to use real Supabase auth
    # print("WARNING: Authentication bypass is enabled for development!")
    # print("This should NEVER be used in production!")

# DEPRECATED: Auth0 Configuration (REMOVED - now using Django + Supabase authentication)
# AUTH0_DOMAIN = env('AUTH0_DOMAIN', default='')
# AUTH0_CLIENT_ID = env('AUTH0_CLIENT_ID', default='')
# AUTH0_CLIENT_SECRET = env('AUTH0_CLIENT_SECRET', default='')
# AUTH0_AUDIENCE = env('AUTH0_AUDIENCE', default='')
# AUTH0_CALLBACK_URL = f"{BACKEND_URL}/api/auth/callback/"
# FRONTEND_CALLBACK_URL = f"{BASE_URL}/auth/login/"
# FRONTEND_LOGOUT_REDIRECT = f"{BASE_URL}/"  # Redirection vers la landing page Django
# AUTH0_ALGORITHM = 'RS256'

# DEPRECATED: JWT_AUTH configuration (REMOVED - now using Django sessions + Supabase)
# JWT_AUTH = {
#     'JWT_PAYLOAD_GET_USERNAME_HANDLER':
#         'apps.authentication.utils.jwt_get_username_from_payload_handler',
#     'JWT_DECODE_HANDLER':
#         'apps.authentication.utils.jwt_decode_token',
#     'JWT_ALGORITHM': 'RS256',
#     'JWT_AUDIENCE': AUTH0_AUDIENCE,
#     'JWT_ISSUER': f'https://{AUTH0_DOMAIN}/',
#     'JWT_AUTH_HEADER_PREFIX': 'Bearer',
#     'JWT_VERIFY_EXPIRATION': False, 
#     'JWT_ALLOW_REFRESH': True,
#     'JWT_EXPIRATION_DELTA': timedelta(days=7),
#     'JWT_REFRESH_EXPIRATION_DELTA': timedelta(days=7),
# }

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

#by default, we use LocMemCache for development

# in production, we can use redis for caching
# install redis and django-redis

# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': 'redis://127.0.0.1:6379/1',
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#         }
#     }
# }


# Configuration de session - ajoutez ou modifiez cette section
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_NAME = 'linguify_session'
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
    # 'apps.authentication.middleware.JWTMiddleware',  # Disabled - using Supabase now
    'apps.authentication.middleware_terms.TermsAcceptanceMiddleware',  # Check terms acceptance
    'core.jobs.middleware.JobsErrorHandlingMiddleware',  # Jobs error handling
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
    
elif django_env == 'production' or is_render:
    # PRODUCTION : Toujours Supabase PostgreSQL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('SUPABASE_DB_NAME', default='postgres'),
            'USER': env('SUPABASE_DB_USER'),
            'PASSWORD': env('SUPABASE_DB_PASSWORD'),
            'HOST': env('SUPABASE_DB_HOST'),
            'PORT': env('SUPABASE_DB_PORT', default='5432'),
            'OPTIONS': {
                'sslmode': 'require',
            },
        }
    }
    print("Using PRODUCTION Supabase PostgreSQL")
    
elif django_env == 'development':
    # DEVELOPMENT : PostgreSQL local uniquement
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
    print("Using PostgreSQL local for development")
    
elif os.environ.get('TEST_MODE') == 'True' or django_env == 'test':
    # Tests : PostgreSQL temporaire en mémoire
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('DB_NAME', default='test_linguify'),
            'USER': env('DB_USER', default='postgres'),
            'PASSWORD': env('DB_PASSWORD', default='postgres'),
            'HOST': env('DB_HOST', default='localhost'),
            'PORT': env('DB_PORT', default='5432'),
            'TEST': {
                'NAME': 'test_linguify_temp',
            },
        }
    }
    print("Using PostgreSQL for testing")
    
else:
    # FALLBACK : Vérifier si des variables Supabase sont présentes
    supabase_host = env('SUPABASE_DB_HOST', default=None)
    if supabase_host and not DEBUG:
        # Production avec Supabase
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': env('SUPABASE_DB_NAME', default='postgres'),
                'USER': env('SUPABASE_DB_USER'),
                'PASSWORD': env('SUPABASE_DB_PASSWORD'),
                'HOST': supabase_host,
                'PORT': env('SUPABASE_DB_PORT', default='5432'),
                'OPTIONS': {
                    'sslmode': 'require',
                },
            }
        }
        print("Using Supabase PostgreSQL (fallback production)")
    else:
        # FALLBACK : PostgreSQL local avec anciennes variables
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': env('DB_NAME', default='db_linguify_dev'),
                'USER': env('DB_USER', default='postgres'),
                'PASSWORD': env('DB_PASSWORD', default='azerty'),
                'HOST': env('DB_HOST', default='localhost'),
                'PORT': env('DB_PORT', default='5432'),
            }
        }
        print("Using local PostgreSQL (fallback development)")
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

# Locale paths - public_web as central hub for consistent translations
LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'public_web/i18n'),
    os.path.join(BASE_DIR, 'apps/authentication/i18n'),
    os.path.join(BASE_DIR, 'saas_web/i18n'),
    os.path.join(BASE_DIR, 'apps/course/i18n'),
    os.path.join(BASE_DIR, 'apps/revision/i18n'),
    os.path.join(BASE_DIR, 'apps/notebook/i18n'),
    os.path.join(BASE_DIR, 'apps/quizz/i18n'),
    os.path.join(BASE_DIR, 'apps/language_ai/i18n'),
    # os.path.join(BASE_DIR, 'locale'),  # Deprecated global translations
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
    os.path.join(BASE_DIR, 'public_web', 'static'),
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
    except (ImportError, redis.exceptions.ConnectionError, redis.exceptions.TimeoutError):
        # Fallback to in-memory layer if Redis is not available
        CHANNEL_LAYERS = {
            "default": {
                "BACKEND": "channels.layers.InMemoryChannelLayer"
            }
        }


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'apps.authentication': {
            'handlers': ['console'],
            'level': 'DEBUG',
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
    'contactEmail': 'support@openlinguify.com',
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
