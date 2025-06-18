# Configuration pour l'intégration du frontend OWL dans Django
# Similaire à l'architecture openlinguify

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Static files configuration for OWL frontend
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Additional directories for static files
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# For each app, include their static directories
for app in ['authentication', 'course', 'notebook', 'revision']:
    app_static = os.path.join(BASE_DIR, f'apps/{app}/static')
    if os.path.exists(app_static):
        STATICFILES_DIRS.append(app_static)

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Django Compressor settings for SCSS/JS compilation
COMPRESS_ENABLED = True
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'django_sass_processor.compressor.SassCompiler',
]
COMPRESS_JS_FILTERS = [
    'compressor.filters.jsmin.JSMinFilter',
]

# OWL Framework configuration
OWL_ASSETS = {
    'owl': {
        'js': [
            'https://cdn.jsdelivr.net/npm/@openlinguify/owl@2.1.1/dist/owl.iife.js',
        ],
        'css': [],
    }
}

# Template configuration for OWL
TEMPLATES_FRONTEND = {
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [
        os.path.join(BASE_DIR, 'templates'),
        # Include app-specific template directories
    ],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
            'django.template.context_processors.static',
            'django.template.context_processors.media',
        ],
    },
}

# WebPack-like configuration for module bundling
FRONTEND_BUILD_CONFIG = {
    'entry_points': {
        # Define entry points for each app
        'authentication': 'apps/authentication/static/src/js/app.js',
        'course': 'apps/course/static/src/js/app.js',
        'notebook': 'apps/notebook/static/src/js/app.js',
        'revision': 'apps/revision/static/src/js/app.js',
    },
    'output': {
        'path': os.path.join(BASE_DIR, 'static/dist'),
        'filename': '[name].bundle.js',
    }
}