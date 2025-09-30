from django.apps import AppConfig


class LanguagelearningConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.language_learning'
    verbose_name = 'Language Learning'

    def ready(self):
        # Importer les signaux pour qu'ils soient enregistrés
        import apps.language_learning.signals
