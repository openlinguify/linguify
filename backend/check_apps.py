#!/usr/bin/env python3
"""
Script pour vérifier l'état des apps dans la base de données Django
"""
import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from app_manager.models import AppDefinition, UserAppSettings
from django.contrib.auth import get_user_model

User = get_user_model()

def check_apps():
    """Vérifier l'état des apps"""
    print("=== Vérification des Apps ===\n")
    
    # Vérifier les apps dans la DB
    apps = AppDefinition.objects.all()
    print(f"📱 Apps définies dans la DB: {apps.count()}")
    
    for app in apps:
        print(f"  - {app.code}: {app.display_name} (enabled: {app.is_enabled})")
    
    if not apps.exists():
        print("❌ Aucune app trouvée dans la base de données!")
        print("   Il faut probablement exécuter les fixtures ou migrations")
        return False
    
    # Vérifier les settings utilisateur
    user_email = "louisphilippelalou@outlook.com"
    try:
        user = User.objects.get(email=user_email)
        print(f"\n👤 Utilisateur trouvé: {user.email} (ID: {user.id})")
        
        user_settings = UserAppSettings.objects.filter(user=user).first()
        if user_settings:
            print(f"⚙️  Settings utilisateur: {user_settings.enabled_apps}")
        else:
            print("❌ Aucun setting utilisateur trouvé - c'est le problème!")
            print("   L'utilisateur doit avoir des settings par défaut")
            
            # Créer des settings par défaut
            enabled_apps = [app.code for app in apps if app.is_enabled]
            UserAppSettings.objects.create(
                user=user,
                enabled_apps=enabled_apps
            )
            print(f"✅ Settings créés avec apps: {enabled_apps}")
        
    except User.DoesNotExist:
        print(f"❌ Utilisateur {user_email} non trouvé dans Django!")
        print("   L'utilisateur Supabase n'est pas synchronisé avec Django")
        
        # Créer l'utilisateur
        user = User.objects.create(
            email=user_email,
            username="llalou",
            first_name="Louis-Philippe",
            last_name="Lalou"
        )
        print(f"✅ Utilisateur créé: {user.email}")
        
        # Créer les settings
        enabled_apps = [app.code for app in apps if app.is_enabled]
        UserAppSettings.objects.create(
            user=user,
            enabled_apps=enabled_apps
        )
        print(f"✅ Settings créés avec apps: {enabled_apps}")
    
    return True

def create_default_apps():
    """Créer les apps par défaut si elles n'existent pas"""
    print("\n=== Création des Apps par Défaut ===\n")
    
    default_apps = [
        {
            'code': 'learning',
            'display_name': 'Learning',
            'description': 'Interactive language lessons and exercises',
            'icon_name': 'BookOpen',
            'color': '#8B5CF6',
            'route_path': '/learning',
            'is_enabled': True,
            'order': 1
        },
        {
            'code': 'flashcard',
            'display_name': 'Flashcards',
            'description': 'Memory training with spaced repetition',
            'icon_name': 'Brain',
            'color': '#EF4444',
            'route_path': '/flashcard',
            'is_enabled': True,
            'order': 2
        },
        {
            'code': 'notebook',
            'display_name': 'Notebook',
            'description': 'Take notes and organize vocabulary',
            'icon_name': 'NotebookPen',
            'color': '#06B6D4',
            'route_path': '/notebook',
            'is_enabled': True,
            'order': 3
        },
        {
            'code': 'language_ai',
            'display_name': 'AI Chat',
            'description': 'Practice conversations with AI',
            'icon_name': 'MessageSquare',
            'color': '#F59E0B',
            'route_path': '/language_ai',
            'is_enabled': True,
            'order': 4
        },
        {
            'code': 'task',
            'display_name': 'Tasks',
            'description': 'Manage learning goals and tasks',
            'icon_name': 'CheckSquare',
            'color': '#10B981',
            'route_path': '/task',
            'is_enabled': True,
            'order': 5
        }
    ]
    
    created_count = 0
    for app_data in default_apps:
        app, created = AppDefinition.objects.get_or_create(
            code=app_data['code'],
            defaults=app_data
        )
        if created:
            print(f"✅ App créée: {app.code}")
            created_count += 1
        else:
            print(f"ℹ️  App existe déjà: {app.code}")
    
    print(f"\n📱 {created_count} apps créées")
    return created_count > 0

if __name__ == '__main__':
    print("🔍 Diagnostic des Apps Linguify\n")
    
    # D'abord vérifier l'état actuel
    apps_exist = check_apps()
    
    # Si pas d'apps, en créer
    if not apps_exist:
        create_default_apps()
        # Re-vérifier après création
        check_apps()
    
    print("\n🎉 Diagnostic terminé!")
    print("   Rafraîchissez le frontend pour voir les changements")