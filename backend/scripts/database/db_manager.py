#!/usr/bin/env python3
"""
Gestionnaire de base de données Linguify - Interface simplifiée
Usage: python scripts/database/db_manager.py [action]
"""
import os
import sys
import subprocess

def print_header():
    print("🗄️  Gestionnaire de Base de Données Linguify")
    print("=" * 60)

def print_menu():
    print("\n📋 Actions disponibles:")
    print("1. sync     - Synchroniser production → développement")
    print("2. export   - Exporter depuis production uniquement")
    print("3. import   - Importer en développement uniquement")
    print("4. clean    - Nettoyer la base de développement")
    print("5. setup    - Configurer PostgreSQL local")
    print("6. status   - Vérifier l'état des bases")
    print("0. help     - Afficher cette aide")

def run_script(script_name):
    """Exécute un script dans le dossier database"""
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    if not os.path.exists(script_path):
        print(f"❌ Script {script_name} introuvable!")
        return False
    
    result = subprocess.run([sys.executable, script_path])
    return result.returncode == 0

def show_status():
    """Affiche l'état actuel des bases"""
    print("\n📊 État des bases de données:")
    print("-" * 40)
    
    # Lire l'environnement actuel
    try:
        with open('.env', 'r') as f:
            content = f.read()
            if 'DJANGO_ENV="production"' in content:
                current_env = "production"
            elif 'DJANGO_ENV="development"' in content:
                current_env = "development"
            else:
                current_env = "inconnu"
        
        print(f"🎯 Environnement actuel: {current_env}")
        
        if current_env == "development":
            print("📍 Connecté à: Base locale PostgreSQL (db_linguify_dev)")
            print("💡 Pour accéder aux CVs: changez en 'production' temporairement")
        elif current_env == "production":
            print("📍 Connecté à: Supabase (production)")
            print("💡 Vous pouvez consulter les CVs réels")
        
    except FileNotFoundError:
        print("❌ Fichier .env introuvable!")
    
    # Vérifier PostgreSQL local
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True)
        if result.returncode == 0:
            print("✅ PostgreSQL local installé")
        else:
            print("❌ PostgreSQL local non installé")
    except FileNotFoundError:
        print("❌ PostgreSQL non trouvé (pas dans PATH)")

def main():
    print_header()
    
    if len(sys.argv) < 2:
        print_menu()
        print("\nUsage: python scripts/database/db_manager.py [action]")
        return
    
    action = sys.argv[1].lower()
    
    if action == "sync":
        print("🔄 Synchronisation production → développement")
        run_script('sync_prod_to_dev.py')
        
    elif action == "export":
        print("📥 Export depuis production")
        print("⚠️  Assurez-vous que DJANGO_ENV='production' dans .env")
        input("Appuyez sur Entrée pour continuer...")
        run_script('export_production_data.py')
        
    elif action == "import":
        print("📤 Import en développement")
        print("⚠️  Assurez-vous que DJANGO_ENV='development' dans .env")
        input("Appuyez sur Entrée pour continuer...")
        run_script('import_to_development.py')
        
    elif action == "clean":
        print("🧹 Nettoyage de la base de développement")
        run_script('clean_database.py')
        
    elif action == "setup":
        print("🛠️  Configuration PostgreSQL")
        script_path = os.path.join(os.path.dirname(__file__), 'setup_postgresql.sh')
        subprocess.run(['bash', script_path])
        
    elif action == "status":
        show_status()
        
    elif action in ["help", "h", "-h", "--help"]:
        print_menu()
        print("\n📖 Exemples d'usage:")
        print("  python scripts/database/db_manager.py sync")
        print("  python scripts/database/db_manager.py status")
        print("  python scripts/database/db_manager.py clean")
        
    else:
        print(f"❌ Action '{action}' inconnue")
        print_menu()

if __name__ == "__main__":
    main()