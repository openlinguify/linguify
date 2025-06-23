from django.core.management.base import BaseCommand
from django.db import transaction
from apps.authentication.models import User
from apps.community.models import Profile
from app_manager.models import App, UserAppSettings


class Command(BaseCommand):
    help = 'Enable community and chat apps for all users by default'

    def handle(self, *args, **options):
        self.stdout.write('Enabling community and chat apps for all users...')
        
        # Get or create the Community and Chat apps
        community_app, created = App.objects.get_or_create(
            code='community',
            defaults={
                'display_name': 'Community',
                'description': 'Connect with other language learners',
                'icon_name': 'users',
                'color': '#3B82F6',
                'route_path': '/community',
                'category': 'social',
                'installable': True,
                'is_enabled': True,
                'manifest_data': {
                    'name': 'Community',
                    'description': 'Language learning community features',
                    'version': '1.0.0',
                    'features': ['friends', 'groups', 'messaging', 'language_exchange']
                }
            }
        )
        
        chat_app, created = App.objects.get_or_create(
            code='chat',
            defaults={
                'display_name': 'Chat',
                'description': 'Real-time messaging with language partners',
                'icon_name': 'message-circle',
                'color': '#10B981',
                'route_path': '/chat',
                'category': 'communication',
                'installable': True,
                'is_enabled': True,
                'manifest_data': {
                    'name': 'Chat',
                    'description': 'Real-time messaging and language exchange',
                    'version': '1.0.0',
                    'features': ['messaging', 'language_tools', 'translation']
                }
            }
        )
        
        users_updated = 0
        profiles_created = 0
        
        with transaction.atomic():
            for user in User.objects.filter(is_active=True):
                
                # Create community profile if doesn't exist
                profile, profile_created = Profile.objects.get_or_create(user=user)
                if profile_created:
                    profiles_created += 1
                    
                    # Set default learning/teaching languages from user settings
                    if user.target_language:
                        from apps.authentication.models import LANGUAGE_CHOICES
                        lang_dict = dict(LANGUAGE_CHOICES)
                        target_lang_name = lang_dict.get(user.target_language, user.target_language)
                        profile.learning_languages = [target_lang_name]
                    
                    if user.native_language:
                        from apps.authentication.models import LANGUAGE_CHOICES
                        lang_dict = dict(LANGUAGE_CHOICES)
                        native_lang_name = lang_dict.get(user.native_language, user.native_language)
                        profile.teaching_languages = [native_lang_name]
                    
                    if not profile.bio:
                        name = user.first_name or user.username
                        profile.bio = f"Hi! I'm {name}. I'm learning languages with Linguify and looking forward to connecting with other learners!"
                    
                    profile.save()
                
                # Enable Community and Chat apps for user
                user_settings, created = UserAppSettings.objects.get_or_create(user=user)
                
                # Add community app if not already enabled
                if not user_settings.enabled_apps.filter(code='community').exists():
                    user_settings.enabled_apps.add(community_app)
                    users_updated += 1
                
                # Add chat app if not already enabled
                if not user_settings.enabled_apps.filter(code='chat').exists():
                    user_settings.enabled_apps.add(chat_app)
                
                self.stdout.write(f'✓ Processed user: {user.username}')
        
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully enabled community features for all users:\n'
                f'- Created {profiles_created} new community profiles\n'
                f'- Updated {users_updated} users with community access\n'
                f'- Total active users: {User.objects.filter(is_active=True).count()}'
            )
        )
        
        # Set apps as installed by default for new users
        community_app.installable = True
        community_app.save()
        
        chat_app.installable = True
        chat_app.save()
        
        self.stdout.write(
            self.style.SUCCESS(
                '\n🎉 Community and Chat apps are now enabled by default for all users!'
            )
        )