from django.apps import AppConfig


class LanguageAiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.language_ai'
    verbose_name = 'Language AI Conversation'

    def ready(self):
        import apps.language_ai.signals