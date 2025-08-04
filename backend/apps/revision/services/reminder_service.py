# -*- coding: utf-8 -*-
"""
Service pour gérer les rappels de révision
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q, Count
from apps.revision.models.settings_models import RevisionSettings
from apps.revision.models.revision_flashcard import FlashcardDeck, Flashcard
from apps.notification.services import NotificationDeliveryService

User = get_user_model()
logger = logging.getLogger(__name__)


class RevisionReminderService:
    """Service pour gérer les rappels de révision"""
    
    @staticmethod
    def send_daily_reminders(dry_run: bool = False, test_user: Optional[str] = None) -> Dict[str, Any]:
        """
        Envoie les rappels quotidiens de révision
        
        Args:
            dry_run: Si True, simule l'envoi sans vraiment envoyer
            test_user: Si spécifié, ne traite que cet utilisateur
            
        Returns:
            Dictionnaire avec les statistiques d'envoi
        """
        current_time = timezone.now()
        stats = {
            'users_checked': 0,
            'notifications_sent': 0,
            'users_with_settings': 0,
            'users_with_reminders_enabled': 0,
            'users_at_reminder_time': 0,
            'users_with_cards_due': 0,
            'errors': []
        }
        
        # Filtrer les utilisateurs
        if test_user:
            users_query = User.objects.filter(
                Q(username=test_user) | Q(email=test_user),
                is_active=True
            )
        else:
            users_query = User.objects.filter(is_active=True)
        
        for user in users_query.iterator():
            stats['users_checked'] += 1
            
            try:
                result = RevisionReminderService._process_user_reminder(
                    user, current_time, dry_run
                )
                
                # Mettre à jour les statistiques
                for key in ['users_with_settings', 'users_with_reminders_enabled', 
                           'users_at_reminder_time', 'users_with_cards_due']:
                    if result.get(key):
                        stats[key] += 1
                
                if result.get('notification_sent'):
                    stats['notifications_sent'] += 1
                
            except Exception as e:
                error_msg = f"Erreur pour {user.username}: {str(e)}"
                stats['errors'].append(error_msg)
                logger.error(error_msg)
        
        return stats
    
    @staticmethod
    def _process_user_reminder(user: User, current_time: datetime, dry_run: bool) -> Dict[str, Any]:
        """
        Traite le rappel pour un utilisateur spécifique
        
        Args:
            user: Utilisateur à traiter
            current_time: Heure actuelle
            dry_run: Mode simulation
            
        Returns:
            Dictionnaire avec les résultats du traitement
        """
        result = {
            'users_with_settings': False,
            'users_with_reminders_enabled': False,
            'users_at_reminder_time': False,
            'users_with_cards_due': False,
            'notification_sent': False
        }
        
        # Obtenir les paramètres de révision
        try:
            revision_settings = RevisionSettings.objects.get(user=user)
            result['users_with_settings'] = True
        except RevisionSettings.DoesNotExist:
            return result
        
        # Vérifier si les rappels sont activés
        if not revision_settings.daily_reminder_enabled:
            return result
        result['users_with_reminders_enabled'] = True
        
        # Vérifier l'heure du rappel
        if not RevisionReminderService._is_reminder_time(revision_settings, current_time):
            return result
        result['users_at_reminder_time'] = True
        
        # Vérifier s'il y a des cartes à réviser
        cards_due_count = RevisionReminderService._get_cards_due_count(user)
        if cards_due_count == 0:
            return result
        result['users_with_cards_due'] = True
        
        # Envoyer la notification
        if not dry_run:
            success = RevisionReminderService._send_revision_reminder(
                user, cards_due_count, revision_settings
            )
            result['notification_sent'] = success
        else:
            # En mode dry_run, on simule sans envoyer
            result['notification_sent'] = False
        
        return result
    
    @staticmethod
    def _is_reminder_time(revision_settings: RevisionSettings, current_time: datetime) -> bool:
        """
        Vérifie si c'est l'heure du rappel pour cet utilisateur
        
        Args:
            revision_settings: Paramètres de révision de l'utilisateur
            current_time: Heure actuelle
            
        Returns:
            True si c'est l'heure du rappel
        """
        reminder_time = revision_settings.reminder_time
        current_time_only = current_time.time()
        
        # Tolérance de ±5 minutes
        tolerance = timedelta(minutes=5)
        
        # Convertir en datetime pour faire les calculs
        today = current_time.date()
        reminder_datetime = datetime.combine(today, reminder_time)
        current_datetime = datetime.combine(today, current_time_only)
        
        # Vérifier si on est dans la fenêtre de tolérance
        time_diff = abs(current_datetime - reminder_datetime)
        return time_diff <= tolerance
    
    @staticmethod
    def _get_cards_due_count(user: User) -> int:
        """
        Calcule le nombre de cartes à réviser pour un utilisateur
        
        Args:
            user: Utilisateur
            
        Returns:
            Nombre de cartes à réviser
        """
        try:
            # Obtenir tous les decks actifs de l'utilisateur
            active_decks = FlashcardDeck.objects.filter(
                user=user,
                is_active=True
            )
            
            if not active_decks.exists():
                return 0
            
            # Compter les cartes qui ont besoin d'être révisées
            cards_due = Flashcard.objects.filter(
                deck__in=active_decks,
                deck__is_active=True
            ).count()
            
            return cards_due
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des cartes dues pour {user.username}: {e}")
            return 0
    
    @staticmethod
    def _send_revision_reminder(user: User, cards_due_count: int, revision_settings: RevisionSettings) -> bool:
        """
        Envoie une notification de rappel de révision
        
        Args:
            user: Utilisateur à notifier
            cards_due_count: Nombre de cartes à réviser
            revision_settings: Paramètres de révision
            
        Returns:
            True si la notification a été envoyée avec succès
        """
        try:
            logger.info(f"Début envoi notification pour {user.username} - {cards_due_count} cartes")
            
            # Préparer le message personnalisé
            if cards_due_count == 1:
                title = "⏰ Rappel de révision"
                message = "Vous avez 1 carte à réviser ! C'est le moment parfait pour une session rapide."
            else:
                title = "⏰ Rappel de révision"
                message = f"Vous avez {cards_due_count} cartes à réviser ! Maintenez votre progression d'apprentissage."
            
            # Données additionnelles pour la notification
            data = {
                "cards_due_count": cards_due_count,
                "reminder_type": "daily_revision",
                "action": "start_revision",
                "session_duration": revision_settings.default_session_duration,
                "cards_per_session": revision_settings.cards_per_session,
                "url": "/revision/flashcards/"
            }
            
            # Envoyer via le service de notifications
            # Utiliser le type FLASHCARD qui existe dans NotificationType
            from apps.notification.models.notification_models import NotificationType, NotificationPriority
            
            logger.info(f"Envoi notification avec type: {NotificationType.FLASHCARD}, priorité: {NotificationPriority.MEDIUM}")
            
            notification = NotificationDeliveryService.create_and_deliver(
                user=user,
                title=title,
                message=message,
                notification_type=NotificationType.FLASHCARD,
                priority=NotificationPriority.MEDIUM,
                data=data,
                expires_in_days=1,
                delivery_channels=['websocket', 'push']
            )
            
            logger.info(f"Résultat de l'envoi: {notification is not None}")
            
            if notification:
                logger.info(f"Rappel de révision envoyé à {user.username} ({cards_due_count} cartes)")
                return True
            else:
                logger.warning(f"Rappel de révision non envoyé à {user.username} (paramètres utilisateur ou erreur)")
                return False
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la notification à {user.username}: {e}")
            return False
    
    @staticmethod
    def send_immediate_reminder(user: User, force: bool = False) -> bool:
        """
        Envoie un rappel immédiat à un utilisateur spécifique
        
        Args:
            user: Utilisateur à notifier
            force: Si True, ignore les paramètres d'heure et envoie toujours
            
        Returns:
            True si la notification a été envoyée
        """
        try:
            revision_settings = RevisionSettings.objects.get(user=user)
        except RevisionSettings.DoesNotExist:
            logger.warning(f"Aucun paramètre de révision pour {user.username}")
            return False
        
        if not revision_settings.daily_reminder_enabled and not force:
            logger.info(f"Rappels désactivés pour {user.username}")
            return False
        
        cards_due_count = RevisionReminderService._get_cards_due_count(user)
        if cards_due_count == 0 and not force:
            logger.info(f"Aucune carte à réviser pour {user.username}")
            return False
        
        return RevisionReminderService._send_revision_reminder(
            user, max(cards_due_count, 1), revision_settings
        )
    
    @staticmethod
    def get_users_due_for_reminder(tolerance_minutes: int = 5) -> List[User]:
        """
        Obtient la liste des utilisateurs qui doivent recevoir un rappel maintenant
        
        Args:
            tolerance_minutes: Tolérance en minutes autour de l'heure du rappel
            
        Returns:
            Liste des utilisateurs éligibles
        """
        current_time = timezone.now()
        current_time_only = current_time.time()
        
        # Créer une fenêtre de temps avec tolérance
        tolerance = timedelta(minutes=tolerance_minutes)
        start_time = (current_time - tolerance).time()
        end_time = (current_time + tolerance).time()
        
        # Obtenir les utilisateurs avec des paramètres de révision actifs
        users = User.objects.filter(
            is_active=True,
            revision_settings__daily_reminder_enabled=True,
            revision_settings__reminder_time__gte=start_time,
            revision_settings__reminder_time__lte=end_time
        ).select_related('revision_settings')
        
        return list(users)