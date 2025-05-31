#!/usr/bin/env python3
"""
Script de debug pour tester l'authentification Supabase
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings
import jwt
import json

def debug_supabase_config():
    """Debug de la configuration Supabase"""
    print("=== DEBUG CONFIGURATION SUPABASE ===")
    
    # Vérifier les variables d'environnement
    supabase_url = getattr(settings, 'SUPABASE_URL', None)
    supabase_jwt_secret = getattr(settings, 'SUPABASE_JWT_SECRET', None)
    supabase_service_key = getattr(settings, 'SUPABASE_SERVICE_ROLE_KEY', None)
    
    print(f"SUPABASE_URL: {supabase_url}")
    print(f"SUPABASE_JWT_SECRET: {'✓ configuré' if supabase_jwt_secret else '✗ manquant'}")
    print(f"SUPABASE_JWT_SECRET length: {len(supabase_jwt_secret) if supabase_jwt_secret else 0}")
    print(f"SUPABASE_SERVICE_ROLE_KEY: {'✓ configuré' if supabase_service_key else '✗ manquant'}")
    
    # Vérifier la base de données
    use_supabase_db = getattr(settings, 'USE_SUPABASE_DB', None)
    print(f"USE_SUPABASE_DB: {use_supabase_db}")
    
    # Test de création d'un token factice pour voir si la config fonctionne
    if supabase_jwt_secret:
        try:
            test_payload = {
                'sub': 'test-user-id',
                'email': 'test@example.com',
                'aud': 'authenticated',
                'iss': f'{supabase_url}/auth/v1' if supabase_url else 'test',
                'exp': 9999999999,  # Far future
                'iat': 1000000000   # Past
            }
            
            test_token = jwt.encode(test_payload, supabase_jwt_secret, algorithm='HS256')
            print(f"✓ Peut créer un token de test")
            
            # Test de décodage
            decoded = jwt.decode(
                test_token,
                supabase_jwt_secret,
                algorithms=['HS256'],
                audience='authenticated',
                issuer=f'{supabase_url}/auth/v1' if supabase_url else 'test',
                options={'verify_exp': False, 'verify_iat': False}
            )
            print(f"✓ Peut décoder le token de test")
            
        except Exception as e:
            print(f"✗ Erreur lors du test de token: {e}")
    
    print("\n=== AUTHENTIFICATION BACKENDS ===")
    auth_backends = getattr(settings, 'AUTHENTICATION_BACKENDS', [])
    for backend in auth_backends:
        print(f"- {backend}")
    
    print("\n=== REST FRAMEWORK AUTH ===")
    drf_settings = getattr(settings, 'REST_FRAMEWORK', {})
    auth_classes = drf_settings.get('DEFAULT_AUTHENTICATION_CLASSES', [])
    for auth_class in auth_classes:
        print(f"- {auth_class}")

if __name__ == '__main__':
    debug_supabase_config()