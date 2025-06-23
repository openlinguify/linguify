from django.core.management.base import BaseCommand
from django.db import transaction
from apps.authentication.models import User
from apps.community.models import Profile


class Command(BaseCommand):
    help = 'Create or update community profiles for existing users'

    def handle(self, *args, **options):
        self.stdout.write('Setting up community profiles for existing users...')
        
        users = User.objects.all()
        created_count = 0
        updated_count = 0
        
        with transaction.atomic():
            for user in users:
                profile, created = Profile.objects.get_or_create(user=user)
                
                # Set default learning and teaching languages based on user's settings
                if created or not profile.learning_languages:
                    if user.target_language:
                        # Get the full language name from LANGUAGE_CHOICES
                        from apps.authentication.models import LANGUAGE_CHOICES
                        lang_dict = dict(LANGUAGE_CHOICES)
                        target_lang_name = lang_dict.get(user.target_language, user.target_language)
                        profile.learning_languages = [target_lang_name]
                
                if created or not profile.teaching_languages:
                    if user.native_language:
                        # Get the full language name from LANGUAGE_CHOICES
                        from apps.authentication.models import LANGUAGE_CHOICES
                        lang_dict = dict(LANGUAGE_CHOICES)
                        native_lang_name = lang_dict.get(user.native_language, user.native_language)
                        profile.teaching_languages = [native_lang_name]
                
                # Add a default bio if not set
                if not profile.bio:
                    profile.bio = f"Hi! I'm {user.name or user.username}. I'm learning languages with Linguify!"
                
                profile.save()
                
                if created:
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f'Created profile for {user.username}'))
                else:
                    updated_count += 1
                    self.stdout.write(f'Updated profile for {user.username}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully processed {len(users)} users:\n'
                f'- Created {created_count} new profiles\n'
                f'- Updated {updated_count} existing profiles'
            )
        )