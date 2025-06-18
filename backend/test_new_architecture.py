#!/usr/bin/env python3
"""
Script de test pour la nouvelle architecture public_web + saas_web
"""

import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse, NoReverseMatch

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

User = get_user_model()

def test_public_routes():
    """Test des routes publiques"""
    client = Client()
    
    print("🌐 Test des routes publiques...")
    
    routes_to_test = [
        ('public_web:landing', '/'),
        ('public_web:features', '/features/'),
        ('public_web:about', '/about/'),
        ('public_web:contact', '/contact/'),
        ('public_web:apps', '/apps/'),
    ]
    
    for route_name, expected_path in routes_to_test:
        try:
            url = reverse(route_name)
            print(f"  ✓ {route_name}: {url}")
            
            response = client.get(url)
            if response.status_code == 200:
                print(f"    ✓ HTTP 200 OK")
            else:
                print(f"    ❌ HTTP {response.status_code}")
                
        except NoReverseMatch:
            print(f"  ❌ Route {route_name} non trouvée")
        except Exception as e:
            print(f"  ❌ Erreur pour {route_name}: {e}")

def test_saas_routes():
    """Test des routes SaaS (nécessitent une authentification)"""
    print("\n🔒 Test des routes SaaS...")
    
    # Test sans authentification
    client = Client()
    routes_to_test = [
        ('saas_web:dashboard', '/dashboard/'),
        ('saas_web:app_store', '/app-store/'),
        ('saas_web:settings', '/settings/'),
    ]
    
    for route_name, expected_path in routes_to_test:
        try:
            url = reverse(route_name)
            print(f"  ✓ {route_name}: {url}")
            
            response = client.get(url)
            if response.status_code == 302:  # Redirection vers login
                print(f"    ✓ Redirection vers login (attendu)")
            elif response.status_code == 200:
                print(f"    ⚠️  HTTP 200 (middleware d'auth non activé?)")
            else:
                print(f"    ❌ HTTP {response.status_code}")
                
        except NoReverseMatch:
            print(f"  ❌ Route {route_name} non trouvée")
        except Exception as e:
            print(f"  ❌ Erreur pour {route_name}: {e}")

def test_template_inheritance():
    """Test de l'héritage des templates"""
    print("\n📄 Test des templates...")
    
    from django.template.loader import get_template
    
    templates_to_test = [
        'public_web/base.html',
        'public_web/landing.html',
        'public_web/features.html',
        'saas_web/base.html',
        'saas_web/dashboard.html',
        'saas_web/app_store.html',
        'components/public_header.html',
        'components/public_footer.html',
        'components/app_header.html',
    ]
    
    for template_name in templates_to_test:
        try:
            template = get_template(template_name)
            print(f"  ✓ {template_name}")
        except Exception as e:
            print(f"  ❌ {template_name}: {e}")

def test_static_files():
    """Test des fichiers statiques"""
    print("\n📁 Test des fichiers statiques...")
    
    static_files = [
        'public_web/css/main.css',
        'public_web/js/main.js',
        'saas_web/css/main.css',
        'saas_web/js/main.js',
        'js/notifications.js',
    ]
    
    for static_file in static_files:
        file_path = os.path.join('backend', 'frontend_web', 'static', static_file)
        if os.path.exists(file_path):
            print(f"  ✓ {static_file}")
        else:
            # Check in new locations
            if 'public_web' in static_file:
                new_path = os.path.join('backend', 'public_web', 'static', static_file)
            elif 'saas_web' in static_file:
                new_path = os.path.join('backend', 'saas_web', 'static', static_file)
            else:
                new_path = os.path.join('backend', 'frontend_web', 'static', static_file)
                
            if os.path.exists(new_path):
                print(f"  ✓ {static_file} (nouveau emplacement)")
            else:
                print(f"  ❌ {static_file} non trouvé")

def test_apps_configuration():
    """Test de la configuration des apps"""
    print("\n⚙️  Test de la configuration des apps...")
    
    from django.apps import apps
    
    expected_apps = [
        'public_web',
        'saas_web',
        'frontend_web',  # Temporaire
    ]
    
    for app_name in expected_apps:
        try:
            app_config = apps.get_app_config(app_name)
            print(f"  ✓ {app_name}: {app_config.verbose_name}")
        except LookupError:
            print(f"  ❌ {app_name} non configuré dans INSTALLED_APPS")

def main():
    """Fonction principale"""
    print("🧪 Test de la nouvelle architecture Open Linguify")
    print("=" * 50)
    
    test_apps_configuration()
    test_public_routes()
    test_saas_routes()
    test_template_inheritance()
    test_static_files()
    
    print("\n" + "=" * 50)
    print("🎉 Tests terminés !")
    print("\n📝 Prochaines étapes :")
    print("  1. Activer le middleware de sécurité pour saas_web")
    print("  2. Migrer tous les templates restants")
    print("  3. Tester l'authentification complète")
    print("  4. Supprimer frontend_web après migration")

if __name__ == '__main__':
    main()