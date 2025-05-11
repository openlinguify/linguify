"""
Tests simplifiés pour le module Course.
Version sans conflit d'importation.
"""
import pytest
from django.utils import timezone
from django.core.exceptions import ValidationError


@pytest.mark.django_db
class TestCourseBasics:
    """Tests simples pour vérifier la configuration de pytest avec Django."""
    
    def test_django_db_setup(self):
        """Test simple pour vérifier que la connexion à la base de données fonctionne."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Créer un utilisateur de test
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User'
        )
        
        # Vérifier que l'utilisateur a bien été créé
        assert user.id is not None
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        
        # Supprimer l'utilisateur
        user.delete()
        assert User.objects.filter(username='testuser').count() == 0
        
    def test_timezone_awareness(self):
        """Test pour vérifier que les dates sont bien gérées avec le timezone."""
        now = timezone.now()
        assert now.tzinfo is not None
        
        # Vérifier que la date est bien dans le futur
        future = now + timezone.timedelta(days=30)
        assert future > now
        
        # Vérifier que la différence est bien de 30 jours
        diff = future - now
        assert diff.days == 30