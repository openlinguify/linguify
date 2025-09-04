from django.apps import AppConfig


class TodoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.todo'
    verbose_name = 'Todo & Productivity'
    
    def ready(self):
        try:
            import apps.todo.signals
        except ImportError:
            pass