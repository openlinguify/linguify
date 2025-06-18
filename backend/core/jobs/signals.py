from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
import logging

from .models import JobApplication

logger = logging.getLogger(__name__)


# Store the old status before saving
@receiver(pre_save, sender=JobApplication)
def store_job_application_old_status(sender, instance, **kwargs):
    """Store the old status before saving for comparison"""
    if instance.pk:
        try:
            old_instance = JobApplication.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except JobApplication.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=JobApplication)
def handle_job_application_status_change(sender, instance, created, **kwargs):
    """Handle email notifications when job application status changes"""
    
    # Skip if this is a new application (already handled in views)
    if created:
        return
    
    # Get the old status from the instance
    old_status = getattr(instance, '_old_status', None)
    if old_status is None:
        return
    
    # Check if status has changed
    if old_status == instance.status:
        return
    
    # Log the status change
    logger.info(f"JobApplication {instance.id} status changed from {old_status} to {instance.status}")
    
    # Send appropriate notifications based on the new status
    try:
        # Send HR notification for important status changes
        hr_notification_statuses = ['interview', 'offer', 'hired', 'rejected']
        if instance.status in hr_notification_statuses:
            send_hr_status_notification(instance, old_status)
        
        # Send candidate notification for all status changes except 'submitted'
        if instance.status != 'submitted':
            send_candidate_status_notification(instance, old_status)
            
    except Exception as e:
        logger.error(f"Failed to send status change notification for application {instance.id}: {str(e)}")


def send_hr_status_notification(application, old_status):
    """Send notification to HR about important status changes"""
    try:
        status_emojis = {
            'interview': '🎯',
            'offer': '🎉',
            'hired': '✅',
            'rejected': '❌'
        }
        
        emoji = status_emojis.get(application.status, '📋')
        subject = f"{emoji} Status Update: {application.position.title} - {application.full_name}"
        
        context = {
            'application': application,
            'old_status': old_status,
            'new_status': application.status,
            'status_display': application.get_status_display(),
            'changed_at': timezone.now()
        }
        
        html_content = render_to_string('jobs/emails/hr_status_notification.html', context)
        text_content = render_to_string('jobs/emails/hr_status_notification.txt', context)
        
        email = EmailMessage(
            subject=subject,
            body=text_content,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@linguify.com'),
            to=['linguify.info@gmail.com'],
            reply_to=[application.email],
        )
        
        email.content_subtype = 'html'
        email.body = html_content
        email.send(fail_silently=False)
        
        logger.info(f"HR notification sent for application {application.id} status change to {application.status}")
        
    except Exception as e:
        logger.error(f"Failed to send HR notification: {str(e)}")
        raise


def send_candidate_status_notification(application, old_status):
    """Send notification to candidate about their application status change"""
    try:
        status_subjects = {
            'reviewed': f"📋 Your application is under review - {application.position.title}",
            'interview': f"🎯 Interview invitation - {application.position.title} at Linguify",
            'offer': f"🎉 Job offer - {application.position.title} at Linguify",
            'hired': f"✅ Welcome to Linguify! - {application.position.title}",
            'rejected': f"Application update - {application.position.title} at Linguify",
            'withdrawn': f"Application withdrawn - {application.position.title}"
        }
        
        subject = status_subjects.get(
            application.status, 
            f"Application update - {application.position.title} at Linguify"
        )
        
        context = {
            'application': application,
            'old_status': old_status,
            'new_status': application.status,
            'status_display': application.get_status_display(),
        }
        
        html_content = render_to_string('jobs/emails/candidate_status_notification.html', context)
        text_content = render_to_string('jobs/emails/candidate_status_notification.txt', context)
        
        email = EmailMessage(
            subject=subject,
            body=text_content,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@linguify.com'),
            to=[application.email],
            reply_to=['linguify.info@gmail.com'],
        )
        
        email.content_subtype = 'html'
        email.body = html_content
        email.send(fail_silently=False)
        
        logger.info(f"Candidate notification sent to {application.email} for status change to {application.status}")
        
    except Exception as e:
        logger.error(f"Failed to send candidate notification: {str(e)}")
        raise