#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestionnaire d'applications - Visibilité, activation, déploiement
"""

import os
import sys
import django
import subprocess
from datetime import datetime

# Configuration Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')


def run_on_env(env_mode, command_script):
    """Exécute une commande sur un environnement spécifique"""
    env = os.environ.copy()
    env['DJANGO_ENV'] = env_mode
    
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    try:
        result = subprocess.run([
            sys.executable, '-c', command_script
        ], env=env, capture_output=True, text=True, cwd=backend_dir)
        
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, result.stderr.strip()
    except Exception as e:
        return False, str(e)


def hide_app(app_code, env_mode='production'):
    """Cache une application des utilisateurs"""
    command = f'''
import django; django.setup()
from app_manager.models import App

try:
    app = App.objects.get(code="{app_code}")
    app.is_enabled = False
    app.installable = False
    app.save()
    print(f"✅ App {{app.display_name}} cachée des utilisateurs")
    print(f"   - is_enabled: False")
    print(f"   - installable: False")
except App.DoesNotExist:
    print(f"❌ App {app_code} non trouvée")
'''
    
    success, output = run_on_env(env_mode, command)
    print(output)
    return success


def show_app(app_code, env_mode='production'):
    """Rend une application visible aux utilisateurs"""
    command = f'''
import django; django.setup()
from app_manager.models import App

try:
    app = App.objects.get(code="{app_code}")
    app.is_enabled = True
    app.installable = True
    app.save()
    print(f"✅ App {{app.display_name}} rendue visible")
    print(f"   - is_enabled: True")
    print(f"   - installable: True")
except App.DoesNotExist:
    print(f"❌ App {app_code} non trouvée")
'''
    
    success, output = run_on_env(env_mode, command)
    print(output)
    return success


def list_apps(env_mode='production'):
    """Liste toutes les applications avec leur statut"""
    command = '''
import django; django.setup()
from app_manager.models import App

print("📱 APPLICATIONS DISPONIBLES:")
print("=" * 50)

for app in App.objects.all().order_by("order"):
    status = "✅ Visible" if app.is_enabled and app.installable else "❌ Cachée"
    enabled = "🔵" if app.is_enabled else "⚫"
    installable = "📦" if app.installable else "🚫"
    
    print(f"{status} {app.display_name}")
    print(f"   Code: {app.code}")
    print(f"   État: {enabled} Enabled | {installable} Installable")
    print(f"   Ordre: {app.order}")
    print()
'''
    
    success, output = run_on_env(env_mode, command)
    print(output)
    return success


def set_app_order(app_code, order, env_mode='production'):
    """Change l'ordre d'affichage d'une application"""
    command = f'''
import django; django.setup()
from app_manager.models import App

try:
    app = App.objects.get(code="{app_code}")
    old_order = app.order
    app.order = {order}
    app.save()
    print(f"✅ App {{app.display_name}} ordre changé: {{old_order}} → {order}")
except App.DoesNotExist:
    print(f"❌ App {app_code} non trouvée")
'''
    
    success, output = run_on_env(env_mode, command)
    print(output)
    return success


def delete_app(app_code, env_mode='production'):
    """Supprime complètement une application (DANGER!)"""
    print(f"⚠️  ATTENTION: Suppression définitive de l'app {app_code}")
    response = input("Êtes-vous sûr? Tapez 'SUPPRIMER' pour confirmer: ")
    
    if response != 'SUPPRIMER':
        print("❌ Suppression annulée")
        return False
    
    command = f'''
import django; django.setup()
from app_manager.models import App

try:
    app = App.objects.get(code="{app_code}")
    app_name = app.display_name
    app.delete()
    print(f"✅ App {{app_name}} supprimée définitivement")
except App.DoesNotExist:
    print(f"❌ App {app_code} non trouvée")
'''
    
    success, output = run_on_env(env_mode, command)
    print(output)
    return success


def main():
    if len(sys.argv) < 2:
        print("🛠️  GESTIONNAIRE D'APPLICATIONS LINGUIFY")
        print("=" * 40)
        print()
        print("Usage: python app_manager.py <action> [args]")
        print()
        print("📋 Actions disponibles:")
        print("  list [env]              Liste toutes les apps")
        print("  hide <app_code>         Cache une app")
        print("  show <app_code>         Rend une app visible")
        print("  order <app_code> <num>  Change l'ordre d'affichage")
        print("  delete <app_code>       Supprime une app (DANGER!)")
        print()
        print("📱 Exemples:")
        print("  python app_manager.py list")
        print("  python app_manager.py list development")
        print("  python app_manager.py hide demo_app_test")
        print("  python app_manager.py show quizz")
        print("  python app_manager.py order course 1")
        return
    
    action = sys.argv[1].lower()
    
    # Déterminer l'environnement automatiquement ou par paramètre
    current_env = os.environ.get('DJANGO_ENV', 'development')
    
    if action == 'list':
        # Utiliser l'environnement passé en paramètre ou l'environnement actuel
        env_mode = sys.argv[2] if len(sys.argv) > 2 else current_env
        list_apps(env_mode)
    
    elif action == 'hide':
        if len(sys.argv) < 3:
            print("❌ Usage: python app_manager.py hide <app_code>")
            return
        app_code = sys.argv[2]
        hide_app(app_code, current_env)
    
    elif action == 'show':
        if len(sys.argv) < 3:
            print("❌ Usage: python app_manager.py show <app_code>")
            return
        app_code = sys.argv[2]
        show_app(app_code, current_env)
    
    elif action == 'order':
        if len(sys.argv) < 4:
            print("❌ Usage: python app_manager.py order <app_code> <number>")
            return
        app_code = sys.argv[2]
        try:
            order = int(sys.argv[3])
            set_app_order(app_code, order, current_env)
        except ValueError:
            print("❌ L'ordre doit être un nombre")
    
    elif action == 'delete':
        if len(sys.argv) < 3:
            print("❌ Usage: python app_manager.py delete <app_code>")
            return
        app_code = sys.argv[2]
        delete_app(app_code, current_env)
    
    else:
        print(f"❌ Action inconnue: {action}")
        print("Utilisez 'python app_manager.py' pour voir l'aide")


if __name__ == "__main__":
    main()