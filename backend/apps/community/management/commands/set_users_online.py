from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.community.models import Profile

User = get_user_model()


class Command(BaseCommand):
    help = 'Set some test users as online'

    def handle(self, *args, **options):
        self.stdout.write('Setting test users online status...')
        
        # Get test users
        online_users = ['marie_fr', 'anna_de']  # Set these users as online
        offline_users = ['carlos_es', 'takeshi_jp', 'elena_it']  # Set these as offline
        
        for username in online_users:
            try:
                user = User.objects.get(username=username)
                profile, _ = Profile.objects.get_or_create(user=user)
                profile.is_online = True
                profile.save()
                self.stdout.write(f'Set {username} as ONLINE')
            except User.DoesNotExist:
                self.stdout.write(f'User {username} not found')
        
        for username in offline_users:
            try:
                user = User.objects.get(username=username)
                profile, _ = Profile.objects.get_or_create(user=user)
                profile.is_online = False
                profile.save()
                self.stdout.write(f'Set {username} as OFFLINE')
            except User.DoesNotExist:
                self.stdout.write(f'User {username} not found')
        
        # Count online users
        online_count = Profile.objects.filter(is_online=True).count()
        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted! {online_count} users are now online.'
            )
        )