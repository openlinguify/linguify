from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.community.models import Profile
from app_manager.models import UserAppSettings

User = get_user_model()


class Command(BaseCommand):
    help = 'Test automatic enabling of community apps for new users'

    def handle(self, *args, **options):
        self.stdout.write('Testing automatic app enablement for new users...')
        
        # Create a test user
        test_username = 'test_auto_user'
        
        # Delete if exists
        User.objects.filter(username=test_username).delete()
        
        # Create new user
        user = User.objects.create_user(
            username=test_username,
            email='test_auto@example.com',
            password='password123',
            first_name='Test',
            last_name='User',
            native_language='EN',
            target_language='FR',
            is_active=True
        )
        
        self.stdout.write(f'✓ Created user: {user.username}')
        
        # Check if community profile was created
        try:
            profile = Profile.objects.get(user=user)
            self.stdout.write(f'✓ Community profile created')
            self.stdout.write(f'  Bio: {profile.bio}')
            self.stdout.write(f'  Teaching: {profile.teaching_languages}')
            self.stdout.write(f'  Learning: {profile.learning_languages}')
        except Profile.DoesNotExist:
            self.stdout.write(self.style.ERROR('✗ Community profile NOT created'))
        
        # Check if apps were enabled
        try:
            user_settings = UserAppSettings.objects.get(user=user)
            enabled_apps = user_settings.get_enabled_app_codes()
            self.stdout.write(f'✓ User app settings created')
            self.stdout.write(f'  Enabled apps: {enabled_apps}')
            
            if 'community' in enabled_apps:
                self.stdout.write('✓ Community app enabled')
            else:
                self.stdout.write(self.style.ERROR('✗ Community app NOT enabled'))
                
            if 'chat' in enabled_apps:
                self.stdout.write('✓ Chat app enabled')
            else:
                self.stdout.write(self.style.ERROR('✗ Chat app NOT enabled'))
                
        except UserAppSettings.DoesNotExist:
            self.stdout.write(self.style.ERROR('✗ User app settings NOT created'))
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('🎉 Test completed! New users should now automatically have community features enabled.'))
        
        # Clean up
        user.delete()
        self.stdout.write('Cleaned up test user.')