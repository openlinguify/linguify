# backend/apps/notification/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Notification, NotificationSetting
from .utils import NotificationManager
from .serializers import NotificationSerializer

# Importations pour les signaux spécifiques
from apps.progress.models.progress_course import UserContentLessonProgress, UserLessonProgress
from apps.course.models import Lesson, ContentLesson

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_notification_settings(sender, instance, created, **kwargs):
    """
    Crée les paramètres de notification pour un nouvel utilisateur
    et envoie une notification de bienvenue
    """
    if created:
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

@receiver(post_save, sender=Notification)
def push_notification_via_websocket(sender, instance, created, **kwargs):
    """
    Envoie la notification via WebSocket quand une notification est créée ou mise à jour
    """
    if created:
        try:
            # Récupérer le channel layer
            channel_layer = get_channel_layer()
            if not channel_layer:
                return
            
            # Obtenir l'ID utilisateur
            user_id = instance.user.id
            group_name = f'user_{user_id}_notifications'
            
            # Sérialiser la notification
            serializer = NotificationSerializer(instance)
            
            # Envoyer au groupe WebSocket de l'utilisateur
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'notification_message',
                    'notification': serializer.data
                }
            )
            
            # Envoyer aussi une mise à jour du compteur
            unread_count = Notification.objects.filter(
                user=instance.user,
                is_read=False
            ).count()
            
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'unread_count_update',
                    'count': unread_count
                }
            )
        except Exception as e:
            print(f"Error sending notification via WebSocket: {e}")

# Signal pour les notifications de progression de leçon
@receiver(post_save, sender=UserContentLessonProgress)
def notify_lesson_progress(sender, instance, created, update_fields=None, **kwargs):
    """
    Envoie une notification quand un utilisateur a progressé significativement dans une leçon
    mais ne l'a pas encore terminée
    """
    # Ne pas envoyer de notification lors de la création initiale
    if created:
        return
    
    # Ne pas envoyer de notification si la mise à jour ne concerne pas le pourcentage de complétion
    if update_fields and 'completion_percentage' not in update_fields:
        return
    
    # Vérifier si la progression est significative mais pas terminée
    if 50 <= instance.completion_percentage < 100:
        # Pour éviter des notifications trop fréquentes, vérifier s'il y a eu une notification récente
        recent_notification = Notification.objects.filter(
            user=instance.user,
            type='lesson_reminder',
            data__contains={'content_lesson_id': instance.content_lesson_id},
            created_at__gte=timezone.now() - timedelta(days=1)  # Pas de notification dans les dernières 24h
        ).exists()
        
        if not recent_notification:
            try:
                # Récupérer les détails de la leçon
                content_lesson = ContentLesson.objects.get(id=instance.content_lesson_id)
                lesson = content_lesson.lesson
                
                # Récupérer le titre avec le bon code de langue ou fallback à l'anglais
                lang_code = instance.language_code or 'en'
                lesson_title = getattr(lesson, f'title_{lang_code}', None)
                if not lesson_title:
                    lesson_title = getattr(lesson, 'title_en', f"Leçon {lesson.id}")

                unit_title = None
                if lesson.unit:
                    unit_title = getattr(lesson.unit, f'title_{lang_code}', None)
                    if not unit_title:
                        unit_title = getattr(lesson.unit, 'title_en', f"Unité {lesson.unit.id}")

                # Créer une notification pour encourager l'utilisateur à terminer
                NotificationManager.send_lesson_reminder(
                    user=instance.user,
                    lesson_title=lesson_title,
                    lesson_id=lesson.id,
                    unit_id=lesson.unit.id if lesson.unit else None,
                    unit_title=unit_title
                )
            except (ContentLesson.DoesNotExist, Lesson.DoesNotExist):
                # Gérer le cas où la leçon n'existe plus
                pass

# Signal pour les notifications de complétion de leçon
@receiver(post_save, sender=UserLessonProgress)
def notify_lesson_completion(sender, instance, created, update_fields=None, **kwargs):
    """
    Envoie une notification quand un utilisateur a complété une leçon entière
    """
    # Ne pas envoyer lors de la création initiale
    if created:
        return
    
    # Vérifier si les champs mis à jour contiennent status
    if update_fields and 'status' not in update_fields:
        return

    # Envoyer une notification uniquement si la leçon vient d'être complétée
    if instance.status == 'completed':
        try:
            # Récupérer la leçon
            lesson = Lesson.objects.get(id=instance.lesson_id)
            
            # Récupérer le titre avec le bon code de langue ou fallback à l'anglais
            lang_code = instance.language_code or 'en'
            lesson_title = getattr(lesson, f'title_{lang_code}', None)
            if not lesson_title:
                lesson_title = getattr(lesson, 'title_en', f"Leçon {lesson.id}")

            # Créer une notification d'accomplissement
            NotificationManager.create_notification(
                user=instance.user,
                title="Leçon terminée!",
                message=f"Bravo! Vous avez terminé la leçon '{lesson_title}'.",
                notification_type='achievement',
                priority='medium',
                data={
                    "action": "view_progress",
                    "lesson_id": lesson.id,
                    "unit_id": lesson.unit.id if lesson.unit else None
                },
                expires_in_days=7
            )
            
            # Vérifier les séries de leçons complétées
            consecutive_days = check_consecutive_days(instance.user)
            if consecutive_days > 0 and consecutive_days % 3 == 0:  # Tous les 3 jours
                NotificationManager.send_streak_notification(
                    user=instance.user,
                    streak_days=consecutive_days
                )
                
        except Lesson.DoesNotExist:
            # Gérer le cas où la leçon n'existe plus
            pass

def check_consecutive_days(user):
    """
    Vérifie le nombre de jours consécutifs où l'utilisateur a complété au moins une leçon
    """
    # Ceci est une implémentation simplifiée
    # Pour une version réelle, il faudrait stocker cette information dans un modèle dédié
    
    # Calculer le nombre de jours consécutifs où l'utilisateur a complété des leçons
    from django.db.models import Count
    from django.db.models.functions import TruncDate
    
    # Récupérer les dates des dernières leçons complétées
    daily_completions = UserLessonProgress.objects.filter(
        user=user,
        status='completed'
    ).annotate(
        completion_date=TruncDate('completed_at')  # Use completed_at instead of updated_at
    ).values('completion_date').annotate(
        count=Count('id')
    ).order_by('-completion_date')
    
    # Convertir en set pour une recherche plus rapide
    completion_dates = {item['completion_date'] for item in daily_completions}
    
    # Vérifier le nombre de jours consécutifs
    consecutive_days = 0
    current_date = timezone.now().date()
    
    while current_date in completion_dates:
        consecutive_days += 1
        current_date -= timedelta(days=1)
    
    return consecutive_days

# Signal pour les suppressions d'utilisateurs
@receiver(post_delete, sender=User)
def cleanup_user_notifications(sender, instance, **kwargs):
    """
    Supprime toutes les notifications associées à un utilisateur supprimé
    """
    Notification.objects.filter(user=instance).delete()
    NotificationSetting.objects.filter(user=instance).delete()