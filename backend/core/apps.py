from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Core Management'
    
    def ready(self):
        """Initialize the SEO system when Django starts"""
        try:
            # Import SEO modules to register them
            from . import seo
        except ImportError:
            pass