"""
Command to clear terms notification cache
"""
from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.contrib.auth import get_user_model
from datetime import datetime

User = get_user_model()


class Command(BaseCommand):
    help = 'Clear terms notification cache for all users or specific user'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-email',
            type=str,
            help='Clear cache only for this specific user email'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Clear cache for all users'
        )

    def handle(self, *args, **options):
        user_email = options.get('user_email')
        clear_all = options.get('all')

        if user_email:
            try:
                user = User.objects.get(email=user_email)
                today = datetime.now().date()
                cache_key = f"terms_notification_sent_{user.id}_{today}"
                
                if cache.delete(cache_key):
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Cleared terms cache for user: {user_email}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'No cache found for user: {user_email}')
                    )
                    
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User with email {user_email} not found')
                )
                return
                
        elif clear_all:
            # Clear all terms-related cache
            cache.delete_many([key for key in cache._cache.keys() if 'terms_notification_sent_' in key])
            self.stdout.write(
                self.style.SUCCESS('✓ Cleared all terms notification cache')
            )
            
        else:
            self.stdout.write(
                self.style.ERROR('Please specify --user-email or --all')
            )