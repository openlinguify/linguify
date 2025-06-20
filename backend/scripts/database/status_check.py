#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de vérification du status des applications entre développement et production
Affiche les différences et recommande les actions à prendre
"""

import os
import sys
import django
import subprocess
from datetime import datetime, timedelta
from collections import defaultdict

# Configuration Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')


def test_db_connection(env_mode):
    """Teste la connexion à la base de données"""
    env = os.environ.copy()
    env['DJANGO_ENV'] = env_mode
    
    # Déterminer le répertoire backend
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    try:
        result = subprocess.run([
            sys.executable, '-c', 
            "import django; django.setup(); from django.db import connection; connection.cursor(); print('OK')"
        ], env=env, capture_output=True, text=True, timeout=10, cwd=backend_dir)
        
        return result.returncode == 0 and 'OK' in result.stdout
    except Exception as e:
        print(f"Debug: Error testing {env_mode}: {e}")
        return False


def get_database_stats(env_mode):
    """Récupère les statistiques de la base de données"""
    env = os.environ.copy()
    env['DJANGO_ENV'] = env_mode
    
    # Déterminer le répertoire backend
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    try:
        result = subprocess.run([
            sys.executable, '-c', '''
import django; django.setup()
from app_manager.models import App
from course.models import Course, Unit, Lesson, TheoryContent, VocabularyList, MatchingExercise
from apps.authentication.models import User
from notebook.models import Note
from revision.models import Flashcard, FlashcardDeck
from django.db import models
import json

stats = {
    "apps": {
        "total": App.objects.count(),
        "enabled": App.objects.filter(is_enabled=True).count(),
        "apps": []
    },
    "course": {
        "units": Unit.objects.count(),
        "lessons": Lesson.objects.count(),
        "theory_content": TheoryContent.objects.count(),
        "vocabulary_lists": VocabularyList.objects.count(),
        "matching_exercises": MatchingExercise.objects.count(),
        "recent_lessons": Lesson.objects.filter(created_at__gte=django.utils.timezone.now() - django.utils.timezone.timedelta(days=7)).count() if hasattr(Lesson.objects.first(), "created_at") else 0
    },
    "users": {
        "total": User.objects.count(),
        "recent": User.objects.filter(created_at__gte=django.utils.timezone.now() - django.utils.timezone.timedelta(days=7)).count() if hasattr(User.objects.first(), "created_at") else 0
    },
    "content": {
        "notes": Note.objects.count(),
        "flashcards": Flashcard.objects.count(),
        "flashcard_decks": FlashcardDeck.objects.count()
    },
    "last_updated": {
        "lessons": Lesson.objects.filter(updated_at__isnull=False).order_by("-updated_at").first().updated_at.isoformat() if Lesson.objects.filter(updated_at__isnull=False).exists() else None,
        "theory": TheoryContent.objects.order_by("-id").first().id if TheoryContent.objects.exists() else 0
    }
}

# Détails des applications
for app in App.objects.all().order_by("order"):
    stats["apps"]["apps"].append({
        "code": app.code,
        "display_name": app.display_name,
        "enabled": app.is_enabled,
        "version": getattr(app, "version", "1.0.0"),
        "category": getattr(app, "category", "general")
    })

print(json.dumps(stats, indent=2, default=str))
'''
        ], env=env, capture_output=True, text=True, cwd=backend_dir)
        
        if result.returncode == 0:
            import json
            return json.loads(result.stdout)
        else:
            print(f"Debug: Error getting stats for {env_mode}: {result.stderr}")
            return None
    except Exception as e:
        print(f"Debug: Exception getting stats for {env_mode}: {e}")
        return None


def compare_stats(dev_stats, prod_stats):
    """Compare les statistiques entre dev et prod"""
    if not dev_stats or not prod_stats:
        return None
        
    comparison = {
        "apps_diff": [],
        "content_diff": {},
        "recommendations": [],
        "needs_deployment": False
    }
    
    # Comparaison des applications
    dev_apps = {app["code"]: app for app in dev_stats["apps"]["apps"]}
    prod_apps = {app["code"]: app for app in prod_stats["apps"]["apps"]}
    
    # Apps nouvelles en dev
    new_in_dev = set(dev_apps.keys()) - set(prod_apps.keys())
    for app_code in new_in_dev:
        app = dev_apps[app_code]
        comparison["apps_diff"].append({
            "type": "new_in_dev",
            "app": app,
            "action": "deploy_to_prod"
        })
        comparison["needs_deployment"] = True
        comparison["recommendations"].append(f"🆕 Nouvelle app '{app['display_name']}' à déployer")
    
    # Apps modifiées
    for app_code in set(dev_apps.keys()) & set(prod_apps.keys()):
        dev_app = dev_apps[app_code]
        prod_app = prod_apps[app_code]
        
        if dev_app["version"] != prod_app["version"]:
            comparison["apps_diff"].append({
                "type": "version_diff",
                "app": dev_app,
                "dev_version": dev_app["version"],
                "prod_version": prod_app["version"],
                "action": "update_version"
            })
            comparison["needs_deployment"] = True
            comparison["recommendations"].append(f"📈 Version différente pour '{app['display_name']}': dev({dev_app['version']}) vs prod({prod_app['version']})")
    
    # Comparaison du contenu
    for category in ["course", "content"]:
        if category in dev_stats and category in prod_stats:
            dev_content = dev_stats[category]
            prod_content = prod_stats[category]
            
            comparison["content_diff"][category] = {}
            
            for key in dev_content:
                if isinstance(dev_content[key], int) and isinstance(prod_content.get(key, 0), int):
                    diff = dev_content[key] - prod_content.get(key, 0)
                    if diff > 0:
                        comparison["content_diff"][category][key] = {
                            "dev": dev_content[key],
                            "prod": prod_content.get(key, 0),
                            "diff": diff
                        }
                        
                        if diff >= 5:  # Seuil significatif
                            comparison["needs_deployment"] = True
                            comparison["recommendations"].append(f"📊 {key}: +{diff} nouveaux éléments en dev")
    
    return comparison


def print_status_report(dev_stats, prod_stats, comparison):
    """Affiche le rapport de status"""
    print("📊 RAPPORT DE STATUS DÉVELOPPEMENT ↔ PRODUCTION")
    print("=" * 60)
    print()
    
    # Status des connexions
    print("🔗 Connexions bases de données:")
    dev_available = dev_stats is not None
    prod_available = prod_stats is not None
    
    print(f"  - Développement: {'✅ Connecté' if dev_available else '❌ Indisponible'}")
    print(f"  - Production: {'✅ Connecté' if prod_available else '❌ Indisponible'}")
    print()
    
    if not prod_available:
        print("❌ Impossible de continuer sans connexion production")
        return
    
    # Statistiques générales
    print("📈 Statistiques générales:")
    if dev_available:
        print(f"  🏗️  Développement:")
        print(f"    - Applications: {dev_stats['apps']['total']} ({dev_stats['apps']['enabled']} activées)")
        print(f"    - Leçons: {dev_stats['course']['lessons']}")
        print(f"    - Contenu théorique: {dev_stats['course']['theory_content']}")
        print(f"    - Utilisateurs: {dev_stats['users']['total']}")
    
    print(f"  🚀 Production:")
    print(f"    - Applications: {prod_stats['apps']['total']} ({prod_stats['apps']['enabled']} activées)")
    print(f"    - Leçons: {prod_stats['course']['lessons']}")
    print(f"    - Contenu théorique: {prod_stats['course']['theory_content']}")
    print(f"    - Utilisateurs: {prod_stats['users']['total']}")
    print()
    
    # Comparaison (si dev disponible)
    if dev_available and comparison:
        print("🔍 Analyse des différences:")
        
        if comparison["needs_deployment"]:
            print("  ⚠️  DES CHANGEMENTS NÉCESSITENT UN DÉPLOIEMENT")
            print()
            
            # Applications
            if comparison["apps_diff"]:
                print("  📱 Applications:")
                for diff in comparison["apps_diff"]:
                    if diff["type"] == "new_in_dev":
                        print(f"    🆕 {diff['app']['display_name']} (code: {diff['app']['code']}) - NOUVELLE")
                    elif diff["type"] == "version_diff":
                        print(f"    📈 {diff['app']['display_name']} - Version dev: {diff['dev_version']}, prod: {diff['prod_version']}")
            
            # Contenu
            if comparison["content_diff"]:
                print("  📊 Contenu:")
                for category, diffs in comparison["content_diff"].items():
                    if diffs:
                        print(f"    {category.title()}:")
                        for key, data in diffs.items():
                            print(f"      - {key}: {data['prod']} → {data['dev']} (+{data['diff']})")
            
            print()
            print("🎯 Recommandations:")
            for rec in comparison["recommendations"]:
                print(f"  {rec}")
                
            print()
            print("🚀 Actions suggérées:")
            print("  make deploy-prod     # Déploiement interactif complet")
            print("  make sync-selective  # Mode interactif pour choix fins")
            
        else:
            print("  ✅ Aucune différence significative détectée")
            print("  🎯 Développement et production sont synchronisés")
    
    else:
        print("ℹ️  Développement indisponible - Comparaison impossible")
        print("🎯 Pour configurer le développement: make setup-db")
    
    print()
    print("📋 Applications disponibles:")
    for app in prod_stats["apps"]["apps"]:
        status = "✅" if app["enabled"] else "❌"
        print(f"  {status} {app['display_name']} (code: {app['code']})")


def main():
    print("🔍 Vérification du status des applications...")
    print()
    
    # Test des connexions
    dev_available = test_db_connection('development')
    prod_available = test_db_connection('production')
    
    # Récupération des stats
    dev_stats = get_database_stats('development') if dev_available else None
    prod_stats = get_database_stats('production') if prod_available else None
    
    # Comparaison
    comparison = compare_stats(dev_stats, prod_stats) if dev_stats and prod_stats else None
    
    # Affichage du rapport
    print_status_report(dev_stats, prod_stats, comparison)


if __name__ == "__main__":
    main()