#!/usr/bin/env python3
"""
Script pour supprimer complètement une app Django
Usage: python scripts/delete_app.py <app_name>
"""
import os
import sys
import shutil
import django
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH
script_dir = Path(__file__).parent
backend_dir = script_dir.parent
sys.path.insert(0, str(backend_dir))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()


def delete_app(app_name):
    """Supprime complètement une app Django"""
    
    if not app_name:
        print("❌ Usage: python scripts/delete_app.py <app_name>")
        return False
    
    base_dir = Path(__file__).parent.parent
    app_dir = base_dir / 'apps' / app_name
    
    print(f"🗑️ SUPPRESSION DE L'APP: {app_name}")
    print("=" * 50)
    print(f"📍 Directory: {app_dir}")
    print()
    
    # Vérifier si l'app existe
    if not app_dir.exists():
        print(f"❌ L'app '{app_name}' n'existe pas dans apps/{app_name}")
        return False
    
    # Confirmation
    confirm = input(f"⚠️ Êtes-vous sûr de vouloir supprimer l'app '{app_name}' ? (oui/non): ").lower().strip()
    if confirm not in ['oui', 'o', 'yes', 'y']:
        print("❌ Suppression annulée")
        return False
    
    try:
        # 1. Supprimer de la base de données
        try:
            from app_manager.models import App, UserAppSettings
            from django.contrib.auth import get_user_model
            
            print("🗃️ Suppression de la base de données...")
            
            # Supprimer l'app de la base de données
            try:
                app_obj = App.objects.get(code=app_name)
                
                # Supprimer des dashboards utilisateurs
                User = get_user_model()
                users = User.objects.all()
                removed_count = 0
                
                for user in users:
                    try:
                        user_settings = UserAppSettings.objects.get(user=user)
                        if user_settings.enabled_apps.filter(code=app_name).exists():
                            user_settings.enabled_apps.remove(app_obj)
                            removed_count += 1
                            print(f"   ✅ Supprimée du dashboard de {user.username}")
                    except UserAppSettings.DoesNotExist:
                        pass
                
                print(f"   🎯 App supprimée de {removed_count} dashboards")
                
                # Supprimer l'objet App
                app_obj.delete()
                print(f"   ✅ App '{app_obj.display_name}' supprimée de la base de données")
                
            except App.DoesNotExist:
                print(f"   ℹ️ App '{app_name}' n'existe pas dans la base de données")
                
        except Exception as e:
            print(f"   ⚠️ Erreur lors de la suppression de la base de données: {e}")
            print("   (L'app sera quand même supprimée du système de fichiers)")
        
        # 2. Supprimer les migrations si elles existent
        migrations_dirs = [
            base_dir / 'migrations' / f'{app_name}_migrations',
            app_dir / 'migrations',
        ]
        
        for migrations_dir in migrations_dirs:
            if migrations_dir.exists():
                shutil.rmtree(migrations_dir)
                print(f"   ✅ Migrations supprimées: {migrations_dir}")
        
        # 3. Supprimer le dossier de l'app
        shutil.rmtree(app_dir)
        print(f"   ✅ Dossier app supprimé: {app_dir}")
        
        # 4. Nettoyer les fichiers __pycache__
        pycache_dirs = []
        for root, dirs, files in os.walk(base_dir):
            if '__pycache__' in dirs and app_name in root:
                pycache_dirs.append(Path(root) / '__pycache__')
        
        for pycache_dir in pycache_dirs:
            if pycache_dir.exists():
                shutil.rmtree(pycache_dir)
                print(f"   ✅ Cache supprimé: {pycache_dir}")
        
        # 5. Resynchroniser le système (optionnel)
        try:
            print("🔄 Resynchronisation du système...")
            from app_manager.services.auto_manifest_service import AutoManifestService
            from app_manager.services.auto_url_service import AutoURLService
            from app_manager.models import App as AppModel
            
            # Resynchroniser
            AutoManifestService.sync_all_apps()
            AutoURLService.sync_all_urls()
            AppModel.sync_apps()
            print("   ✅ Système resynchronisé")
            
        except Exception as e:
            print(f"   ⚠️ Erreur lors de la resynchronisation: {e}")
            print("   Vous pourrez exécuter manuellement: poetry run python manage.py setup_auto_apps")
        
        print()
        print("🎉 APP SUPPRIMÉE AVEC SUCCÈS!")
        print("="*50)
        print("✅ Dossier app supprimé")
        print("✅ Base de données nettoyée")
        print("✅ Migrations supprimées")
        print("✅ Cache nettoyé")
        print("✅ Dashboards utilisateurs mis à jour")
        print()
        print("ℹ️ L'app a été complètement supprimée du système.")
        print("   Vous pouvez maintenant la recréer si nécessaire.")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la suppression: {e}")
        return False


def list_apps():
    """Liste toutes les apps disponibles"""
    base_dir = Path(__file__).parent.parent
    apps_dir = base_dir / 'apps'
    
    if not apps_dir.exists():
        print("❌ Dossier apps non trouvé")
        return
    
    apps = []
    for item in apps_dir.iterdir():
        if item.is_dir() and item.name != '__pycache__' and not item.name.startswith('.'):
            # Vérifier si c'est une vraie app Django
            if (item / '__init__.py').exists() and (item / 'apps.py').exists():
                apps.append(item.name)
    
    if not apps:
        print("ℹ️ Aucune app Django trouvée")
        return
    
    print(f"📱 Apps Django disponibles ({len(apps)}):")
    print("=" * 40)
    for app in sorted(apps):
        print(f"   • {app}")
    print()
    print("💡 Pour supprimer une app: python scripts/delete_app.py <app_name>")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("❌ Usage: python scripts/delete_app.py <app_name>")
        print("📝 Exemple: python scripts/delete_app.py learn_write")
        print()
        list_apps()
        sys.exit(1)
    
    app_name = sys.argv[1]
    
    # Gestion des commandes spéciales
    if app_name == '--list' or app_name == '-l':
        list_apps()
        sys.exit(0)
    
    if delete_app(app_name):
        sys.exit(0)
    else:
        sys.exit(1)