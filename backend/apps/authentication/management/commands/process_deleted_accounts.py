"""
Management command to process accounts pending deletion.
This script should run daily via a scheduled task.
"""
import logging
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

User = get_user_model()
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Process accounts scheduled for deletion and send reminders'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without making any changes'
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Running in dry-run mode - no changes will be made'))
        
        # Process accounts to be deleted
        self.process_expired_accounts(dry_run)
        
        # Send reminder emails
        self.send_reminder_emails(dry_run)
        
        self.stdout.write(self.style.SUCCESS('Account processing completed successfully'))

    def process_expired_accounts(self, dry_run):
        """
        Delete accounts that have reached their deletion date
        """
        now = timezone.now()
        
        accounts_to_delete = User.objects.filter(
            is_pending_deletion=True,
            deletion_date__lte=now
        )
        
        count = accounts_to_delete.count()
        self.stdout.write(f'Found {count} accounts to delete')
        
        if dry_run:
            for user in accounts_to_delete:
                self.stdout.write(f"Would delete user {user.email} (deletion date: {user.deletion_date})")
            return
            
        for user in accounts_to_delete:
            try:
                self.stdout.write(f"Deleting user {user.email} (deletion date: {user.deletion_date})")
                user.delete_user_account(anonymize=True, immediate=True)
                logger.info(f"Successfully deleted account for {user.email}")
            except Exception as e:
                logger.error(f"Failed to delete account for {user.email}: {str(e)}")

    def send_reminder_emails(self, dry_run):
        """
        Send reminder emails to users whose accounts are approaching deletion
        """
        now = timezone.now()
        
        # Find accounts that will be deleted in 3 days
        reminder_date = now + timedelta(days=3)
        accounts_for_reminder = User.objects.filter(
            is_pending_deletion=True,
            deletion_date__date=reminder_date.date()
        )
        
        count = accounts_for_reminder.count()
        self.stdout.write(f'Found {count} accounts to send reminders to')
        
        if dry_run:
            for user in accounts_for_reminder:
                self.stdout.write(f"Would send reminder to {user.email} (deletion date: {user.deletion_date})")
            return
            
        for user in accounts_for_reminder:
            try:
                # Construct email content
                subject = "Your Linguify account will be deleted in 3 days"
                message = f"""
Hello,

Your Linguify account is scheduled for deletion in 3 days.

If you wish to keep your account, please log in and restore your account before {user.deletion_date.strftime('%Y-%m-%d %H:%M')}.

To restore your account, visit: {settings.BASE_URL}/account-recovery

If you do nothing, your account will be permanently deleted on {user.deletion_date.strftime('%Y-%m-%d')}.

Thank you,
The Linguify Team
"""
                
                # Send email
                self.stdout.write(f"Sending reminder to {user.email}")
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                
                logger.info(f"Successfully sent deletion reminder to {user.email}")
            except Exception as e:
                logger.error(f"Failed to send reminder to {user.email}: {str(e)}")