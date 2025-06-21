#!/usr/bin/env python3
"""
Script de synchronisation granulaire des tables
Synchronise des tables spécifiques de dev vers production
Usage: python sync_table.py <app> <table> <target>
Exemples:
  python sync_table.py blog blogpost_tags prod
  python sync_table.py course lesson dev
"""

import os
import sys
import django
import json

# Configuration du chemin Python
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, backend_dir)

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings
from django.core.management import execute_from_command_line
from django.db import connection
from django.apps import apps

def get_table_name(app_name, model_name):
    """Obtient le nom de table réel pour un modèle Django"""
    try:
        app_config = apps.get_app_config(app_name)
        model = app_config.get_model(model_name)
        return model._meta.db_table
    except:
        # Si ce n'est pas un modèle Django, assume que c'est un nom de table direct
        return f"{app_name}_{model_name}"

def sync_table_to_production(app_name, table_name, target_env):
    """Synchronise une table spécifique vers la production"""
    
    print(f"🔄 Synchronisation de {app_name}.{table_name} vers {target_env}")
    
    # Obtenir le nom de table réel
    real_table_name = get_table_name(app_name, table_name)
    print(f"📋 Table: {real_table_name}")
    
    # Configuration des environnements
    if target_env.lower() in ['prod', 'production']:
        env_config = 'production'
        print("🚀 Cible: Production (Supabase)")
    else:
        env_config = 'development'
        print("🏗️  Cible: Développement (PostgreSQL local)")
    
    # Charger la configuration de développement pour exporter
    os.environ['DJANGO_ENV'] = 'development'
    
    try:
        # Vérifier que la table existe
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                );
            """, [real_table_name])
            
            if not cursor.fetchone()[0]:
                print(f"❌ Table {real_table_name} non trouvée en développement")
                return False
        
        # Compter les données en développement
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM {real_table_name}")
            dev_count = cursor.fetchone()[0]
            print(f"📊 Données en développement: {dev_count} lignes")
        
        if dev_count == 0:
            print("⚠️  Aucune donnée à synchroniser")
            return True
        
        # Exporter les données en format JSON
        print("📤 Export des données...")
        
        # Utiliser dumpdata pour exporter la table spécifique
        # Convertir le nom de table en nom de modèle Django
        model_name = table_name.title()  # category -> Category
        dump_command = [
            'manage.py', 'dumpdata', 
            f'{app_name}.{model_name}',
            '--format=json',
            '--indent=2'
        ]
        
        # Rediriger vers un fichier temporaire
        import subprocess
        result = subprocess.run(
            ['poetry', 'run', 'python'] + dump_command,
            capture_output=True,
            text=True,
            cwd='/mnt/c/Users/louis/WebstormProjects/linguify/backend'
        )
        
        if result.returncode != 0:
            print(f"❌ Erreur lors de l'export: {result.stderr}")
            return False
        
        export_data = result.stdout
        print(f"📦 Données exportées: {len(export_data)} caractères")
        
        if not export_data or export_data.strip() == "[]":
            print("⚠️  Aucune donnée exportée")
            return True
        
        # Maintenant basculer vers la production pour importer
        print(f"🔄 Basculement vers {env_config}...")
        os.environ['DJANGO_ENV'] = env_config
        
        # Recharger Django avec la nouvelle configuration
        from django.core.management.utils import get_random_secret_key
        import importlib
        import core.settings
        importlib.reload(core.settings)
        
        # Vérifier la connexion de production
        from django.db import connection as prod_connection
        try:
            with prod_connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                print(f"✅ Connexion {env_config} établie")
        except Exception as e:
            print(f"❌ Erreur de connexion {env_config}: {e}")
            return False
        
        # Sauvegarder temporairement les données
        temp_file = f"/tmp/sync_table_{app_name}_{table_name}.json"
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(export_data)
        
        print(f"💾 Données sauvegardées dans {temp_file}")
        
        # Vérifier le contenu du fichier
        if os.path.getsize(temp_file) == 0:
            print("❌ Fichier temporaire vide")
            os.unlink(temp_file)
            return False
        
        # Importer les données en production
        print("📥 Import vers la production...")
        
        import_command = [
            'manage.py', 'loaddata', temp_file
        ]
        
        result = subprocess.run(
            ['poetry', 'run', 'python'] + import_command,
            capture_output=True,
            text=True,
            cwd='/mnt/c/Users/louis/WebstormProjects/linguify/backend',
            env=dict(os.environ, DJANGO_ENV=env_config)
        )
        
        if result.returncode != 0:
            print(f"❌ Erreur lors de l'import: {result.stderr}")
            # Nettoyer le fichier temporaire
            os.unlink(temp_file)
            return False
        
        print("✅ Import réussi")
        
        # Vérifier les données en production
        with prod_connection.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM {real_table_name}")
            prod_count = cursor.fetchone()[0]
            print(f"📊 Données en production: {prod_count} lignes")
        
        # Nettoyer le fichier temporaire
        os.unlink(temp_file)
        
        print(f"✅ Synchronisation terminée: {dev_count} → {prod_count}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    if len(sys.argv) != 4:
        print("❌ Usage: python sync_table.py <app> <table> <target>")
        print("📝 Exemples:")
        print("  python sync_table.py blog blogpost prod")
        print("  python sync_table.py course lesson prod")
        print("  python sync_table.py blog category prod")
        sys.exit(1)
    
    app_name = sys.argv[1]
    table_name = sys.argv[2]
    target_env = sys.argv[3]
    
    print(f"🎯 Synchronisation {app_name}.{table_name} → {target_env}")
    
    success = sync_table_to_production(app_name, table_name, target_env)
    
    if success:
        print("✅ Synchronisation réussie")
        sys.exit(0)
    else:
        print("❌ Synchronisation échouée")
        sys.exit(1)

if __name__ == "__main__":
    main()