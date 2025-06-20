"""
Nettoie complètement la base de développement
Usage: DJANGO_ENV="development" puis lancer ce script
"""
import os
import sys
import subprocess

# Forcer UTF-8
sys.stdout.reconfigure(encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from django.core.management import call_command
from django.db import connection

print("🧹 Nettoyage complet de la base de développement")
print("=" * 60)

# Vérifier qu'on est en développement
print(f"🔗 Connecté à: {connection.settings_dict['HOST']}")

if 'localhost' not in connection.settings_dict['HOST']:
    print("❌ ERREUR: Pas en mode développement!")
    print("   Changez DJANGO_ENV='development' dans .env")
    sys.exit(1)

try:
    print("\n⚠️  ATTENTION: Cette action va supprimer TOUTES les données locales!")
    confirm = input("Continuer? (tapez 'OUI' pour confirmer): ")
    
    if confirm != 'OUI':
        print("❌ Opération annulée")
        sys.exit(0)
    
    print("\n🗑️  Suppression complète de la base...")
    
    db_name = connection.settings_dict['NAME']
    db_user = connection.settings_dict['USER'] 
    db_password = connection.settings_dict['PASSWORD']
    
    # Fermer la connexion Django
    connection.close()
    
    # Commandes PostgreSQL
    postgres_conn = f"postgresql://{db_user}:{db_password}@localhost:5432/postgres"
    
    print("   Suppression de la base...")
    result = subprocess.run([
        "psql", postgres_conn, "-c", f"DROP DATABASE IF EXISTS {db_name};"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Erreur lors de la suppression: {result.stderr}")
        sys.exit(1)
    
    print("   Recréation de la base...")
    result = subprocess.run([
        "psql", postgres_conn, "-c", f"CREATE DATABASE {db_name} WITH ENCODING 'UTF8';"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Erreur lors de la création: {result.stderr}")
        sys.exit(1)
    
    print("   ✅ Base recréée")
    
    # Recharger Django
    django.setup()
    
    print("\n🔧 Application des migrations...")
    call_command('migrate', verbosity=0)
    
    print("\n✅ Nettoyage terminé!")
    print("\n🎯 La base de développement est maintenant vide et prête.")
    print("\n📋 Prochaines étapes:")
    print("1. Synchroniser avec la production:")
    print("   python scripts/database/sync_prod_to_dev.py")
    print("2. Ou créer des données de test:")
    print("   python manage.py createsuperuser")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()