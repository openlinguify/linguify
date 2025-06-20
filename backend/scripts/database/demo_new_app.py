#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de démonstration : Création et déploiement d'une nouvelle application
Simule le workflow complet d'ajout d'une nouvelle app
"""

import os
import sys
import django
import subprocess
from datetime import datetime

# Configuration Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')


def create_demo_app_in_dev():
    """Crée une application de démonstration en développement"""
    print("🏗️ Création d'une application de démonstration...")
    
    # Changer vers développement (si disponible) ou production pour la démo
    env = os.environ.copy()
    env['DJANGO_ENV'] = 'production'  # On utilise production pour la démo
    
    result = subprocess.run([
        sys.executable, '-c', '''
import django; django.setup()
from app_manager.models import App

# Vérifier si l'app demo existe déjà
demo_app, created = App.objects.get_or_create(
    code="demo_app_test",
    defaults={
        "display_name": "🚀 Demo App Test",
        "description": "Application de démonstration créée pour tester le workflow de déploiement",
        "icon_name": "rocket",
        "color": "#10B981",
        "route_path": "/demo-app",
        "category": "demo",
        "version": "1.0.0",
        "is_enabled": True,
        "installable": True,
        "order": 999,
        "manifest_data": {"demo": True}
    }
)

if created:
    print(f"✅ Application demo créée avec succès (ID: {demo_app.id})")
else:
    print(f"ℹ️  Application demo existe déjà (ID: {demo_app.id})")
    
print(f"📋 App: {demo_app.display_name} (code: {demo_app.code})")
'''
    ], env=env, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(result.stdout)
        return True
    else:
        print(f"❌ Erreur: {result.stderr}")
        return False


def main():
    print("🎯 DÉMONSTRATION DU WORKFLOW NOUVEAU DÉPLOIEMENT")
    print("=" * 60)
    print()
    
    print("📋 Scénario:")
    print("  1. Créer une nouvelle application 'demo_app_test'")
    print("  2. La déployer en utilisant notre système")
    print("  3. Montrer le workflow complet")
    print()
    
    # Étape 1: Créer l'app
    if not create_demo_app_in_dev():
        print("❌ Échec de la création de l'app demo")
        return
    
    print()
    print("🚀 Maintenant, vous pouvez tester le déploiement avec:")
    print("   make sync-app APP=demo_app_test")
    print()
    print("🔄 Ou utiliser le mode interactif avec:")
    print("   poetry run python scripts/database/selective_sync.py")
    print()
    print("📱 Applications actuellement disponibles:")
    
    # Lister les apps disponibles
    env = os.environ.copy()
    env['DJANGO_ENV'] = 'production'
    
    subprocess.run([
        sys.executable, '-c', '''
import django; django.setup()
from app_manager.models import App
print("Applications en production:")
for app in App.objects.all().order_by("order"):
    print(f"  - {app.display_name} (code: {app.code})")
'''
    ], env=env)


if __name__ == "__main__":
    main()