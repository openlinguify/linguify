"""
Signal handlers for authentication app
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import CookieConsent, CookieConsentLog


@receiver(post_save, sender=CookieConsent)
def log_cookie_consent_change(sender, instance, created, **kwargs):
    """
    Automatically log cookie consent changes
    """
    try:
        if created:
            # Log creation
            CookieConsentLog.objects.create(
                consent=instance,
                action='created',
                new_values=instance.to_dict(),
                ip_address=getattr(instance, '_current_ip', None),
                user_agent=getattr(instance, '_current_user_agent', None)
            )
        else:
            # Log update (only if not already logged by explicit save)
            if not getattr(instance, '_log_created', False):
                CookieConsentLog.objects.create(
                    consent=instance,
                    action='updated',
                    new_values=instance.to_dict(),
                    ip_address=getattr(instance, '_current_ip', None),
                    user_agent=getattr(instance, '_current_user_agent', None)
                )
    except Exception as e:
        # Don't let logging errors break the save
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error logging cookie consent change: {e}")


@receiver(pre_save, sender=CookieConsent)
def prepare_cookie_consent_log(sender, instance, **kwargs):
    """
    Prepare for logging by storing old values
    """
    if instance.pk:
        try:
            old_instance = CookieConsent.objects.get(pk=instance.pk)
            instance._old_values = old_instance.to_dict()
        except CookieConsent.DoesNotExist:
            instance._old_values = None
    else:
        instance._old_values = None