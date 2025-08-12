"""
Import des données de production dans la base de développement
Usage: DJANGO_ENV="development" puis lancer ce script
"""
import os
import sys
import subprocess

# Forcer UTF-8
sys.stdout.reconfigure(encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Ajouter le répertoire parent au path Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from django.core.management import call_command
from django.db import connection

print("📤 Import des données en développement")
print("=" * 50)

# Vérifier qu'on est en développement
print(f"🔗 Connecté à: {connection.settings_dict['HOST']}")

if 'localhost' not in connection.settings_dict['HOST']:
    print("❌ ERREUR: Pas en mode développement!")
    print("   Changez DJANGO_ENV='development' dans .env")
    sys.exit(1)

# Vérifier le fichier d'export
export_file = 'production_export.json'
if not os.path.exists(export_file):
    print(f"❌ Fichier {export_file} introuvable!")
    print("   Lancez d'abord: python scripts/database/export_production_data.py")
    sys.exit(1)

try:
    size_mb = os.path.getsize(export_file) / 1024 / 1024
    print(f"📁 Fichier trouvé: {export_file} ({size_mb:.2f} MB)")
    
    print("\n🗑️  Nettoyage complet de la base locale...")
    
    # Recréer la base complètement
    db_name = connection.settings_dict['NAME']
    db_user = connection.settings_dict['USER'] 
    db_password = connection.settings_dict['PASSWORD']
    
    # Fermer la connexion Django
    connection.close()
    
    # Commandes PostgreSQL
    postgres_conn = f"postgresql://{db_user}:{db_password}@localhost:5432/postgres"
    
    print("   Suppression de la base...")
    subprocess.run([
        "psql", postgres_conn, "-c", f"DROP DATABASE IF EXISTS {db_name};"
    ], capture_output=True)
    
    print("   Création de la base...")
    subprocess.run([
        "psql", postgres_conn, "-c", f"CREATE DATABASE {db_name} WITH ENCODING 'UTF8';"
    ], capture_output=True)
    
    print("   ✅ Base recréée")
    
    # Recharger Django
    django.setup()
    
    print("\n🔧 Application des migrations...")
    call_command('migrate', verbosity=0)
    
    print("\n📥 Import des données...")
    call_command('loaddata', export_file, verbosity=1)
    
    print("\n✅ SUCCÈS! Import terminé!")
    
    # Vérification et statistiques
    print("\n📊 Données importées:")
    
    try:
        from apps.authentication.models import User
        user_count = User.objects.count()
        print(f"   👥 Utilisateurs: {user_count}")
    except:
        user_count = 0
    
    try:
        from app_manager.models import App
        app_count = App.objects.count()
        print(f"   📱 Applications: {app_count}")
    except:
        app_count = 0
    
    try:
        from apps.course.models import Lesson, Unit, VocabularyList
        unit_count = Unit.objects.count()
        lesson_count = Lesson.objects.count()
        vocab_count = VocabularyList.objects.count()
        
        print(f"   📚 Unités: {unit_count}")
        print(f"   📖 Leçons: {lesson_count}")
        print(f"   📝 Vocabulaire: {vocab_count}")
    except Exception as e:
        unit_count = lesson_count = vocab_count = 0
        print(f"   ⚠️  Course data: {e}")
    
    try:
        from core.jobs.models import JobApplication, JobPosition
        pos_count = JobPosition.objects.count()
        job_app_count = JobApplication.objects.count()
        
        print(f"   💼 Postes: {pos_count}")
        print(f"   📋 Candidatures: {job_app_count}")
    except:
        pos_count = job_app_count = 0
    
    try:
        from apps.revision.models import Flashcard
        flash_count = Flashcard.objects.count()
        print(f"   🔄 Flashcards: {flash_count}")
    except:
        flash_count = 0
    
    total_imported = user_count + app_count + lesson_count + vocab_count + flash_count
    print(f"\n🎯 TOTAL: ~{total_imported} objets importés!")
    
    print(f"\n🚀 Prochaines étapes:")
    print(f"1. Créer votre superuser:")
    print(f"   python manage.py createsuperuser")
    print(f"   Username: admin  # Replace with your username")
    print(f"   Email: admin@example.com  # Replace with your admin email")
    print(f"   Password: password")
    print(f"2. Lancer le serveur:")
    print(f"   python manage.py runserver")
    print(f"3. Accéder à l'admin:")
    print(f"   http://localhost:8000/admin/")
    
    print(f"\n💡 Pour accéder aux CVs de production:")
    print(f"   Changez temporairement DJANGO_ENV='production'")
    
    # Nettoyer le fichier d'export
    confirm = input(f"\n🧹 Supprimer le fichier {export_file}? (y/N): ")
    if confirm.lower() == 'y':
        os.remove(export_file)
        print(f"   ✅ Fichier {export_file} supprimé")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()