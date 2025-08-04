from django.apps import AppConfig


class DocumentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.documents'
    verbose_name = 'Documents'
    
    def ready(self):
        # Import signal handlers
        try:
            import apps.documents.signals
        except ImportError:
            pass