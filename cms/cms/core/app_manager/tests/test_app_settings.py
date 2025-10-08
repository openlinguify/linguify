#!/usr/bin/env python3
"""
Script de test pour le système d'activation/désactivation des apps
"""
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

django.setup()

from django.contrib.auth import get_user_model
from ..models import App, UserAppSettings

User = get_user_model()

def test_app_activation():
    """Test l'activation/désactivation des apps"""
    
    # Créer un utilisateur de test
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'pbkdf2_sha256$870000$dummy$dummy='  # Mot de passe dummy
        }
    )
    
    print(f"🧪 Test utilisateur: {user.username}")
    
    # Vérifier les apps disponibles
    print("\n📱 Apps disponibles:")
    for app in App.objects.filter(is_enabled=True):
        print(f"  - {app.code}: {app.display_name}")
    
    # Vérifier les apps activées pour l'utilisateur
    print("\n✅ Apps activées pour l'utilisateur:")
    user_settings, _ = UserAppSettings.objects.get_or_create(user=user)
    enabled_apps = user_settings.get_enabled_app_codes()
    print(f"Apps activées: {enabled_apps}")
    
    # Tester la récupération des paramètres avec filtrage
    print("\n⚙️  Récupération des paramètres (avec filtrage):")
    categories, tabs = AppSettingsService.get_all_settings_tabs(user=user)
    
    print(f"Catégories: {len(categories)}")
    for cat_id, cat_info in categories.items():
        print(f"  - {cat_id}: {cat_info['name']} ({len(cat_info['tabs'])} onglets)")
        for tab in cat_info['tabs']:
            print(f"    * {tab['id']}: {tab['name']}")
    
    # Tester la désactivation d'une app
    print("\n🔴 Désactivation de l'app 'revision':")
    user_settings, _ = UserAppSettings.objects.get_or_create(user=user)
    success = user_settings.disable_app('revision')
    print(f"Désactivation réussie: {success}")
    
    # Vérifier que l'app n'apparaît plus
    print("\n⚙️  Paramètres après désactivation:")
    categories, tabs = AppSettingsService.get_all_settings_tabs(user=user)
    
    revision_found = False
    for cat_id, cat_info in categories.items():
        for tab in cat_info['tabs']:
            if tab['id'] == 'revision':
                revision_found = True
                break
    
    print(f"App 'revision' visible: {revision_found}")
    
    # Réactiver l'app
    print("\n🟢 Réactivation de l'app 'revision':")
    success = user_settings.enable_app('revision')
    print(f"Réactivation réussie: {success}")
    
    # Vérifier que l'app réapparaît
    print("\n⚙️  Paramètres après réactivation:")
    categories, tabs = AppSettingsService.get_all_settings_tabs(user=user)
    
    revision_found = False
    for cat_id, cat_info in categories.items():
        for tab in cat_info['tabs']:
            if tab['id'] == 'revision':
                revision_found = True
                break
    
    print(f"App 'revision' visible: {revision_found}")
    
    # Nettoyer
    print("\n🧹 Nettoyage:")
    user.delete()
    print("Utilisateur de test supprimé")

if __name__ == "__main__":
    test_app_activation()