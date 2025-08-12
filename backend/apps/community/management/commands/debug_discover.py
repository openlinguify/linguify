from django.core.management.base import BaseCommand
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from apps.community.views import DiscoverUsersView
from apps.community.models import Profile

User = get_user_model()


class Command(BaseCommand):
    help = 'Debug the discover users view'

    def handle(self, *args, **options):
        self.stdout.write('=== Debugging DiscoverUsersView ===')
        
        # Create a fake request
        factory = RequestFactory()
        request = factory.get('/community/discover/')
        
        # Get a test user (first superuser or any user)
        try:
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                user = User.objects.first()
            if not user:
                self.stdout.write(self.style.ERROR('No users found in database'))
                return
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('No users found in database'))
            return
        request.user = user
        
        # Create the view
        view = DiscoverUsersView()
        view.request = request
        
        # Test the queryset
        self.stdout.write('Testing queryset...')
        queryset = view.get_queryset()
        self.stdout.write(f'Found {queryset.count()} users:')
        
        for user_obj in queryset:
            profile, created = Profile.objects.get_or_create(user=user_obj)
            self.stdout.write(f'  - {user_obj.username} ({user_obj.email})')
            self.stdout.write(f'    Native: {user_obj.native_language} -> Target: {user_obj.target_language}')
            self.stdout.write(f'    Profile exists: {not created}, Bio: {profile.bio[:30] if profile.bio else "None"}...')
        
        # Test the context
        self.stdout.write('\nTesting context...')
        context = view.get_context_data()
        
        self.stdout.write(f'Context keys: {list(context.keys())}')
        if 'users' in context:
            users = context['users']
            self.stdout.write(f'Users in context: {len(list(users)) if users else 0}')
        
        if 'language_choices' in context:
            self.stdout.write(f'Language choices available: {len(context["language_choices"])}')
        
        self.stdout.write('\n=== Debug complete ===')