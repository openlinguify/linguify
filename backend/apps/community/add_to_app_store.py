#!/usr/bin/env python3
"""
Script pour ajouter l'app Community à l'app store d'OpenLinguify
"""

import os
import sys
import django

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from app_manager.models import App

def add_community_app():
    """Ajouter l'app Community à l'app store"""
    
    # Données de l'app Community
    community_app_data = {
        'code': 'community',
        'display_name': 'Community',
        'description': 'Connectez-vous avec d\'autres apprenants de langues. Trouvez des partenaires linguistiques, rejoignez des groupes d\'étude et participez à des conversations pour améliorer vos compétences.',
        'icon_name': 'Users',
        'color': '#16A085',  # Couleur turquoise pour l'aspect social
        'route_path': '/community',
        'category': 'Social',
        'version': '1.0.0',
        'installable': True,
        'is_enabled': True,
        'order': 6,
        'manifest_data': {
            'name': 'Community',
            'version': '1.0.0',
            'description': 'Social features for OpenLinguify - friends, groups, messaging, and community interactions',
            'category': 'Social',
            'author': 'OpenLinguify Team',
            'depends': ['authentication', 'notification'],
            'installable': True,
            'application': True,
            'auto_install': False,
            'icon': 'fa-users',
            'sequence': 30,
            'summary': 'Connect with other language learners',
            'urls': {
                'main': '/community/',
                'api': '/api/community/',
            },
            'features': [
                'friend_system',
                'user_discovery', 
                'messaging',
                'groups',
                'activity_feed',
                'recommendations',
                'badges',
                'stories'
            ],
            'menu_items': [
                {
                    'name': 'Discover Users',
                    'url': '/community/discover/',
                    'icon': 'fa-search',
                    'description': 'Find other language learners'
                },
                {
                    'name': 'My Friends',
                    'url': '/community/friends/',
                    'icon': 'fa-user-friends', 
                    'description': 'Manage your connections'
                },
                {
                    'name': 'Messages',
                    'url': '/community/messages/',
                    'icon': 'fa-envelope',
                    'description': 'Private conversations'
                },
                {
                    'name': 'Groups',
                    'url': '/community/groups/',
                    'icon': 'fa-users',
                    'description': 'Join language groups'
                },
                {
                    'name': 'Activity Feed',
                    'url': '/community/feed/',
                    'icon': 'fa-stream',
                    'description': 'See what friends are doing'
                }
            ],
            'frontend_components': {
                'icon': '👥',
                'description': 'Connect with language learners',
                'route': '/community'
            },
            'technical_info': {
                'web_url': '/community/',
                'api_url': '/api/v1/community/'
            }
        }
    }
    
    # Créer ou mettre à jour l'app
    app, created = App.objects.get_or_create(
        code='community',
        defaults=community_app_data
    )
    
    if created:
        print("✅ App Community créée avec succès dans l'app store!")
        print(f"   - Nom: {app.display_name}")
        print(f"   - Catégorie: {app.category}")
        print(f"   - Route: {app.route_path}")
        print(f"   - Version: {app.version}")
    else:
        # Mettre à jour les données existantes
        updated = False
        for key, value in community_app_data.items():
            if key != 'code' and getattr(app, key) != value:
                setattr(app, key, value)
                updated = True
        
        if updated:
            app.save()
            print("✅ App Community mise à jour dans l'app store!")
        else:
            print("ℹ️  App Community existe déjà et est à jour.")
    
    return app

def main():
    print("🚀 Ajout de l'app Community à l'app store d'OpenLinguify...")
    
    try:
        app = add_community_app()
        
        print(f"\n📊 Informations de l'app:")
        print(f"   - ID: {app.id}")
        print(f"   - Code: {app.code}")
        print(f"   - Nom d'affichage: {app.display_name}")
        print(f"   - Catégorie: {app.category}")
        print(f"   - Activée: {app.is_enabled}")
        print(f"   - Installable: {app.installable}")
        
        print(f"\n🔗 URLs de l'app:")
        print(f"   - Interface web: {app.route_path}")
        print(f"   - API: /api/v1/community/")
        
        print(f"\n✨ L'app Community devrait maintenant apparaître dans l'app store!")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'ajout de l'app Community: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()