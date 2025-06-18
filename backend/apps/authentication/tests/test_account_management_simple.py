"""
Tests simplifiés pour les fonctionnalités de gestion de compte dans l'application authentication.
Version sans conflit d'importation.
"""
import pytest
import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError


@pytest.mark.django_db
class TestAuthenticationBasics:
    """Tests simples pour vérifier la configuration de pytest avec Django."""
    
    def test_user_model_access(self):
        """Test simple pour vérifier l'accès au modèle User."""
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
    
    def test_user_profile_update(self):
        """Test de la mise à jour du profil utilisateur."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Créer un utilisateur de test
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            first_name='Original',
            last_name='Name'
        )
        
        # Mettre à jour le profil
        user.first_name = 'Updated'
        user.last_name = 'Profile'
        user.save()
        
        # Vérifier que les modifications ont été enregistrées
        user.refresh_from_db()
        assert user.first_name == 'Updated'
        assert user.last_name == 'Profile'
        
        # Nettoyer la BD
        user.delete()