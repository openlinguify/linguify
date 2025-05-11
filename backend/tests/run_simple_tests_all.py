#!/usr/bin/env python
"""
Script pour exécuter toutes les versions simplifiées des tests unitaires.
Cette version évite les problèmes d'importation.
"""
import os
import sys
import django

if __name__ == "__main__":
    # Configurer l'environnement Django avant les importations des modèles
    os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'
    os.environ.setdefault('DJANGO_SECRET_KEY', 'test_secret_key')
    
    # Ajouter les répertoires au path
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    # Initialiser Django
    django.setup()
    
    # Maintenant que Django est configuré, nous pouvons importer et exécuter les tests
    import pytest
    
    # Exécuter les tests simplifiés
    test_paths = [
        "apps/authentication/tests/test_account_management_simple.py",
        "apps/course/tests/test_exercises_simple.py",
    ]
    
    # Exécuter les tests avec pytest et sortir avec le code de retour approprié
    sys.exit(pytest.main(["-v"] + test_paths))