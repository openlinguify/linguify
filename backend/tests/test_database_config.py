"""
Test spécifique pour vérifier la configuration de la base de données.
"""
import os
import pytest
from django.conf import settings

@pytest.mark.django_db
def test_database_config():
    """Vérifie que la configuration de la base de données est correcte."""
    # Vérifier que la configuration de la base de données est bien définie
    assert 'default' in settings.DATABASES
    
    # Vérifier le moteur de base de données
    db_config = settings.DATABASES['default']
    engine = db_config.get('ENGINE', '')
    
    # Afficher la configuration complète pour le débogage
    print(f"Database engine: {engine}")
    print(f"Database config: {db_config}")
    
    # En mode test, nous devrions utiliser SQLite
    if os.environ.get('TEST_MODE') == 'True':
        assert 'sqlite3' in engine
    # Sinon, nous devrions utiliser PostgreSQL
    else:
        assert 'postgresql' in engine
        # Vérifier que nous utilisons l'utilisateur "postgres" et non "root"
        assert db_config.get('USER') == 'postgres'