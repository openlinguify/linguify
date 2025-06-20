#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Status simple et direct des bases de données
"""

import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')


def get_stats(env_mode):
    """Récupère les stats directement"""
    original_env = os.environ.get('DJANGO_ENV')
    
    try:
        # Changer l'environnement
        os.environ['DJANGO_ENV'] = env_mode
        
        # Reconfigurer Django
        from django.conf import settings
        if settings.configured:
            from importlib import reload
            from core import settings as settings_module
            reload(settings_module)
        
        django.setup()
        
        # Importer les modèles
        from app_manager.models import App
        from course.models import Lesson, TheoryContent
        from apps.authentication.models import User
        from django.db import connection
        
        # Tester la connexion
        cursor = connection.cursor()
        cursor.close()
        
        # Récupérer les stats
        stats = {
            'apps': App.objects.count(),
            'lessons': Lesson.objects.count(),
            'theory': TheoryContent.objects.count(),
            'users': User.objects.count(),
            'connected': True
        }
        
        return stats
        
    except Exception as e:
        return {'connected': False, 'error': str(e)}
    
    finally:
        # Restaurer l'environnement original
        if original_env:
            os.environ['DJANGO_ENV'] = original_env
        elif 'DJANGO_ENV' in os.environ:
            del os.environ['DJANGO_ENV']


def main():
    print("⚡ Status rapide et direct")
    print("=" * 35)
    print()
    
    # Test développement
    print("🏗️  Développement:", end=" ")
    dev_stats = get_stats('development')
    if dev_stats.get('connected'):
        print("✅ Connecté")
        print(f"   Apps: {dev_stats['apps']} | Lessons: {dev_stats['lessons']} | Theory: {dev_stats['theory']} | Users: {dev_stats['users']}")
    else:
        print("❌ Indisponible")
        print(f"   Erreur: {dev_stats.get('error', 'Connexion échouée')[:50]}...")
    
    print()
    
    # Test production
    print("🚀 Production:", end=" ")
    prod_stats = get_stats('production')
    if prod_stats.get('connected'):
        print("✅ Connecté")
        print(f"   Apps: {prod_stats['apps']} | Lessons: {prod_stats['lessons']} | Theory: {prod_stats['theory']} | Users: {prod_stats['users']}")
    else:
        print("❌ Indisponible")
        print(f"   Erreur: {prod_stats.get('error', 'Connexion échouée')[:50]}...")
    
    print()
    
    # Comparaison
    if dev_stats.get('connected') and prod_stats.get('connected'):
        print("📊 Différences (dev vs prod):")
        diff_apps = dev_stats['apps'] - prod_stats['apps']
        diff_lessons = dev_stats['lessons'] - prod_stats['lessons']
        diff_theory = dev_stats['theory'] - prod_stats['theory']
        
        if diff_apps != 0:
            print(f"   📱 Apps: {diff_apps:+d}")
        if diff_lessons != 0:
            print(f"   📚 Lessons: {diff_lessons:+d}")
        if diff_theory != 0:
            print(f"   📖 Theory: {diff_theory:+d}")
            
        if diff_apps > 0 or diff_lessons > 0 or diff_theory > 0:
            print("   🎯 Déploiement vers production recommandé!")
        elif diff_apps < 0 or diff_lessons < 0 or diff_theory < 0:
            print("   🔄 Synchronisation depuis production recommandée!")
        else:
            print("   ✅ Environnements synchronisés")
    elif prod_stats.get('connected'):
        print("💡 Conseil:")
        print("   Pour configurer le développement: ./quick-setup-postgres.sh")
        print("   Puis: make sync-prod")
    
    print()
    print("🛠️  Commandes disponibles:")
    print("   make sync-prod       # Production → Développement")
    print("   make deploy-prod     # Développement → Production")
    print("   make sync-app APP=X  # Sync app spécifique")


if __name__ == "__main__":
    main()