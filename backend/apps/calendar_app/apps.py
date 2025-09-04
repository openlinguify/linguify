from django.apps import AppConfig


class CalendarConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.calendar_app'
    verbose_name = 'Calendar'
    
    def ready(self):
        # Import signals to ensure they are registered
        try:
            from . import signals
        except ImportError:
            pass