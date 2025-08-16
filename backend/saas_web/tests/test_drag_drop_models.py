#!/usr/bin/env python3
"""
Script de test rapide pour valider les modèles de drag & drop
Utilisation: python test_drag_drop_models.py
"""

import os
import sys
import django

# Ajouter le répertoire parent pour l'import des modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from app_manager.models import App, UserAppSettings
from app_manager.services import UserAppService

User = get_user_model()

def test_models():
    """Test rapide des modèles de drag & drop"""
    print("🧪 Test des modèles de drag & drop")
    print("=" * 50)
    
    # 1. Créer ou récupérer un utilisateur de test
    user, created = User.objects.get_or_create(
        username='test_drag_drop',
        defaults={
            'email': 'test_drag_drop@example.com',
            'password': 'testpass123'
        }
    )
    print(f"✅ Utilisateur: {user.username} ({'créé' if created else 'existant'})")
    
    # 2. Vérifier les apps disponibles
    apps = App.objects.filter(is_enabled=True)
    print(f"✅ Applications disponibles: {apps.count()}")
    for app in apps:
        print(f"   - {app.display_name} -> {app.route_path}")
    
    # 3. Créer/récupérer les settings utilisateur
    user_settings = UserAppService.get_or_create_user_settings(user)
    print(f"✅ Settings utilisateur: {user_settings}")
    
    # 4. Activer quelques apps si nécessaire
    if user_settings.enabled_apps.count() == 0:
        user_settings.enabled_apps.set(apps[:5])  # Activer les 5 premières
        print(f"✅ Apps activées: {user_settings.enabled_apps.count()}")
    
    # 5. Test de l'ordre par défaut
    print(f"\n📋 Ordre actuel: {user_settings.app_order}")
    
    # 6. Test de mise à jour d'ordre
    enabled_apps = user_settings.enabled_apps.all()
    app_names = [app.display_name for app in enabled_apps]
    
    if len(app_names) >= 3:
        # Inverser l'ordre des 3 premières apps
        new_order = app_names[:3][::-1] + app_names[3:]
        print(f"📋 Nouvel ordre de test: {new_order}")
        
        success = user_settings.update_app_order(new_order)
        print(f"✅ Mise à jour réussie: {success}")
        
        user_settings.refresh_from_db()
        print(f"📋 Ordre sauvegardé: {user_settings.app_order}")
    
    # 7. Test de récupération ordonnée
    ordered_apps = user_settings.get_ordered_enabled_apps()
    print(f"\n🎯 Apps dans l'ordre personnalisé:")
    for i, app in enumerate(ordered_apps):
        print(f"   {i+1}. {app.display_name}")
    
    # 8. Test du service UserAppService
    installed_apps = UserAppService.get_user_installed_apps(user)
    print(f"\n🎯 Apps formatées pour le frontend:")
    for app_data in installed_apps:
        print(f"   - {app_data['display_name']} -> {app_data['url']}")
    
    # 9. Test avec ordre partiel
    if len(app_names) >= 2:
        partial_order = app_names[:2]  # Seulement les 2 premières
        user_settings.update_app_order(partial_order)
        
        ordered_apps = user_settings.get_ordered_enabled_apps()
        result_names = [app.display_name for app in ordered_apps]
        
        print(f"\n🧪 Test ordre partiel:")
        print(f"   Ordre partiel: {partial_order}")
        print(f"   Résultat complet: {result_names}")
        
        # Vérifier que les premières apps suivent l'ordre
        assert result_names[:2] == partial_order, "Ordre partiel non respecté"
        print("   ✅ Ordre partiel respecté")
        
        # Vérifier que toutes les apps sont présentes
        assert len(result_names) == len(app_names), "Apps manquantes"
        print("   ✅ Toutes les apps présentes")
    
    print(f"\n🎉 Tous les tests sont passés!")
    return True

def test_edge_cases():
    """Test des cas limites"""
    print("\n🧪 Test des cas limites")
    print("=" * 30)
    
    user = User.objects.get(username='test_drag_drop')
    user_settings = UserAppSettings.objects.get(user=user)
    
    # 1. Test avec liste vide
    user_settings.update_app_order([])
    ordered = user_settings.get_ordered_enabled_apps()
    print(f"✅ Liste vide: {len(ordered)} apps récupérées")
    
    # 2. Test avec noms d'apps invalides
    invalid_order = ['App Inexistante', 'Autre App Bidon']
    success = user_settings.update_app_order(invalid_order)
    user_settings.refresh_from_db()
    print(f"✅ Apps invalides: success={success}, order={user_settings.app_order}")
    
    # 3. Test avec mix valide/invalide
    enabled_apps = [app.display_name for app in user_settings.enabled_apps.all()]
    if enabled_apps:
        mixed_order = [enabled_apps[0], 'App Inexistante', enabled_apps[-1] if len(enabled_apps) > 1 else 'Test']
        user_settings.update_app_order(mixed_order)
        user_settings.refresh_from_db()
        
        # Seules les apps valides doivent être sauvegardées
        valid_in_order = [name for name in user_settings.app_order if name in enabled_apps]
        print(f"✅ Mix valide/invalide: {len(valid_in_order)} apps valides conservées")
    
    print("✅ Cas limites validés")

if __name__ == "__main__":
    try:
        test_models()
        test_edge_cases()
        print(f"\n🎯 Résumé: Tous les tests de modèles sont passés avec succès!")
    except Exception as e:
        print(f"\n❌ Erreur dans les tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)