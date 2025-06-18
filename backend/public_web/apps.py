from django.apps import AppConfig


class PublicWebConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'public_web'
    verbose_name = 'Public Website'