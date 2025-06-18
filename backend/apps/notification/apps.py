# backend/apps/notification/apps.py
from django.apps import AppConfig

class NotificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notification'
    verbose_name = 'Notifications'
    
    def ready(self):
        """
        Initialize signals when the app is ready
        """
        # Import signals to register them
        import apps.notification.signals