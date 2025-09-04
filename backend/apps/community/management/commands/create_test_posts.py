from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.community.models import Profile, Post
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Create test posts for the community feed'

    def handle(self, *args, **options):
        self.stdout.write('Creating test posts...')
        
        # Get test users
        test_users = User.objects.filter(username__in=[
            'marie_fr', 'carlos_es', 'anna_de', 'takeshi_jp', 'elena_it'
        ])
        
        if not test_users.exists():
            self.stdout.write(self.style.ERROR('No test users found. Run create_test_users first.'))
            return
        
        test_posts = [
            {
                'content': 'Just completed my first conversation in French! Feeling so proud of my progress 🎉 #FrenchLearning',
                'language': 'FR',
                'hours_ago': 2,
            },
            {
                'content': 'Had an amazing language exchange session today. Thank you to all the patient native speakers! 🙏',
                'language': 'EN',
                'hours_ago': 4,
            },
            {
                'content': 'Discovered a new grammar rule today that finally makes sense. Learning Chinese is challenging but rewarding! 📚',
                'language': 'ZH',
                'hours_ago': 24,
            },
            {
                'content': 'Perfected my Italian pronunciation today. Practice makes perfect! 🗣️',
                'language': 'IT',
                'hours_ago': 48,
            },
            {
                'content': 'Spanish conjugations are getting easier every day. Consistency is key! 💪',
                'language': 'ES',
                'hours_ago': 72,
            },
            {
                'content': 'Started reading a French novel today. It\'s challenging but I understand more than I expected! 📖',
                'language': 'FR',
                'hours_ago': 6,
            },
            {
                'content': 'Anyone else struggle with German articles? Der, die, das... sometimes I feel like I\'ll never get it right! 😅',
                'language': 'DE',
                'hours_ago': 12,
            },
            {
                'content': 'Watched a Spanish movie without subtitles for the first time. I understood about 70%! Small victories 🎬',
                'language': 'ES',
                'hours_ago': 18,
            }
        ]
        
        created_count = 0
        users_list = list(test_users)
        
        for i, post_data in enumerate(test_posts):
            # Assign post to a user (cycle through users)
            author = users_list[i % len(users_list)]
            
            # Create timestamp
            created_at = timezone.now() - timedelta(hours=post_data['hours_ago'])
            
            # Check if post already exists (avoid duplicates)
            if not Post.objects.filter(
                author=author,
                content=post_data['content']
            ).exists():
                post = Post.objects.create(
                    author=author,
                    content=post_data['content'],
                    created_at=created_at,
                    updated_at=created_at,
                )
                
                # Add some random likes
                likes_count = random.randint(5, 30)
                potential_likers = User.objects.exclude(id=author.id)[:likes_count]
                post.likes.set(potential_likers)
                created_count += 1
                self.stdout.write(f'Created post by {author.username}: "{post_data["content"][:50]}..."')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted! Created {created_count} new posts.'
                f'\nTotal posts: {Post.objects.count()}'
            )
        )