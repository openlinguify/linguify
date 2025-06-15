# backend/apps/authentication/apps.py
from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.authentication'
    label = 'authentication'
    
    def ready(self):
        import apps.authentication.signals

