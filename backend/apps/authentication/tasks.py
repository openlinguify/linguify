"""
Async tasks for the authentication module 
"""
import logging
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from datetime import timedelta

User = get_user_model()
logger = logging.getLogger(__name__)


def remind_users_to_accept_terms():
    """
    Send email reminders to active users who haven't accepted the terms
    """
    # Get all active users who haven't accepted terms
    users_to_remind = User.objects.filter(
        is_active=True,
        terms_accepted=False,
        email_notifications=True  # Only send to users who have enabled email notifications
    )
    
    logger.info(f"Sending terms acceptance reminders to {users_to_remind.count()} users")
    
    for user in users_to_remind:
        try:
            # Prepare email content
            context = {
                'user': user,
                'terms_url': f"{settings.FRONTEND_URL}/annexes/legal",
                'app_name': "Linguify"
            }
            
            # Render email content from templates
            subject = "Action required: Accept Terms and Conditions"
            html_message = render_to_string('emails/terms_reminder.html', context)
            plain_message = render_to_string('emails/terms_reminder.txt', context)
            
            # Send email
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False
            )
            
            logger.info(f"Terms reminder sent to {user.email}")
        except Exception as e:
            logger.error(f"Failed to send terms reminder to {user.email}: {str(e)}")


def check_terms_compliance():
    """
    Generate a report on terms compliance statistics
    """
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    accepted = User.objects.filter(terms_accepted=True).count()
    not_accepted = User.objects.filter(terms_accepted=False).count()
    
    # Get stats for active users
    active_accepted = User.objects.filter(is_active=True, terms_accepted=True).count()
    active_not_accepted = User.objects.filter(is_active=True, terms_accepted=False).count()
    
    # Get stats for recent acceptances (last 7 days)
    one_week_ago = timezone.now() - timedelta(days=7)
    recent_acceptances = User.objects.filter(
        terms_accepted=True,
        terms_accepted_at__gte=one_week_ago
    ).count()
    
    # Prepare report
    report = (
        f"Terms & Conditions Compliance Report\n"
        f"======================================\n"
        f"Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"Total users: {total_users}\n"
        f"Active users: {active_users}\n\n"
        f"Terms accepted: {accepted} ({accepted/total_users*100:.1f}% of all users)\n"
        f"Terms not accepted: {not_accepted} ({not_accepted/total_users*100:.1f}% of all users)\n\n"
        f"Active users who accepted terms: {active_accepted} ({active_accepted/active_users*100:.1f}% of active users)\n"
        f"Active users who haven't accepted terms: {active_not_accepted} ({active_not_accepted/active_users*100:.1f}% of active users)\n\n"
        f"Recent acceptances (last 7 days): {recent_acceptances}\n"
    )
    
    logger.info(report)
    
    # Could also email this report to administrators
    try:
        admin_emails = User.objects.filter(is_superuser=True).values_list('email', flat=True)
        if admin_emails:
            send_mail(
                subject="Terms Compliance Weekly Report",
                message=report,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=list(admin_emails),
                fail_silently=False
            )
    except Exception as e:
        logger.error(f"Failed to send terms compliance report: {str(e)}")
        
    return report