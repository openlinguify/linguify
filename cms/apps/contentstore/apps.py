from django.apps import AppConfig


class ContentstoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.contentstore'
    verbose_name = 'Content Store'
    
    def ready(self):
        """Initialize app when Django starts."""
        # Import signals to ensure they're registered
        try:
            from . import signals  # noqa
        except ImportError:
            pass