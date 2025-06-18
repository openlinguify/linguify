"""
Fichier de configuration pytest pour les tests du module Authentication.
Ce fichier définit les fixtures partagées par les différents tests.
"""
import pytest
import datetime
from decimal import Decimal
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def create_user():
    """
    Fixture pour créer un utilisateur de test.
    
    Retourne une fonction factory qui peut être utilisée pour créer des utilisateurs
    avec des attributs personnalisés.
    """
    def _create_user(**kwargs):
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'first_name': 'Test',
            'last_name': 'User',
            'native_language': 'EN',
            'target_language': 'FR',
            'language_level': 'A2',
            'objectives': 'Travel',
            'terms_accepted': False,
            'terms_version': 'v1.0'
        }
        user_data.update(kwargs)
        
        return User.objects.create_user(**user_data)
    
    return _create_user


@pytest.fixture
def create_coach():
    """
    Fixture pour créer un profil de coach de test.
    
    Retourne une fonction factory qui peut être utilisée pour créer des profils de coach
    avec des attributs personnalisés.
    """
    def _create_coach(**kwargs):
        from ..models import CoachProfile
        
        # Créer l'utilisateur coach si non fourni
        if 'user' not in kwargs:
            user = User.objects.create_user(
                username='coachuser',
                email='coach@example.com',
                password='password123',
                is_coach=True
            )
            kwargs['user'] = user
        
        coach_data = {
            'coaching_languages': 'EN',
            'price_per_hour': Decimal('50.00'),
            'availability': 'Monday to Friday, 9am to 5pm',
            'description': 'Experienced language coach',
            'commission_rate': Decimal('5.00')
        }
        coach_data.update(kwargs)
        
        return CoachProfile.objects.create(**coach_data)
    
    return _create_coach