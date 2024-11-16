# backend/django_apps/flashcard/apps.py
from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class FlashcardConfig(AppConfig):
    """Config of the flashcard app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_apps.flashcard'
    verbose_name = 'Flashcard App'

    def ready(self):
        """Import signals."""
        logger.info('Importing signals...')
        import django_apps.flashcard.signals
        logger.info(_("The Flashcard App is ready and can import the Signals imported."))
