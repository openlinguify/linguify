# -*- coding: utf-8 -*-
"""
Commande Django pour envoyer les rappels de révision
"""
import logging
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q, Count
from apps.revision.models.settings_models import RevisionSettings
from apps.revision.models.revision_flashcard import FlashcardDeck, Flashcard
from apps.notification.services import NotificationDeliveryService

User = get_user_model()
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Envoie des rappels de révision aux utilisateurs selon leurs paramètres'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-user',
            type=str,
            help='Tester avec un utilisateur spécifique (username ou email)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mode simulation - ne pas envoyer de vraies notifications'
        )
        parser.add_argument(
            '--force-time',
            type=str,
            help='Forcer une heure spécifique (format HH:MM)'
        )

    def handle(self, *args, **options):
        """Traite l'envoi des rappels de révision"""
        dry_run = options.get('dry_run', False)
        test_user = options.get('test_user')
        force_time = options.get('force_time')
        
        self.stdout.write(
            self.style.SUCCESS(
                f"🔔 Démarrage des rappels de révision - {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
        )
        
        if dry_run:
            self.stdout.write(self.style.WARNING("⚠️  Mode simulation activé - aucune notification ne sera envoyée"))
        
        if force_time:
            try:
                # Parse l'heure forcée
                hour, minute = map(int, force_time.split(':'))
                current_time = timezone.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
                self.stdout.write(self.style.WARNING(f"⏰ Heure forcée: {force_time}"))
            except ValueError:
                self.stdout.write(self.style.ERROR("❌ Format d'heure invalide. Utilisez HH:MM"))
                return
        else:
            current_time = timezone.now()
        
        # Filtrer les utilisateurs selon les paramètres
        if test_user:
            users_query = User.objects.filter(
                Q(username=test_user) | Q(email=test_user)
            )
            if not users_query.exists():
                self.stdout.write(self.style.ERROR(f"❌ Utilisateur '{test_user}' non trouvé"))
                return
        else:
            users_query = User.objects.filter(is_active=True)
        
        total_users = users_query.count()
        self.stdout.write(f"👥 {total_users} utilisateurs à vérifier")
        
        # Compteurs pour les statistiques
        users_checked = 0
        notifications_sent = 0
        users_with_settings = 0
        users_with_reminders_enabled = 0
        users_at_reminder_time = 0
        users_with_cards_due = 0
        
        for user in users_query.iterator():
            users_checked += 1
            
            try:
                # Obtenir les paramètres de révision
                try:
                    revision_settings = RevisionSettings.objects.get(user=user)
                    users_with_settings += 1
                except RevisionSettings.DoesNotExist:
                    if test_user:
                        self.stdout.write(
                            self.style.WARNING(f"⚠️  {user.username}: Aucun paramètre de révision")
                        )
                    continue
                
                # Vérifier si les rappels sont activés
                if not revision_settings.daily_reminder_enabled:
                    if test_user:
                        self.stdout.write(
                            self.style.WARNING(f"⚠️  {user.username}: Rappels désactivés")
                        )
                    continue
                
                users_with_reminders_enabled += 1
                
                # Vérifier l'heure du rappel
                if not self._is_reminder_time(revision_settings, current_time, force_time is not None):
                    if test_user:
                        reminder_time = revision_settings.reminder_time.strftime('%H:%M')
                        current_time_str = current_time.strftime('%H:%M')
                        self.stdout.write(
                            self.style.WARNING(
                                f"⚠️  {user.username}: Pas l'heure du rappel "
                                f"(configuré: {reminder_time}, actuel: {current_time_str})"
                            )
                        )
                    continue
                
                users_at_reminder_time += 1
                
                # Vérifier s'il y a des cartes à réviser
                cards_due_count = self._get_cards_due_count(user)
                if cards_due_count == 0:
                    if test_user:
                        self.stdout.write(
                            self.style.WARNING(f"⚠️  {user.username}: Aucune carte à réviser")
                        )
                    continue
                
                users_with_cards_due += 1
                
                # Envoyer la notification
                if not dry_run:
                    success = self._send_revision_reminder(user, cards_due_count, revision_settings)
                    if success:
                        notifications_sent += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"✅ {user.username}: Notification envoyée ({cards_due_count} cartes)"
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(f"❌ {user.username}: Échec de l'envoi")
                        )
                else:
                    notifications_sent += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✅ {user.username}: Notification simulée ({cards_due_count} cartes)"
                        )
                    )
                
            except Exception as e:
                logger.error(f"Erreur lors du traitement de l'utilisateur {user.username}: {e}")
                self.stdout.write(
                    self.style.ERROR(f"❌ {user.username}: Erreur - {str(e)}")
                )
        
        # Afficher les statistiques finales
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS("📊 STATISTIQUES FINALES"))
        self.stdout.write(f"👥 Utilisateurs vérifiés: {users_checked}")
        self.stdout.write(f"⚙️  Avec paramètres de révision: {users_with_settings}")
        self.stdout.write(f"🔔 Rappels activés: {users_with_reminders_enabled}")
        self.stdout.write(f"⏰ À l'heure du rappel: {users_at_reminder_time}")
        self.stdout.write(f"📚 Avec cartes à réviser: {users_with_cards_due}")
        self.stdout.write(f"📬 Notifications envoyées: {notifications_sent}")
        
        if notifications_sent > 0:
            self.stdout.write(
                self.style.SUCCESS(f"🎉 Rappels de révision terminés avec succès!")
            )
        else:
            self.stdout.write(
                self.style.WARNING("⚠️  Aucune notification envoyée")
            )

    def _is_reminder_time(self, revision_settings, current_time, force_time=False):
        """Vérifie si c'est l'heure du rappel pour cet utilisateur"""
        if force_time:
            # En mode force, on considère que c'est toujours l'heure
            return True
        
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

    def _get_cards_due_count(self, user):
        """Calcule le nombre de cartes à réviser pour un utilisateur"""
        try:
            # Obtenir tous les decks actifs de l'utilisateur
            active_decks = FlashcardDeck.objects.filter(
                user=user,
                is_active=True
            )
            
            if not active_decks.exists():
                return 0
            
            # Compter les cartes qui ont besoin d'être révisées
            # Ceci est une logique simplifiée - vous pouvez l'adapter selon votre algorithme de répétition espacée
            cards_due = Flashcard.objects.filter(
                deck__in=active_decks,
                deck__is_active=True
            ).count()
            
            return cards_due
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des cartes dues pour {user.username}: {e}")
            return 0

    def _send_revision_reminder(self, user, cards_due_count, revision_settings):
        """Envoie une notification de rappel de révision"""
        try:
            # Préparer le message personnalisé
            if cards_due_count == 1:
                title = "Rappel de révision"
                message = "Vous avez 1 carte à réviser ! C'est le moment parfait pour une session rapide."
            else:
                title = "Rappel de révision"
                message = f"Vous avez {cards_due_count} cartes à réviser ! Maintenez votre progression d'apprentissage."
            
            # Données additionnelles pour la notification
            data = {
                "cards_due_count": cards_due_count,
                "reminder_type": "daily_revision",
                "action": "start_revision",
                "session_duration": revision_settings.default_session_duration,
                "cards_per_session": revision_settings.cards_per_session
            }
            
            # Envoyer via le service de notifications
            from apps.notification.models.notification_models import NotificationType, NotificationPriority
            
            notification = NotificationDeliveryService.create_and_deliver(
                user=user,
                title=title,
                message=message,
                notification_type=NotificationType.FLASHCARD,
                priority=NotificationPriority.MEDIUM,
                data=data,
                expires_in_days=1,
                delivery_channels=['websocket', 'push', 'email']
            )
            
            return notification is not None
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la notification à {user.username}: {e}")
            return False