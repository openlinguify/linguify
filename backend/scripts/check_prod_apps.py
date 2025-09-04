#!/usr/bin/env python3
"""
Script pour vérifier les applications disponibles en production
"""

import os
import sys
import django

# Ajouter le répertoire backend au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
os.environ.setdefault('DJANGO_ENV', 'production')

def main():
    print("🚀 APPLICATIONS EN PRODUCTION:")
    print("=" * 50)
    
    try:
        django.setup()
        from app_manager.models import App
        
        # Apps visibles en production
        visible_apps = App.objects.filter(
            is_enabled=True, 
            installable=True
        ).order_by('order', 'display_name')
        
        if visible_apps.exists():
            print("📱 Applications accessibles aux utilisateurs:")
            for app in visible_apps:
                print(f"   ✅ {app.display_name} ({app.code})")
        else:
            print("   ℹ️  Aucune application visible actuellement")
        
        # Stats
        hidden_apps = App.objects.filter(is_enabled=False)
        total_apps = App.objects.all()
        
        print()
        print(f"📊 RÉSUMÉ:")
        print(f"   🔵 Visibles: {visible_apps.count()}")
        print(f"   ❌ Cachées: {hidden_apps.count()}")
        print(f"   📱 Total: {total_apps.count()}")
        
        # Apps cachées (développement)
        if hidden_apps.exists():
            print()
            print("🚧 Apps en développement (cachées):")
            for app in hidden_apps.order_by('display_name')[:5]:
                print(f"   ⚫ {app.display_name} ({app.code})")
            if hidden_apps.count() > 5:
                print(f"   ... et {hidden_apps.count() - 5} autres")
        
    except Exception as e:
        print("❌ PRODUCTION NON ACCESSIBLE")
        print("=" * 50)
        print("💡 Raisons possibles:")
        print("   - Credentials Supabase expirés/incorrects")
        print("   - Problème de réseau/VPN") 
        print("   - Base de données Supabase en maintenance")
        print("   - Variables d'environnement incorrectes")
        print()
        print("📋 APPS CONFIGURÉES LOCALEMENT (état probable en prod):")
        print("   ✅ Révision (revision) - Système de flashcards")
        print("   ✅ To-do (todo) - Listes de tâches")
        print("   ✅ Notes (notebook) - Prise de notes")
        print("   ✅ Documents (documents) - Gestion documents")
        print("   ❌ ~11 autres apps cachées (en développement)")
        print()
        print("🔧 Pour déboguer:")
        print("   make env-prod    # Vérifier config production")
        print("   make test-prod   # Tester connexion prod")
        print("   make apps        # Voir apps locales")
        print("   make env         # Voir environnement actuel")
        print()
        print(f"🔍 Erreur technique: {e}")

if __name__ == "__main__":
    main()