# backend/apps/notification/services.py
import json
import logging
import time
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext as _, activate, get_language

# Optional import for web push notifications
try:
    from pywebpush import webpush, WebPushException
    WEBPUSH_AVAILABLE = True
except ImportError:
    WEBPUSH_AVAILABLE = False
    webpush = None
    WebPushException = Exception

from .models.notification_models import Notification, NotificationType, NotificationPriority, NotificationSetting, NotificationDevice
from .serializers import NotificationSerializer

User = get_user_model()
logger = logging.getLogger(__name__)

# Default VAPID keys (should be overridden in settings)
DEFAULT_VAPID_CLAIMS = {
    "sub": "mailto:info@linguify.com",
}

# Cache of user notification settings (to reduce DB queries)
_user_notification_settings_cache = {}
_user_notification_settings_cache_expiry = {}
SETTINGS_CACHE_TTL = 300  # 5 minutes


class NotificationDeliveryService:
    """
    Service for delivering notifications through various channels
    """

    @staticmethod
    def create_and_deliver(
        user: User,
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.INFO,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        data: Optional[Dict] = None,
        action_url: Optional[str] = None,
        **kwargs
    ) -> Optional[Notification]:
        """
        Create a notification and deliver it through enabled channels

        Args:
            user: User to send notification to
            title: Notification title
            message: Notification message
            notification_type: Type of notification
            priority: Priority level
            data: Additional data for the notification
            action_url: URL for action button
            **kwargs: Additional fields for notification

        Returns:
            Created Notification object or None if failed
        """
        try:
            # Create notification in database
            notification_data = data or {}
            if action_url:
                notification_data['action_url'] = action_url

            notification = Notification.objects.create(
                user=user,
                title=title,
                message=message,
                type=notification_type,
                priority=priority,
                data=notification_data,
                **kwargs
            )

            # Get user's notification settings
            settings = NotificationDeliveryService._get_user_notification_settings(user)

            # Deliver through WebSocket (always enabled)
            NotificationDeliveryService._deliver_via_websocket(notification)

            # Deliver through other channels based on settings
            if settings.get('push_notifications', False):
                NotificationDeliveryService._deliver_via_push(notification)

            if settings.get('email_notifications', False):
                # Only send email for important notifications
                if priority == NotificationPriority.HIGH:
                    NotificationDeliveryService._deliver_via_email(notification)

            logger.info(f"Notification {notification.id} created and delivered to user {user.id}")
            return notification

        except Exception as e:
            logger.error(f"Failed to create/deliver notification: {str(e)}", exc_info=True)
            return None

    @staticmethod
    def _get_user_notification_settings(user: User) -> Dict:
        """
        Get user notification settings with caching
        """
        # Check cache
        if user.id in _user_notification_settings_cache:
            if time.time() < _user_notification_settings_cache_expiry.get(user.id, 0):
                return _user_notification_settings_cache[user.id]

        # Load from database
        try:
            setting = NotificationSetting.objects.get(user=user)
            settings = {
                'push_notifications': setting.push_enabled,
                'email_notifications': setting.email_enabled,
                'web_notifications': setting.web_enabled,
                'quiet_hours_start': setting.quiet_hours_start if setting.quiet_hours_enabled else None,
                'quiet_hours_end': setting.quiet_hours_end if setting.quiet_hours_enabled else None,
            }
        except NotificationSetting.DoesNotExist:
            # Return default settings
            settings = {
                'push_notifications': True,
                'email_notifications': True,
                'web_notifications': True,
                'quiet_hours_start': None,
                'quiet_hours_end': None,
            }

        # Update cache
        _user_notification_settings_cache[user.id] = settings
        _user_notification_settings_cache_expiry[user.id] = time.time() + SETTINGS_CACHE_TTL

        return settings

    @staticmethod
    def _deliver_via_websocket(notification: Notification):
        """
        Deliver notification via WebSocket
        """
        try:
            channel_layer = get_channel_layer()

            # Serialize notification
            serializer = NotificationSerializer(notification)

            # Send to user's notification channel
            async_to_sync(channel_layer.group_send)(
                f"notifications_{notification.user.id}",
                {
                    "type": "notification_message",
                    "notification": serializer.data
                }
            )

            logger.debug(f"WebSocket notification sent to user {notification.user.id}")

        except Exception as e:
            logger.error(f"Failed to send WebSocket notification: {str(e)}")

    @staticmethod
    def _deliver_via_push(notification: Notification):
        """
        Deliver notification via web push
        """
        if not WEBPUSH_AVAILABLE:
            logger.warning("Web push not available (pywebpush not installed)")
            return

        try:
            # Get user's registered devices
            devices = NotificationDevice.objects.filter(
                user=notification.user,
                is_active=True
            )

            for device in devices:
                try:
                    # Prepare push data
                    push_data = {
                        'title': notification.title,
                        'body': notification.message,
                        'icon': '/static/images/logo.png',
                        'badge': '/static/images/badge.png',
                        'url': notification.data.get('action_url') if notification.data else '/',
                        'tag': f'notification-{notification.id}',
                        'requireInteraction': notification.priority >= NotificationPriority.HIGH,
                    }

                    # Send push notification
                    webpush(
                        subscription_info={
                            'endpoint': device.endpoint,
                            'keys': {
                                'p256dh': device.public_key,
                                'auth': device.auth_key,
                            }
                        },
                        data=json.dumps(push_data),
                        vapid_private_key=settings.VAPID_PRIVATE_KEY,
                        vapid_claims=DEFAULT_VAPID_CLAIMS
                    )

                    logger.debug(f"Push notification sent to device {device.id}")

                except WebPushException as e:
                    # Handle push errors (e.g., expired subscription)
                    if e.response and e.response.status_code == 410:
                        # Subscription expired, deactivate device
                        device.is_active = False
                        device.save()
                        logger.info(f"Deactivated expired device {device.id}")
                    else:
                        logger.error(f"Push notification failed: {str(e)}")

        except Exception as e:
            logger.error(f"Failed to send push notifications: {str(e)}")

    @staticmethod
    def _deliver_via_email(notification: Notification):
        """
        Deliver notification via email
        """
        try:
            # Don't send email if user has no email
            if not notification.user.email:
                return

            # Prepare email context
            context = {
                'user': notification.user,
                'notification': notification,
                'action_url': notification.data.get('action_url') if notification.data else None,
                'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000',
            }

            # Render email templates
            subject = f"[Linguify] {notification.title}"
            html_message = render_to_string('notifications/email/notification.html', context)
            plain_message = render_to_string('notifications/email/notification.txt', context)

            # Send email
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification.user.email],
                html_message=html_message,
                fail_silently=False
            )

            logger.info(f"Email notification sent to {notification.user.email}")

        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")


class NotificationManager:
    """
    Manager for notification operations
    """

    @staticmethod
    def mark_as_read(notification_ids: List[int], user: User) -> int:
        """
        Mark notifications as read

        Args:
            notification_ids: List of notification IDs to mark as read
            user: User who owns the notifications

        Returns:
            Number of notifications marked as read
        """
        try:
            count = Notification.objects.filter(
                id__in=notification_ids,
                user=user,
                is_read=False
            ).update(
                is_read=True,
                read_at=timezone.now()
            )

            logger.info(f"Marked {count} notifications as read for user {user.id}")
            return count

        except Exception as e:
            logger.error(f"Failed to mark notifications as read: {str(e)}")
            return 0

    @staticmethod
    def mark_all_as_read(user: User) -> int:
        """
        Mark all notifications as read for a user

        Args:
            user: User whose notifications to mark as read

        Returns:
            Number of notifications marked as read
        """
        try:
            count = Notification.objects.filter(
                user=user,
                is_read=False
            ).update(
                is_read=True,
                read_at=timezone.now()
            )

            logger.info(f"Marked all ({count}) notifications as read for user {user.id}")
            return count

        except Exception as e:
            logger.error(f"Failed to mark all notifications as read: {str(e)}")
            return 0

    @staticmethod
    def delete_notifications(notification_ids: List[int], user: User) -> int:
        """
        Delete notifications

        Args:
            notification_ids: List of notification IDs to delete
            user: User who owns the notifications

        Returns:
            Number of notifications deleted
        """
        try:
            count, _ = Notification.objects.filter(
                id__in=notification_ids,
                user=user
            ).delete()

            logger.info(f"Deleted {count} notifications for user {user.id}")
            return count

        except Exception as e:
            logger.error(f"Failed to delete notifications: {str(e)}")
            return 0

    @staticmethod
    def get_unread_count(user: User) -> int:
        """
        Get count of unread notifications for a user

        Args:
            user: User to get unread count for

        Returns:
            Number of unread notifications
        """
        try:
            return Notification.objects.filter(
                user=user,
                is_read=False
            ).count()
        except Exception as e:
            logger.error(f"Failed to get unread count: {str(e)}")
            return 0

    @staticmethod
    def cleanup_old_notifications(days: int = 30) -> int:
        """
        Delete notifications older than specified days

        Args:
            days: Number of days to keep notifications

        Returns:
            Number of notifications deleted
        """
        try:
            cutoff_date = timezone.now() - timedelta(days=days)

            # Keep important notifications longer
            count, _ = Notification.objects.filter(
                created_at__lt=cutoff_date,
                priority__lt=NotificationPriority.HIGH  # Don't delete high priority
            ).delete()

            logger.info(f"Cleaned up {count} old notifications")
            return count

        except Exception as e:
            logger.error(f"Failed to cleanup old notifications: {str(e)}")
            return 0


class NotificationService:
    """
    High-level notification service
    """

    @staticmethod
    def notify_flashcard_review(user: User, count: int) -> Optional[Notification]:
        """
        Send flashcard review reminder notification with localization
        """
        # Save current language
        current_language = get_language()

        try:
            # Activate user's interface language
            user_language = getattr(user, 'interface_language', 'en')
            activate(user_language)

            # Create localized notification
            title = _('🔥 REVISION REMINDER')
            message = _('You have %(count)d cards to review today. Keep your streak going!') % {'count': count}

            return NotificationDeliveryService.create_and_deliver(
                user=user,
                title=title,
                message=message,
                notification_type=NotificationType.REVISION_REMINDER,
                priority=NotificationPriority.MEDIUM,
                data={'count': count},
                action_url='/language-learning/reviews/'
            )
        finally:
            # Restore original language
            activate(current_language)

    @staticmethod
    def notify_achievement_unlocked(user: User, achievement: str) -> Optional[Notification]:
        """
        Send achievement unlocked notification with localization
        """
        current_language = get_language()

        try:
            user_language = getattr(user, 'interface_language', 'en')
            activate(user_language)

            title = _('🏆 Achievement Unlocked!')
            message = _('You earned: %(achievement)s') % {'achievement': achievement}

            return NotificationDeliveryService.create_and_deliver(
                user=user,
                title=title,
                message=message,
                notification_type=NotificationType.ACHIEVEMENT,
                priority=NotificationPriority.MEDIUM,
                data={'achievement': achievement}
            )
        finally:
            activate(current_language)

    @staticmethod
    def notify_course_completed(user: User, course_name: str) -> Optional[Notification]:
        """
        Send course completion notification with localization
        """
        current_language = get_language()

        try:
            user_language = getattr(user, 'interface_language', 'en')
            activate(user_language)

            title = _('🎉 Course Completed!')
            message = _('Congratulations! You completed %(course)s') % {'course': course_name}

            return NotificationDeliveryService.create_and_deliver(
                user=user,
                title=title,
                message=message,
                notification_type=NotificationType.ACHIEVEMENT,
                priority=NotificationPriority.HIGH,
                data={'course': course_name}
            )
        finally:
            activate(current_language)

    @staticmethod
    def notify_system_update(user: User, update_info: str) -> Optional[Notification]:
        """
        Send system update notification with localization
        """
        current_language = get_language()

        try:
            user_language = getattr(user, 'interface_language', 'en')
            activate(user_language)

            title = _('System Update')
            message = update_info

            return NotificationDeliveryService.create_and_deliver(
                user=user,
                title=title,
                message=message,
                notification_type=NotificationType.SYSTEM,
                priority=NotificationPriority.LOW
            )
        finally:
            activate(current_language)


def send_terms_acceptance_email_and_notification(user):
    """
    Envoie un email et crée une notification pour demander l'acceptation des conditions d'utilisation
    avec support multilingue basé sur interface_language
    """
    current_language = get_language()

    try:
        # Activer la langue de l'interface utilisateur
        user_language = getattr(user, 'interface_language', 'en')
        activate(user_language)

        # Créer la notification localisée
        title = _('Action Required: Accept Terms of Use')
        message = _('Please accept our updated terms of use to continue using Linguify.')

        notification = NotificationDeliveryService.create_and_deliver(
            user=user,
            title=title,
            message=message,
            notification_type=NotificationType.ACTION_REQUIRED,
            priority=NotificationPriority.HIGH,
            data={'action': 'accept_terms'},
            action_url=f"{getattr(settings, 'SITE_URL', 'http://localhost:8000')}/api/auth/terms/accept-page/"
        )

        # Envoyer l'email localisé
        portal_url = getattr(settings, 'PORTAL_URL', 'http://localhost:8080')
        context = {
            'user': user,
            'terms_url': f"{portal_url}/annexes/terms",
            'portal_url': portal_url,
            'app_name': "Open Linguify"
        }

        # Déterminer le template selon la langue
        template_base = 'emails/terms_reminder'
        html_template = f'{template_base}.html'
        txt_template = f'{template_base}.txt'

        # TODO: Créer des templates localisés (terms_reminder_fr.html, etc.)
        # Pour l'instant, utiliser le template par défaut

        subject = _('Action Required: Accept Terms of Use')
        html_message = render_to_string(html_template, context)
        plain_message = render_to_string(txt_template, context)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )

        logger.info(f"Terms acceptance email and notification sent to user {user.id} in language {user_language}")
        return True

    except Exception as e:
        logger.error(f"Failed to send terms acceptance email/notification: {str(e)}", exc_info=True)
        return False
    finally:
        # Restaurer la langue originale
        activate(current_language)