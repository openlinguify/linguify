#!/usr/bin/env python3
"""
Script pour tester la configuration Supabase dans Django
"""
import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings
import jwt

def test_supabase_config():
    """Test la configuration Supabase"""
    print("=== Test Configuration Supabase ===\n")
    
    # Vérifier les variables d'environnement
    config_vars = [
        'SUPABASE_URL',
        'SUPABASE_ANON_KEY', 
        'SUPABASE_SERVICE_ROLE_KEY',
        'SUPABASE_JWT_SECRET'
    ]
    
    missing_vars = []
    for var in config_vars:
        value = getattr(settings, var, None)
        if value:
            # Masquer partiellement les clés sensibles
            if 'SECRET' in var or 'KEY' in var:
                display_value = f"{value[:10]}...{value[-4:]}" if len(value) > 14 else "***"
            else:
                display_value = value
            print(f"✓ {var}: {display_value}")
        else:
            print(f"✗ {var}: MANQUANT")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ Variables manquantes: {', '.join(missing_vars)}")
        return False
    
    print("\n✅ Toutes les variables Supabase sont configurées")
    
    # Test du JWT secret
    try:
        # Créer un token de test simple
        test_payload = {'test': True, 'exp': 9999999999}
        test_token = jwt.encode(test_payload, settings.SUPABASE_JWT_SECRET, algorithm='HS256')
        
        # Essayer de décoder
        decoded = jwt.decode(test_token, settings.SUPABASE_JWT_SECRET, algorithms=['HS256'])
        print(f"✓ JWT Secret fonctionne: {decoded}")
        
    except Exception as e:
        print(f"✗ Erreur JWT Secret: {e}")
        return False
    
    # Tester l'authentification Supabase
    try:
        from apps.authentication.supabase_auth import SupabaseAuthentication
        auth = SupabaseAuthentication()
        print("✓ SupabaseAuthentication peut être initialisé")
        
    except Exception as e:
        print(f"✗ Erreur SupabaseAuthentication: {e}")
        return False
    
    return True

def test_example_token():
    """Test avec un token d'exemple du format Supabase"""
    print("\n=== Test Token d'Exemple ===\n")
    
    try:
        from apps.authentication.supabase_auth import SupabaseAuthentication
        auth = SupabaseAuthentication()
        
        # NOTE: Ceci échouera car nous n'avons pas de vrai token
        # Mais nous pouvons voir l'erreur
        print("ℹ️  Pour tester avec un vrai token, copiez-le depuis le navigateur")
        print("   et modifiez ce script")
        
    except Exception as e:
        print(f"Note: {e}")

if __name__ == '__main__':
    success = test_supabase_config()
    test_example_token()
    
    if success:
        print("\n🎉 Configuration Supabase semble correcte!")
        print("   Si vous avez encore des erreurs 401, vérifiez:")
        print("   1. Que les URLs Supabase correspondent entre frontend et backend")
        print("   2. Que le JWT secret est correct")
        print("   3. Que l'utilisateur existe dans la base Django")
    else:
        print("\n❌ Problèmes de configuration détectés")