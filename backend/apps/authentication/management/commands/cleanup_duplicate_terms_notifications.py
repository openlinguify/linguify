"""
Command to clean up duplicate terms notifications
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from backend.apps.notification.models.notification_models import Notification
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Clean up duplicate terms notifications, keeping only the most recent one per user'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Only show what would be deleted without actually deleting'
        )
        parser.add_argument(
            '--user-email',
            type=str,
            help='Clean up notifications only for this specific user email'
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run')
        user_email = options.get('user_email')

        if user_email:
            try:
                users = [User.objects.get(email=user_email)]
                self.stdout.write(f'Processing notifications for user: {user_email}')
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User with email {user_email} not found')
                )
                return
        else:
            users = User.objects.all()
            self.stdout.write(f'Processing notifications for all users')

        total_deleted = 0
        
        for user in users:
            # Get all terms notifications for this user
            terms_notifications = Notification.objects.filter(
                user=user,
                type='terms'
            ).order_by('-created_at')
            
            if terms_notifications.count() <= 1:
                continue
                
            # Keep the most recent one, delete the rest
            most_recent = terms_notifications.first()
            duplicates_list = list(terms_notifications[1:])  # Convert to list to avoid slicing issues
            
            duplicate_count = len(duplicates_list)
            if duplicate_count > 0:
                self.stdout.write(
                    f'User {user.email}: Found {duplicate_count} duplicate terms notifications'
                )
                
                if dry_run:
                    self.stdout.write(
                        self.style.WARNING(f'  [DRY RUN] Would delete {duplicate_count} notifications')
                    )
                    for notif in duplicates_list:
                        self.stdout.write(
                            f'    - ID: {notif.id}, Created: {notif.created_at}, Read: {notif.is_read}'
                        )
                else:
                    # Actually delete the duplicates one by one
                    deleted_count = 0
                    for notif in duplicates_list:
                        notif.delete()
                        deleted_count += 1
                    
                    total_deleted += deleted_count
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✓ Deleted {deleted_count} duplicate notifications')
                    )
                    self.stdout.write(
                        f'    Kept most recent: ID {most_recent.id}, Created: {most_recent.created_at}'
                    )

        # Summary
        self.stdout.write('\n' + '='*50)
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN COMPLETE - No notifications were actually deleted')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'CLEANUP COMPLETE - Deleted {total_deleted} duplicate notifications')
            )
            
        # Also clean up very old read notifications
        if not dry_run:
            old_threshold = timezone.now() - timedelta(days=30)
            old_read_notifications = Notification.objects.filter(
                type='terms',
                is_read=True,
                created_at__lt=old_threshold
            )
            
            old_count = old_read_notifications.count()
            if old_count > 0:
                old_read_notifications.delete()
                self.stdout.write(
                    self.style.SUCCESS(f'Also deleted {old_count} old read terms notifications (>30 days)')
                )