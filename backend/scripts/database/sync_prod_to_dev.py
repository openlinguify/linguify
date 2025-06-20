"""
Script tout-en-un pour synchroniser la production vers le développement
Automatise export + import en gérant les changements d'environnement
"""
import os
import sys
import subprocess
import json

# Forcer UTF-8
sys.stdout.reconfigure(encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

print("🔄 Synchronisation Production → Développement")
print("=" * 60)

def run_script(script_path, env_mode):
    """Exécute un script avec l'environnement spécifié"""
    env = os.environ.copy()
    env['DJANGO_ENV'] = env_mode
    
    # Déterminer le répertoire backend (parent du dossier scripts)
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    result = subprocess.run([
        sys.executable, script_path
    ], env=env, capture_output=True, text=True, cwd=backend_dir)
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    return result.returncode == 0

try:
    # Étape 1: Export depuis la production
    print("\n📥 ÉTAPE 1: Export depuis Supabase (Production)")
    print("-" * 50)
    
    export_script = os.path.join(os.path.dirname(__file__), 'export_production_data.py')
    if not run_script(export_script, 'production'):
        print("❌ Échec de l'export")
        sys.exit(1)
    
    # Vérifier que le fichier d'export existe
    if not os.path.exists('production_export.json'):
        print("❌ Fichier d'export non trouvé")
        sys.exit(1)
    
    # Étape 2: Import en développement
    print("\n📤 ÉTAPE 2: Import en Développement (Local)")
    print("-" * 50)
    
    import_script = os.path.join(os.path.dirname(__file__), 'import_to_development.py')
    if not run_script(import_script, 'development'):
        print("❌ Échec de l'import")
        sys.exit(1)
    
    print("\n✅ SYNCHRONISATION TERMINÉE AVEC SUCCÈS!")
    print("=" * 60)
    
    print("\n🎯 Votre base de développement est maintenant synchronisée!")
    print("\n📋 Actions recommandées:")
    print("1. Vérifiez que DJANGO_ENV='development' dans .env")
    print("2. Créez votre superuser si nécessaire:")
    print("   python manage.py createsuperuser")
    print("3. Lancez le serveur:")
    print("   python manage.py runserver")
    print("4. Accédez à l'admin: http://localhost:8000/admin/")
    
    print("\n💡 Pour accéder aux CVs de production:")
    print("   Changez temporairement DJANGO_ENV='production' dans .env")
    
except KeyboardInterrupt:
    print("\n⚠️  Synchronisation interrompue par l'utilisateur")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Erreur inattendue: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)