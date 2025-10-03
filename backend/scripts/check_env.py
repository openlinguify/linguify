# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

"""
Script pour vérifier l'environnement de développement Linguify
"""

import os
import sys
from pathlib import Path

def check_environment():
    """Affiche les informations sur l'environnement actuel"""
    
    # Déterminer l'environnement à partir de DJANGO_ENV ou DEBUG
    django_env = os.getenv('DJANGO_ENV', 'development')
    debug = os.getenv('DEBUG', 'True').lower() in ('true', '1', 'yes')
    
    # Informations sur la base de données
    db_engine = os.getenv('DATABASE_ENGINE', 'postgresql')
    db_host = os.getenv('DATABASE_HOST', 'localhost')
    db_port = os.getenv('DATABASE_PORT', '5432')
    db_name = os.getenv('DATABASE_NAME', os.getenv('DEV_DB_NAME', 'db_linguify_dev'))
    
    # URL du backend
    backend_url = os.getenv('BACKEND_URL', 'http://localhost:8081')
    
    print(f"📊 DJANGO_ENV: {django_env}")
    print(f"🐛 DEBUG: {debug}")
    print(f"🌐 BACKEND_URL: {backend_url}")
    print(f"💾 Database: {db_engine} @ {db_host}:{db_port}/{db_name}")
    
    # Vérifier les variables critiques
    secret_key = os.getenv('SECRET_KEY')
    if not secret_key:
        print("⚠️  WARNING: SECRET_KEY non définie!")
        return False
    else:
        print(f"🔐 SECRET_KEY: {'*' * 8}... (définie)")
    
    # Vérifier les fichiers critiques
    env_file = Path('.env')
    if env_file.exists():
        print(f"✅ Fichier .env: trouvé")
    else:
        print(f"❌ Fichier .env: manquant")
        return False
    
    # Vérifier la configuration Poetry
    poetry_lock = Path('poetry.lock')
    if poetry_lock.exists():
        print(f"✅ Poetry: configuré")
    else:
        print(f"⚠️  Poetry: poetry.lock manquant")
    
    return True

if __name__ == '__main__':
    # Charger les variables d'environnement depuis .env
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key, value.strip('"\''))
    
    success = check_environment()
    sys.exit(0 if success else 1)