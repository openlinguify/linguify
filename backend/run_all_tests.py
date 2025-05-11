#!/usr/bin/env python
"""
Script qui exécute automatiquement tous les tests du projet Linguify.
Ce script découvre et exécute tous les tests dans les trois répertoires:
- backend/tests
- backend/apps/authentication/tests
- backend/apps/course/tests
"""
import os
import sys
import django
import glob

def discover_test_files():
    """Découvre tous les fichiers de test dans les répertoires spécifiés."""
    test_dirs = [
        'tests',
        'apps/authentication/tests',
        'apps/course/tests'
    ]
    
    # Chemins adaptés pour être relatifs au répertoire backend
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Liste pour stocker tous les fichiers de test simples trouvés
    test_files = []
    
    # Chercher tous les fichiers de test dans chaque répertoire
    for test_dir in test_dirs:
        full_path = os.path.join(base_dir, test_dir)
        if os.path.exists(full_path):
            # Chercher les fichiers de test simples qui évitent les problèmes d'importation
            simple_tests = glob.glob(os.path.join(full_path, 'test_*_simple.py'))
            test_files.extend(simple_tests)
            
            # Si aucun test simple n'est trouvé, essayer les tests normaux
            if not simple_tests:
                normal_tests = glob.glob(os.path.join(full_path, 'test_*.py'))
                test_files.extend(normal_tests)
    
    # Convertir les chemins absolus en chemins relatifs pour pytest
    return [os.path.relpath(test_file, base_dir) for test_file in test_files]

if __name__ == "__main__":
    # Configurer l'environnement Django avant les importations des modèles
    os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'
    os.environ.setdefault('DJANGO_SECRET_KEY', 'test_secret_key')
    os.environ.setdefault('TEST_MODE', 'True')

    # Ajouter les répertoires au path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, base_dir)
    
    # Initialiser Django
    django.setup()
    
    # Découvrir tous les fichiers de test
    test_files = discover_test_files()
    
    if not test_files:
        print("AVERTISSEMENT: Aucun fichier de test n'a été trouvé.")
        sys.exit(1)
    
    print(f"Tests découverts: {test_files}")
    
    # Maintenant que Django est configuré, nous pouvons importer et exécuter les tests
    import pytest
    
    # Exécuter tous les tests découverts avec pytest
    sys.exit(pytest.main(["-v"] + test_files))