# app_manager/signals.py
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps
import logging

logger = logging.getLogger(__name__)

@receiver(post_migrate)
def sync_apps_after_migrate(sender, **kwargs):
    """
    Sync apps from manifests after migrations are complete.
    This ensures database is ready and avoids the warning about
    accessing database during app initialization.
    """
    # Only run for app_manager migrations or the first migration
    if sender.name == 'app_manager' or kwargs.get('verbosity', 1) >= 1:
        try:
            # Import here to avoid circular imports
            from .models.app_manager_models import App

            # Check if we can access the database safely
            if apps.ready:
                summary = App.sync_apps()
                logger.info(f"Apps synchronized: {summary}")
        except Exception as e:
            # Don't break startup if sync fails
            logger.warning(f"App sync failed during post_migrate: {e}")


def sync_apps_on_first_request():
    """
    Alternative: Sync apps on first request instead of startup.
    This can be called from a middleware or view.
    """
    try:
        from .models.app_manager_models import App
        return App.sync_apps()
    except Exception as e:
        logger.warning(f"App sync failed on first request: {e}")
        return None