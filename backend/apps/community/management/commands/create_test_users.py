from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.community.models import Profile

User = get_user_model()


class Command(BaseCommand):
    help = 'Create test users with diverse language profiles'

    def handle(self, *args, **options):
        self.stdout.write('Creating test users...')
        
        test_users = [
            {
                'username': 'marie_fr',
                'email': 'marie@example.com',
                'name': 'Marie Dubois',
                'native_language': 'FR',
                'target_language': 'EN',
                'bio': 'Bonjour! I\'m a French native speaker from Paris. I love helping people learn French while I practice my English!',
                'teaching_languages': ['French', 'Spanish'],
                'learning_languages': ['English'],
            },
            {
                'username': 'carlos_es',
                'email': 'carlos@example.com', 
                'name': 'Carlos Martinez',
                'native_language': 'ES',
                'target_language': 'EN',
                'bio': '¡Hola! Spanish teacher from Madrid. I enjoy language exchange and helping others with Spanish pronunciation.',
                'teaching_languages': ['Spanish'],
                'learning_languages': ['English', 'French'],
            },
            {
                'username': 'anna_de',
                'email': 'anna@example.com',
                'name': 'Anna Mueller',
                'native_language': 'DE', 
                'target_language': 'FR',
                'bio': 'Hallo! German native from Berlin. I\'m passionate about French culture and looking for conversation partners.',
                'teaching_languages': ['German', 'English'],
                'learning_languages': ['French'],
            },
            {
                'username': 'takeshi_jp',
                'email': 'takeshi@example.com',
                'name': 'Takeshi Yamamoto', 
                'native_language': 'EN',  # En tant que bilingue
                'target_language': 'FR',
                'bio': 'Hello! I\'m bilingual English-Japanese and learning French. I can help with English conversation!',
                'teaching_languages': ['English', 'Japanese'],
                'learning_languages': ['French', 'Spanish'],
            },
            {
                'username': 'elena_it',
                'email': 'elena@example.com',
                'name': 'Elena Rossi',
                'native_language': 'IT',
                'target_language': 'EN', 
                'bio': 'Ciao! Italian from Rome, teacher by profession. Love sharing Italian culture and learning English slang!',
                'teaching_languages': ['Italian'],
                'learning_languages': ['English', 'French'],
            }
        ]
        
        created_count = 0
        for user_data in test_users:
            # Create user if doesn't exist
            name_parts = user_data['name'].split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            # Check if user exists
            if User.objects.filter(username=user_data['username']).exists():
                user = User.objects.get(username=user_data['username'])
                created = False
            else:
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password='password123',
                    first_name=first_name,
                    last_name=last_name,
                    native_language=user_data['native_language'],
                    target_language=user_data['target_language'],
                    is_active=True,
                )
                created = True
                created_count += 1
                self.stdout.write(f'Created user: {user.username}')
            
            # Create/update profile
            profile, profile_created = Profile.objects.get_or_create(user=user)
            profile.bio = user_data['bio']
            profile.teaching_languages = user_data['teaching_languages']
            profile.learning_languages = user_data['learning_languages']
            profile.save()
            
            if profile_created:
                self.stdout.write(f'Created profile for: {user.username}')
            else:
                self.stdout.write(f'Updated profile for: {user.username}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted! Created {created_count} new users.'
                f'\nTotal users with profiles: {User.objects.count()}'
            )
        )