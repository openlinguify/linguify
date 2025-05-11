#!/usr/bin/env python
"""
Script pour exécuter les tests
Ce script configure correctement l'environnement avant d'exécuter pytest.
"""
import os
import sys
import django
from django.conf import settings

# Configurer l'environnement Django avant les importations des modèles
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'
# Définir les variables d'environnement pour les tests
os.environ.setdefault('DJANGO_SECRET_KEY', 'test_secret_key')
os.environ.setdefault('DB_NAME', 'test_db_linguify')
os.environ.setdefault('DB_USER', 'postgres')
os.environ.setdefault('DB_PASSWORD', 'postgres')
os.environ.setdefault('DB_HOST', 'localhost')
os.environ.setdefault('DB_PORT', '5432')
os.environ.setdefault('AUTH0_DOMAIN', 'test.auth0.com')
os.environ.setdefault('AUTH0_CLIENT_ID', 'test_client_id')
os.environ.setdefault('AUTH0_CLIENT_SECRET', 'test_client_secret')
os.environ.setdefault('AUTH0_AUDIENCE', 'https://test-api')


def main():
    """
    Fonction principale qui exécute les tests.
    """
    import pytest

    # Initialiser Django
    django.setup()

    # Spécifier les tests à exécuter
    test_paths = [
        "apps/authentication/tests/test_account_management.py",
        "apps/course/tests/test_exercises.py"
    ]

    # Exécuter les tests avec pytest
    sys.exit(pytest.main(["-v"] + test_paths))


if __name__ == "__main__":
    main()