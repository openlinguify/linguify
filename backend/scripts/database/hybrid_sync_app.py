#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de synchronisation hybride d'une application spécifique
Lit depuis développement (si disponible) ou production, et déploie vers production
Usage: python hybrid_sync_app.py nom_de_app
"""

import os
import sys
import django
import subprocess
from datetime import datetime

# Configuration Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')


def test_db_connection(env_mode):
    """Teste la connexion à la base de données"""
    env = os.environ.copy()
    env['DJANGO_ENV'] = env_mode
    
    try:
        # Test simple de connexion
        result = subprocess.run([
            sys.executable, '-c', 
            "import django; django.setup(); from django.db import connection; connection.cursor()"
        ], env=env, capture_output=True, text=True, timeout=5)
        
        return result.returncode == 0
    except:
        return False


def get_app_from_db(app_name, env_mode):
    """Récupère une application depuis la base de données"""
    env = os.environ.copy()
    env['DJANGO_ENV'] = env_mode
    
    try:
        result = subprocess.run([
            sys.executable, '-c', f"""
import django; django.setup()
from app_manager.models import App
try:
    app = App.objects.get(code='{app_name}')
    print(f'FOUND|{{app.id}}|{{app.display_name}}|{{app.code}}')
except App.DoesNotExist:
    try:
        app = App.objects.get(display_name__icontains='{app_name}')
        print(f'FOUND|{{app.id}}|{{app.display_name}}|{{app.code}}')
    except App.DoesNotExist:
        print('NOT_FOUND')
        apps = App.objects.all()
        for a in apps:
            print(f'AVAILABLE|{{a.display_name}}|{{a.code}}')
"""
        ], env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.startswith('FOUND|'):
                    _, app_id, display_name, code = line.split('|')
                    return {'id': app_id, 'display_name': display_name, 'code': code}
                elif line.startswith('AVAILABLE|'):
                    return None  # App not found, but we have available apps
            return None
        else:
            return None
    except Exception as e:
        print(f"❌ Erreur lors de la lecture: {e}")
        return None


def export_app(app_id, app_code, source_env):
    """Exporte une application depuis une base de données"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"app_{app_code}_{timestamp}.json"
    
    env = os.environ.copy()
    env['DJANGO_ENV'] = source_env
    
    try:
        result = subprocess.run([
            sys.executable, 'manage.py', 'dumpdata',
            'app_manager.App',
            '--pks', app_id,
            '--format=json',
            '--indent=2',
            '--output', filename
        ], env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"  ✅ App exportée vers {filename}")
            return filename
        else:
            print(f"  ❌ Erreur lors de l'export: {result.stderr}")
            return None
    except Exception as e:
        print(f"  ❌ Exception lors de l'export: {e}")
        return None


def deploy_to_production(filename):
    """Déploie un fichier vers la production"""
    env = os.environ.copy()
    env['DJANGO_ENV'] = 'production'
    
    print(f"  📤 Déploiement de {filename} vers la production...")
    
    # Confirmation de sécurité
    response = input("  ⚠️ ATTENTION: Déploiement vers PRODUCTION. Continuer? (oui/non): ")
    if response.lower() not in ['oui', 'yes', 'y']:
        print("  ❌ Déploiement annulé")
        return False
    
    try:
        result = subprocess.run([
            sys.executable, 'manage.py', 'loaddata', filename
        ], env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"  ✅ {filename} déployé avec succès vers la production")
            return True
        else:
            print(f"  ❌ Erreur lors du déploiement: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ❌ Exception lors du déploiement: {e}")
        return False


def main():
    if len(sys.argv) != 2:
        print("❌ Usage: python hybrid_sync_app.py <nom_de_app>")
        print("📝 Exemple: python hybrid_sync_app.py quizz")
        sys.exit(1)
        
    app_name = sys.argv[1]
    
    print(f"🚀 Synchronisation hybride de l'application: {app_name}")
    print("=" * 60)
    
    # Tester les connexions DB
    print("🔍 Test des connexions base de données...")
    dev_available = test_db_connection('development')
    prod_available = test_db_connection('production')
    
    print(f"  - Développement: {'✅ Disponible' if dev_available else '❌ Indisponible'}")
    print(f"  - Production: {'✅ Disponible' if prod_available else '❌ Indisponible'}")
    
    if not prod_available:
        print("❌ Impossible de continuer: Production inaccessible")
        sys.exit(1)
    
    # Chercher l'app (priorité au dev si disponible)
    app_data = None
    source_env = None
    
    if dev_available:
        print("📱 Recherche de l'application en développement...")
        app_data = get_app_from_db(app_name, 'development')
        source_env = 'development'
    
    if not app_data and prod_available:
        print("📱 Recherche de l'application en production...")
        app_data = get_app_from_db(app_name, 'production')
        source_env = 'production'
    
    if not app_data:
        print(f"❌ Application '{app_name}' non trouvée")
        print("📋 Applications disponibles:")
        
        # Lister depuis la source disponible
        env_to_list = 'development' if dev_available else 'production'
        get_app_from_db('__non_existent__', env_to_list)  # Pour déclencher la liste
        sys.exit(1)
    
    print(f"✅ Application trouvée: {app_data['display_name']} (code: {app_data['code']})")
    print(f"📍 Source: {source_env}")
    
    # Export
    print("📦 Export de l'application...")
    filename = export_app(app_data['id'], app_data['code'], source_env)
    
    if not filename:
        print("❌ Échec de l'export")
        sys.exit(1)
    
    # Déploiement vers production (seulement si source != production)
    if source_env != 'production':
        print("🚀 Déploiement vers production...")
        success = deploy_to_production(filename)
        
        if success:
            print(f"🎉 Application {app_data['display_name']} synchronisée avec succès!")
        else:
            print("❌ Échec du déploiement")
            sys.exit(1)
    else:
        print("ℹ️  L'application est déjà en production, aucun déploiement nécessaire")
    
    # Nettoyage
    try:
        os.remove(filename)
        print(f"🧹 Fichier temporaire supprimé: {filename}")
    except:
        pass


if __name__ == "__main__":
    main()