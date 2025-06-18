"""
Debug settings for troubleshooting
Minimal configuration to get Django running
"""

from .settings import *

# Disable problematic features for debugging
USE_I18N = False
USE_L10N = False

# Use English only
LANGUAGE_CODE = 'en-us'

# Minimal middleware stack
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # SEO middleware
    'core.seo.middleware.simple.SimpleSEOMiddleware',
]

# Disable locale paths temporarily
LOCALE_PATHS = []

# Simple logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}

print("🔧 Debug settings loaded - minimal configuration")