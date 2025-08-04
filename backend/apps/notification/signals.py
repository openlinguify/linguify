# backend/apps/notification/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from asgiref.sync import async_to_sync

from .models.notification_models import Notification, NotificationSetting
from .utils import NotificationManager
from .serializers import NotificationSerializer
import logging

logger = logging.getLogger(__name__)
# Importations pour les signaux spécifiques
from apps.course.models.core import Lesson, ContentLesson

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_notification_settings(sender, instance, created, **kwargs):
    """
    Crée les paramètres de notification pour un nouvel utilisateur
    et envoie une notification de bienvenue
    """
    if created:
        try:
            # Créer les paramètres par défaut
            NotificationSetting.objects.create(user=instance)
            # Envoyer une notification de bienvenue
            NotificationManager.create_notification(
                user=instance,
                title="Bienvenue sur Linguify!",
                message=f"Bonjour {instance.first_name or instance.username}! Bienvenue sur Linguify, votre plateforme d'apprentissage des langues.",
                notification_type='info',
                priority='medium',
                data={
                    "action": "onboarding"
                },
                expires_in_days=7
            )
        except Exception as e:
            # Log error but don't prevent user creation
            logger.error(f"Failed to create notification settings for user {instance.username}: {e}")
            # Create minimal settings to prevent future errors
            try:
                NotificationSetting.objects.get_or_create(user=instance)
            except Exception as e2:
                logger.error(f"Failed to create fallback notification settings: {e2}")


# Signal pour les suppressions d'utilisateurs
@receiver(post_delete, sender=User)
def cleanup_user_notifications(sender, instance, **kwargs):
    """
    Supprime toutes les notifications associées à un utilisateur supprimé
    """
    Notification.objects.filter(user=instance).delete()
    NotificationSetting.objects.filter(user=instance).delete()