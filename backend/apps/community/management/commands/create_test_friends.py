from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.community.models import Profile, FriendRequest
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Create test friend relationships and requests'

    def handle(self, *args, **options):
        self.stdout.write('Creating test friend relationships...')
        
        # Get test users
        test_users = User.objects.filter(username__in=[
            'marie_fr', 'carlos_es', 'anna_de', 'takeshi_jp', 'elena_it'
        ])
        
        if not test_users.exists():
            self.stdout.write(self.style.ERROR('No test users found. Run create_test_users first.'))
            return
        
        # Get current user (admin) if exists
        current_user = None
        try:
            current_user = User.objects.get(username='admin')
        except User.DoesNotExist:
            # Try to get any superuser
            current_user = User.objects.filter(is_superuser=True).first()
        
        users_list = list(test_users)
        friends_created = 0
        requests_created = 0
        
        # Create some friendships between test users
        for i in range(len(users_list)):
            for j in range(i + 1, min(i + 3, len(users_list))):  # Each user becomes friends with 1-2 others
                user1 = users_list[i]
                user2 = users_list[j]
                
                profile1, _ = Profile.objects.get_or_create(user=user1)
                profile2, _ = Profile.objects.get_or_create(user=user2)
                
                # Add as friends (bidirectional)
                if not profile1.friends.filter(user=user2).exists():
                    profile1.friends.add(profile2)
                    profile2.friends.add(profile1)
                    friends_created += 1
                    self.stdout.write(f'Created friendship: {user1.username} <-> {user2.username}')
        
        # Create some friend requests for the current user if exists
        if current_user:
            current_profile, _ = Profile.objects.get_or_create(user=current_user)
            
            # Create some incoming friend requests
            for user in users_list[:3]:  # First 3 users send requests to current user
                if not FriendRequest.objects.filter(
                    sender=user, 
                    receiver=current_user
                ).exists() and not current_profile.friends.filter(user=user).exists():
                    FriendRequest.objects.create(
                        sender=user,
                        receiver=current_user,
                        status='pending'
                    )
                    requests_created += 1
                    self.stdout.write(f'Created friend request: {user.username} -> {current_user.username}')
            
            # Current user sends requests to last 2 users
            for user in users_list[-2:]:
                if not FriendRequest.objects.filter(
                    sender=current_user, 
                    receiver=user
                ).exists() and not current_profile.friends.filter(user=user).exists():
                    FriendRequest.objects.create(
                        sender=current_user,
                        receiver=user,
                        status='pending'
                    )
                    requests_created += 1
                    self.stdout.write(f'Created friend request: {current_user.username} -> {user.username}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted!'
                f'\nFriendships created: {friends_created}'
                f'\nFriend requests created: {requests_created}'
            )
        )