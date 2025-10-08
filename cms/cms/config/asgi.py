"""
ASGI config for Linguify Teacher CMS project.
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cms.config.settings.development')

application = get_asgi_application()
