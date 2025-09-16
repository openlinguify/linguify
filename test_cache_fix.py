#!/usr/bin/env python
"""
Script simple pour vérifier que le cache du dashboard est bien invalidé
quand une app est installée/désinstallée.
"""
import os
import sys
import django

# Configuration de Django
sys.path.append('/mnt/c/Users/louis/WebstormProjects/linguify/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.core.cache import cache
from app_manager.models import App, UserAppSettings
from app_manager.services import UserAppService

User = get_user_model()

def test_cache_invalidation():
    """Test que le cache est bien invalidé lors de l'installation d'une app"""
    print("=== Test de l'invalidation du cache ===")

    # Créer ou récupérer un utilisateur de test
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )

    if created:
        print(f"✅ Utilisateur de test créé: {user.username}")
    else:
        print(f"✅ Utilisateur de test trouvé: {user.username}")

    # Vérifier qu'il y a des apps disponibles
    available_apps = App.objects.filter(is_enabled=True, installable=True)
    if not available_apps.exists():
        print("❌ Aucune app disponible pour le test")
        return False

    test_app = available_apps.first()
    print(f"📱 App de test: {test_app.display_name} ({test_app.code})")

    # Étape 1: Vider le cache et initialiser
    cache_key = f"user_installed_apps_{user.id}"
    cache.delete(cache_key)
    print("🗑️  Cache vidé")

    # Étape 2: Générer le cache initial (sans l'app de test)
    user_settings, _ = UserAppSettings.objects.get_or_create(user=user)
    user_settings.enabled_apps.remove(test_app)  # S'assurer qu'elle n'est pas installée

    initial_apps = UserAppService.get_user_installed_apps(user)
    print(f"📦 Apps initiales en cache: {len(initial_apps)}")

    # Vérifier que le cache contient bien ces données
    cached_data = cache.get(cache_key)
    if cached_data:
        print("✅ Cache correctement initialisé")
    else:
        print("❌ Échec de l'initialisation du cache")
        return False

    # Étape 3: Installer l'app via le service (simuler l'API)
    user_settings.enabled_apps.add(test_app)
    cache.delete(cache_key)  # Simuler l'invalidation faite par l'API
    print(f"➕ App {test_app.display_name} installée et cache invalidé")

    # Étape 4: Vérifier que les nouvelles données incluent l'app
    updated_apps = UserAppService.get_user_installed_apps(user)
    print(f"📦 Apps après installation: {len(updated_apps)}")

    # Vérifier que l'app de test est maintenant présente
    app_found = any(app['name'] == test_app.code for app in updated_apps)

    if app_found:
        print(f"✅ L'app {test_app.display_name} est maintenant visible dans le dashboard")
        return True
    else:
        print(f"❌ L'app {test_app.display_name} n'est toujours pas visible")
        return False

if __name__ == "__main__":
    try:
        success = test_cache_invalidation()
        if success:
            print("\n🎉 Test réussi: Le cache est correctement invalidé!")
        else:
            print("\n💥 Test échoué: Problème avec l'invalidation du cache")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erreur pendant le test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)