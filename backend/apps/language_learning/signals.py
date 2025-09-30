"""
Signaux Django pour l'app language_learning
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserLearningProfile
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@receiver(post_save, sender=User)
def create_user_learning_profile(sender, instance, created, **kwargs):
    """
    Crée automatiquement un UserLearningProfile quand un nouvel utilisateur est créé
    """
    if created:
        try:
            # Créer le profil d'apprentissage avec des valeurs par défaut
            profile = UserLearningProfile.objects.create(
                user=instance,
                native_language='EN',  # Valeur par défaut, sera mise à jour via le profil
                target_language='FR',  # Valeur par défaut populaire
                language_level='A1',   # Niveau débutant par défaut
                objectives='Personal', # Objectif par défaut
                daily_goal=15,         # 15 minutes par jour par défaut
                weekday_reminders=True,
                weekend_reminders=False,
                reminder_time='18:00',
                speaking_exercises=True,
                listening_exercises=True,
                reading_exercises=True,
                writing_exercises=True,
            )

            logger.info(f"✅ UserLearningProfile créé automatiquement pour {instance.username}")

        except Exception as e:
            logger.error(f"❌ Erreur lors de la création du UserLearningProfile pour {instance.username}: {e}")


@receiver(post_save, sender=User)
def update_user_learning_profile(sender, instance, created, **kwargs):
    """
    Met à jour le profil d'apprentissage si nécessaire
    """
    if not created:
        try:
            # Vérifier si le profil existe, le créer sinon
            if not hasattr(instance, 'learning_profile'):
                create_user_learning_profile(sender, instance, True, **kwargs)

        except Exception as e:
            logger.error(f"❌ Erreur lors de la mise à jour du UserLearningProfile pour {instance.username}: {e}")