from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
import logging

logger = logging.getLogger(__name__)

class RevisionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.revision'
    label = 'revision'
    verbose_name = _('Revision')
    
    def ready(self):
        """Called when Django starts"""
        try:
            # Import settings models to register them
            from .models import settings_models
            logger.info("Revision settings models loaded successfully")
            
            # Register signals if needed
            from . import signals
            logger.info("Revision signals registered")
            
        except ImportError as e:
            logger.warning(f"Could not import revision settings models or signals: {e}")
        except Exception as e:
            logger.error(f"Error initializing revision app: {e}")
    
    @classmethod
    def get_settings_config(cls):
        """Return settings configuration for integration with saas_web"""
        from .__manifest__ import __manifest__
        return __manifest__.get('settings_config', {})
