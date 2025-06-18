"""
Command to manually send terms acceptance notification to users
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.notification.services import send_terms_acceptance_email_and_notification
from apps.notification.models import Notification

User = get_user_model()


class Command(BaseCommand):
    help = 'Send terms acceptance notification to users who have not accepted terms'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Send notification only to this specific email'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Send to all users who have not accepted terms'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Only show what would be sent without actually sending'
        )

    def handle(self, *args, **options):
        email = options.get('email')
        send_all = options.get('all')
        dry_run = options.get('dry_run')

        if not email and not send_all:
            self.stdout.write(
                self.style.ERROR('Please specify --email or --all')
            )
            return

        # Get users to notify
        if email:
            users = User.objects.filter(email=email)
            if not users.exists():
                self.stdout.write(
                    self.style.ERROR(f'No user found with email: {email}')
                )
                return
        else:
            users = User.objects.filter(terms_accepted=False, is_active=True)

        total_users = users.count()
        self.stdout.write(
            self.style.SUCCESS(f'Found {total_users} users to notify')
        )

        success_count = 0
        error_count = 0

        for user in users:
            self.stdout.write(f'\nProcessing user: {user.email}')
            self.stdout.write(f'  - Terms accepted: {user.terms_accepted}')
            self.stdout.write(f'  - Email notifications: {user.email_notifications}')
            
            # Check existing notifications
            existing = Notification.objects.filter(
                user=user,
                type='terms',
                is_read=False
            ).count()
            self.stdout.write(f'  - Existing unread terms notifications: {existing}')

            if dry_run:
                self.stdout.write(
                    self.style.WARNING('  - [DRY RUN] Would send notification')
                )
                continue

            try:
                success = send_terms_acceptance_email_and_notification(user)
                if success:
                    self.stdout.write(
                        self.style.SUCCESS('  - ✓ Notification sent successfully')
                    )
                    success_count += 1
                else:
                    self.stdout.write(
                        self.style.ERROR('  - ✗ Failed to send notification')
                    )
                    error_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  - ✗ Error: {str(e)}')
                )
                error_count += 1

        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS(f'Successfully sent: {success_count}')
        )
        if error_count > 0:
            self.stdout.write(
                self.style.ERROR(f'Failed: {error_count}')
            )
        if dry_run:
            self.stdout.write(
                self.style.WARNING('This was a dry run - no notifications were actually sent')
            )