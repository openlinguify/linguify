from django.apps import AppConfig


class AppManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_manager'
    label = 'app_manager'

    def ready(self):
        """Called when Django is ready. Setup signals for delayed app sync."""
        # Only setup signals in production/development, not during migrations or management commands
        import sys
        if any(cmd in sys.argv for cmd in ['migrate', 'makemigrations', 'collectstatic', 'test']):
            return

        # Import signals to set up delayed sync
        from . import signals
