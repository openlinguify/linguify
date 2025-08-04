#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestionnaire de manifests d'applications
Gère l'intégration entre les manifests et la base de données
"""

import os
import sys
import json
import glob
from pathlib import Path

# Configuration Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')


def find_app_manifests():
    """Trouve tous les fichiers __manifest__.py dans les applications"""
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    apps_dir = os.path.join(backend_dir, 'apps')
    
    manifests = []
    
    # Apps à ignorer (apps système ou internes)
    ignored_apps = {'authentication', 'app_manager', 'cms_sync', 'data', 'notification', 
                   'payments', 'subscription', 'task', 'coaching'}
    
    # Chercher dans le dossier apps/
    for app_dir in glob.glob(os.path.join(apps_dir, '*')):
        if os.path.isdir(app_dir):
            app_name = os.path.basename(app_dir)
            
            # Ignorer les apps système
            if app_name in ignored_apps:
                continue
                
            manifest_path = os.path.join(app_dir, '__manifest__.py')
            if os.path.exists(manifest_path):
                manifests.append({
                    'app_name': app_name,
                    'path': manifest_path,
                    'relative_path': f'apps/{app_name}/__manifest__.py'
                })
    
    return manifests


def read_manifest(manifest_path):
    """Lit et parse un fichier manifest"""
    try:
        # Lire le fichier comme du Python
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Exécuter le code pour obtenir les variables
        namespace = {}
        exec(content, namespace)
        
        # Extraire le dictionnaire __manifest__
        if '__manifest__' in namespace:
            manifest_data = namespace['__manifest__']
        else:
            # Fallback: extraire les variables individuelles
            manifest_data = {}
            manifest_keys = [
                'name', 'version', 'description', 'author', 'category', 
                'depends', 'auto_install', 'installable', 'application',
                'icon', 'color', 'route_path', 'order', 'permissions', 'summary'
            ]
            
            for key in manifest_keys:
                if key in namespace:
                    manifest_data[key] = namespace[key]
        
        return manifest_data
    
    except Exception as e:
        return {'error': str(e)}


def sync_manifest_to_db(app_name, manifest_data, env_mode='production'):
    """Synchronise un manifest vers la base de données"""
    from scripts.database.app_manager import run_on_env
    
    # Déterminer la visibilité selon l'environnement
    is_production_ready = manifest_data.get('installable', True)
    menu_order = manifest_data.get('frontend_components', {}).get('menu_order', 100)
    
    command = f'''
import django; django.setup()
from app_manager.models import App
import json

manifest_data = {json.dumps(manifest_data)}
app_name = "{app_name}"
env_mode = "{env_mode}"

# Logique de visibilité selon l'environnement
is_application_ready = manifest_data.get('application', True)
is_installable = manifest_data.get('installable', True)

# En production : seulement les apps avec 'application': True
if env_mode == 'production':
    should_be_visible_in_env = is_application_ready and is_installable
# En développement : toutes les apps sont visibles (pour pouvoir les développer)
else:
    should_be_visible_in_env = True

try:
    app, created = App.objects.get_or_create(
        code=app_name,
        defaults={{
            'display_name': manifest_data.get('name', app_name.title()),
            'description': manifest_data.get('description', f'Application {{app_name}}'),
            'icon_name': manifest_data.get('icon', 'package'),
            'color': manifest_data.get('color', '#3B82F6'),
            'route_path': manifest_data.get('route_path', f'/{{app_name}}'),
            'category': manifest_data.get('category', 'general'),
            'version': manifest_data.get('version', '1.0.0'),
            'is_enabled': should_be_visible_in_env,
            'installable': should_be_visible_in_env,
            'order': manifest_data.get('frontend_components', {{}}).get('menu_order', 100),
            'manifest_data': manifest_data
        }}
    )
    
    if created:
        print(f"✅ App {{app.display_name}} créée depuis manifest")
    else:
        # Mettre à jour les champs depuis le manifest SANS toucher à la visibilité
        updated_fields = []
        
        # Mettre à jour les informations de base du manifest
        if app.display_name != manifest_data.get('name', app.display_name):
            app.display_name = manifest_data.get('name', app.display_name)
            updated_fields.append('nom')
        if app.description != manifest_data.get('description', app.description):
            app.description = manifest_data.get('description', app.description)
            updated_fields.append('description')
        if app.version != manifest_data.get('version', app.version):
            app.version = manifest_data.get('version', app.version)
            updated_fields.append('version')
        
        # Mettre à jour l'ordre SEULEMENT si ce n'est pas 100 (valeur par défaut)
        new_order = manifest_data.get('frontend_components', {{}}).get('menu_order', 100)
        if app.order == 100 and new_order != 100:
            app.order = new_order
            updated_fields.append('ordre')
        
        # IMPORTANT: Ne pas toucher à is_enabled et installable
        # Ces champs sont gérés manuellement par l'administrateur
        
        app.manifest_data = manifest_data
        app.save()
        
        if updated_fields:
            print(f"✅ App {{app.display_name}} mise à jour depuis manifest ({{', '.join(updated_fields)}})")
        else:
            print(f"✅ App {{app.display_name}} - aucune mise à jour nécessaire")
        
    print(f"   Code: {{app.code}}")
    print(f"   Version: {{app.version}}")
    print(f"   Ordre: {{app.order}}")
    print(f"   Visible: {{'Oui' if app.is_enabled else 'Non'}}")
    
except Exception as e:
    print(f"❌ Erreur: {{e}}")
'''
    
    success, output = run_on_env(env_mode, command)
    print(output)
    return success


def list_manifests():
    """Liste tous les manifests trouvés"""
    manifests = find_app_manifests()
    
    print("📋 MANIFESTS D'APPLICATIONS TROUVÉS")
    print("=" * 40)
    print()
    
    for manifest_info in manifests:
        print(f"📱 App: {manifest_info['app_name']}")
        print(f"   Chemin: {manifest_info['relative_path']}")
        
        manifest_data = read_manifest(manifest_info['path'])
        
        if 'error' in manifest_data:
            print(f"   ❌ Erreur: {manifest_data['error']}")
        else:
            print(f"   Nom: {manifest_data.get('name', 'Non défini')}")
            print(f"   Version: {manifest_data.get('version', 'Non définie')}")
            print(f"   Installable: {manifest_data.get('installable', True)}")
            print(f"   Application: {manifest_data.get('application', True)}")
        print()


def sync_all_manifests(env_mode='production'):
    """Synchronise tous les manifests vers la base de données"""
    manifests = find_app_manifests()
    
    print(f"🔄 SYNCHRONISATION DES MANIFESTS VERS {env_mode.upper()}")
    print("=" * 50)
    print()
    
    success_count = 0
    
    for manifest_info in manifests:
        print(f"📱 Traitement de {manifest_info['app_name']}...")
        
        manifest_data = read_manifest(manifest_info['path'])
        
        if 'error' in manifest_data:
            print(f"   ❌ Erreur dans le manifest: {manifest_data['error']}")
            continue
        
        if sync_manifest_to_db(manifest_info['app_name'], manifest_data, env_mode):
            success_count += 1
        
        print()
    
    print(f"📊 Résultat: {success_count}/{len(manifests)} manifests synchronisés")


def apply_manifest_visibility(env_mode='development'):
    """Applique la visibilité selon les manifests pour l'environnement donné"""
    print(f"🔧 APPLICATION DE LA VISIBILITÉ SELON LES MANIFESTS ({env_mode.upper()})")
    print("=" * 70)
    print()
    
    manifests = find_app_manifests()
    if not manifests:
        print("❌ Aucun manifest trouvé")
        return
    
    for manifest_info in manifests:
        app_name = manifest_info['app_name']
        manifest_path = manifest_info['path']
        manifest_data = read_manifest(manifest_path)
        if 'error' in manifest_data:
            print(f"❌ Erreur lors du chargement du manifest pour {app_name}: {manifest_data['error']}")
            continue
        
        # Déterminer si l'app doit être visible selon le manifest
        is_application_ready = manifest_data.get('application', True)
        is_installable = manifest_data.get('installable', True)
        
        if env_mode == 'production':
            should_be_visible = is_application_ready and is_installable
            reason = f"application={is_application_ready}, installable={is_installable}"
        else:
            should_be_visible = True
            reason = "développement (toutes visibles)"
        
        # Appliquer la visibilité
        from scripts.database.app_manager import run_on_env
        
        command = f'''
import django; django.setup()
from app_manager.models import App

try:
    app = App.objects.get(code="{app_name}")
    old_enabled = app.is_enabled
    old_installable = app.installable
    
    app.is_enabled = {should_be_visible}
    app.installable = {should_be_visible}
    app.save()
    
    if old_enabled != {should_be_visible} or old_installable != {should_be_visible}:
        status = "✅ Visible" if {should_be_visible} else "❌ Cachée"
        print(f"🔄 {{app.display_name}}: {{status}} ({{"{reason}"}})")
    else:
        status = "✅ Visible" if {should_be_visible} else "❌ Cachée"
        print(f"✅ {{app.display_name}}: {{status}} (inchangé)")
        
except App.DoesNotExist:
    print(f"⚠️  App {app_name} non trouvée en base")
except Exception as e:
    print(f"❌ Erreur: {{e}}")
'''
        
        success, output = run_on_env(env_mode, command)
        if not success:
            print(f"❌ Erreur pour {app_name}: {output}")


def main():
    if len(sys.argv) < 2:
        print("📋 GESTIONNAIRE DE MANIFESTS")
        print("=" * 30)
        print()
        print("Usage: python manifest_manager.py <action>")
        print()
        print("📋 Actions:")
        print("  list           Liste tous les manifests")
        print("  sync           Synchronise les manifests vers la DB (sans changer visibilité)")
        print("  sync-dev       Synchronise vers développement")
        print("  sync-prod      Synchronise vers production") 
        print("  apply-manifest Applique la visibilité selon les manifests")
        print()
        return
    
    action = sys.argv[1].lower()
    
    # Déterminer l'environnement automatiquement ou par paramètre
    current_env = os.environ.get('DJANGO_ENV', 'development')
    
    if action == 'list':
        list_manifests()
    
    elif action == 'sync':
        # Utiliser l'environnement actuel par défaut
        sync_all_manifests(current_env)
    
    elif action == 'sync-dev':
        sync_all_manifests('development')
    
    elif action == 'sync-prod':
        sync_all_manifests('production')
    
    elif action == 'apply-manifest':
        apply_manifest_visibility(current_env)
    
    else:
        print(f"❌ Action inconnue: {action}")


if __name__ == "__main__":
    main()