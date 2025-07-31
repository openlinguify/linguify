"""
Signaux pour l'application Révision
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_revision_settings(sender, instance, created, **kwargs):
    """
    Crée automatiquement les paramètres de révision pour un nouvel utilisateur
    """
    if created:
        try:
            from .models_settings import RevisionSettings
            RevisionSettings.objects.create(user=instance)
            logger.info(f"Created revision settings for new user: {instance.username}")
        except Exception as e:
            logger.error(f"Failed to create revision settings for user {instance.username}: {e}")