#!/usr/bin/env python3
"""
Script de diagnostic pour l'authentification Supabase
"""
import os
import sys
import django
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings
import requests
import jwt

def test_supabase_config():
    """Test la configuration Supabase"""
    print("=== TEST CONFIGURATION SUPABASE ===")
    
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_ANON_KEY', 
        'SUPABASE_SERVICE_ROLE_KEY',
        'SUPABASE_JWT_SECRET'
    ]
    
    for var in required_vars:
        value = getattr(settings, var, None)
        if value:
            print(f"✅ {var}: {value[:20]}...{value[-10:]}")
        else:
            print(f"❌ {var}: NOT SET")
    
    print(f"\n✅ PROJECT URL: {settings.SUPABASE_URL}")
    print(f"✅ PROJECT ID: {getattr(settings, 'SUPABASE_PROJECT_ID', 'NOT SET')}")

def test_jwt_verification():
    """Test la vérification JWT avec un token factice"""
    print("\n=== TEST VERIFICATION JWT ===")
    
    try:
        from apps.authentication.supabase_auth import SupabaseAuthentication
        
        auth = SupabaseAuthentication()
        print(f"✅ SupabaseAuthentication initialisé")
        print(f"✅ JWT Secret: {auth.jwt_secret[:20]}...{auth.jwt_secret[-10:]}")
        print(f"✅ Project URL: {auth.project_url}")
        
    except Exception as e:
        print(f"❌ Erreur initialisation SupabaseAuthentication: {e}")

def test_backend_endpoints():
    """Test les endpoints backend"""
    print("\n=== TEST ENDPOINTS BACKEND ===")
    
    base_url = "http://localhost:8000"
    
    # Test basic endpoint
    try:
        response = requests.get(f"{base_url}/api/auth/debug/supabase-config/", timeout=5)
        print(f"✅ Debug endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Debug endpoint: {e}")
    
    # Test Supabase auth endpoints
    endpoints = [
        "/api/auth/supabase/login/",
        "/api/auth/supabase/signup/", 
        "/api/auth/terms/status/",
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            print(f"✅ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")

def test_supabase_connection():
    """Test la connexion à Supabase"""
    print("\n=== TEST CONNEXION SUPABASE ===")
    
    try:
        url = f"{settings.SUPABASE_URL}/rest/v1/"
        headers = {
            'apikey': settings.SUPABASE_ANON_KEY,
            'Authorization': f'Bearer {settings.SUPABASE_ANON_KEY}'
        }
        
        response = requests.get(url, headers=headers, timeout=5)
        print(f"✅ Connexion Supabase: {response.status_code}")
        
        # Test auth endpoint
        auth_url = f"{settings.SUPABASE_URL}/auth/v1/settings"
        response = requests.get(auth_url, headers=headers, timeout=5)
        print(f"✅ Supabase Auth: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Connexion Supabase: {e}")

if __name__ == "__main__":
    try:
        test_supabase_config()
        test_jwt_verification() 
        test_backend_endpoints()
        test_supabase_connection()
        
        print("\n=== RÉSUMÉ ===")
        print("✅ Tests terminés. Vérifiez les erreurs ci-dessus.")
        print("🔧 Si des endpoints backend échouent, le serveur Django n'est peut-être pas démarré.")
        print("🔧 Si la connexion Supabase échoue, vérifiez vos clés dans .env")
        
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        sys.exit(1)