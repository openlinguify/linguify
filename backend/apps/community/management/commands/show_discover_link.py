from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Show the correct links to access community features'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Liens d\'accès à la communauté ==='))
        self.stdout.write('')
        self.stdout.write('🌐 Page principale de la communauté:')
        self.stdout.write('   http://127.0.0.1:8000/community/')
        self.stdout.write('')
        self.stdout.write('🔍 Page de découverte d\'utilisateurs:')
        self.stdout.write('   http://127.0.0.1:8000/community/discover/')
        self.stdout.write('')
        self.stdout.write('👥 Page des amis:')
        self.stdout.write('   http://127.0.0.1:8000/community/friends/')
        self.stdout.write('')
        self.stdout.write('💬 Page des messages:')
        self.stdout.write('   http://127.0.0.1:8000/community/messages/')
        self.stdout.write('')
        self.stdout.write('📚 Page des groupes d\'étude:')
        self.stdout.write('   http://127.0.0.1:8000/community/groups/')
        self.stdout.write('')
        self.stdout.write('📈 Feed d\'activités:')
        self.stdout.write('   http://127.0.0.1:8000/community/feed/')
        self.stdout.write('')
        
        self.stdout.write(self.style.WARNING('📝 Pour accéder aux pages:'))
        self.stdout.write('1. Démarrez le serveur: python manage.py runserver')
        self.stdout.write('2. Connectez-vous avec un compte utilisateur')
        self.stdout.write('3. Naviguez vers les liens ci-dessus')
        self.stdout.write('')
        
        self.stdout.write('👤 Comptes de test disponibles:')
        users = User.objects.all()[:8]
        for user in users:
            self.stdout.write(f'   - {user.username} (email: {user.email})')
        self.stdout.write('   Mot de passe: password123 (pour les nouveaux comptes)')
        self.stdout.write('')
        
        self.stdout.write(self.style.SUCCESS('🎯 URL de connexion:'))
        self.stdout.write('   http://127.0.0.1:8000/auth/login/')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('🏠 Dashboard principal:'))
        self.stdout.write('   http://127.0.0.1:8000/dashboard/')
        
        # Count users for discover
        current_user = users.first()
        if current_user:
            from apps.community.models import Profile
            profile, _ = Profile.objects.get_or_create(user=current_user)
            excluded_users = [current_user.id] + list(profile.friends.values_list('user_id', flat=True))
            discoverable_count = User.objects.exclude(id__in=excluded_users).filter(is_active=True).count()
            self.stdout.write('')
            self.stdout.write(f'📊 Utilisateurs découvrables: {discoverable_count} (pour {current_user.username})')