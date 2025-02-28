# authentication/tests/conftest.py
"""
Configuration pour pytest.
Ce fichier sera automatiquement reconnu par pytest et 
appliqué à tous les tests utilisant pytest.
"""
import os
import sys
import pytest
from django.conf import settings

# Ajouter le chemin du projet pour permettre les importations
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .test_settings import SQLITE_MEMORY_DB

@pytest.fixture(scope='session')
def django_db_setup():
    """
    Configuration de la base de données de test pour pytest.
    Ce fixture sera utilisé automatiquement par les tests utilisant la base de données.
    """
    # Utiliser SQLite en mémoire pour les tests
    settings.DATABASES = SQLITE_MEMORY_DB
    
    # Assurez-vous que les migrations sont appliquées
    from django.core.management import call_command
    call_command('migrate')

# Vous pouvez ajouter d'autres fixtures utiles pour vos tests
@pytest.fixture
def create_user(db):
    """Fixture pour créer un utilisateur de test"""
    from authentication.models import User
    
    def _create_user(username='testuser', email='test@example.com', password='password123', **kwargs):
        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
            **kwargs
        )
    
    return _create_user

@pytest.fixture
def create_coach(db, create_user):
    """Fixture pour créer un coach de test"""
    from authentication.models import CoachProfile
    from decimal import Decimal
    
    def _create_coach(user=None, **kwargs):
        if user is None:
            user = create_user(username='coachuser', email='coach@example.com', is_coach=True)
        
        coach_data = {
            'coaching_languages': 'EN',
            'price_per_hour': Decimal('50.00'),
            'availability': 'Monday to Friday, 9am to 5pm',
            'description': 'Experienced language coach',
        }
        coach_data.update(kwargs)
        
        return CoachProfile.objects.create(user=user, **coach_data)
    
    return _create_coach

@pytest.fixture
def api_client():
    """Fixture pour créer un client API de test"""
    from rest_framework.test import APIClient
    return APIClient()

@pytest.fixture
def authenticated_client(create_user, api_client):
    """Fixture pour créer un client API authentifié"""
    def _get_authenticated_client(user=None):
        if user is None:
            user = create_user()
        
        api_client.force_authenticate(user=user)
        return api_client
    
    return _get_authenticated_client