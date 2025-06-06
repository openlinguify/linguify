#!/usr/bin/env python3
"""
Test direct de l'authentification Supabase
"""
import requests
import json

# Configuration Supabase (remplacez par vos vraies valeurs)
SUPABASE_URL = "https://bfsxhrpyotstyhddkvrf.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJmc3hocnB5b3RzdHloZGRrdnJmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg5MTAzODgsImV4cCI6MjA2NDQ4NjM4OH0.cXQKzrqcSKA8KzUtbP9QG21i1_e8soq3_9gnCt-X6_c"

def test_supabase_signup():
    """Teste l'inscription directe avec Supabase"""
    print("=== TEST INSCRIPTION SUPABASE ===")
    
    url = f"{SUPABASE_URL}/auth/v1/signup"
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Content-Type': 'application/json'
    }
    data = {
        'email': 'test@linguify.dev',
        'password': 'Test123456',
        'data': {
            'first_name': 'Test',
            'last_name': 'User'
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erreur inscription: {response.text}")
            return None
            
    except Exception as e:
        print(f"Erreur: {e}")
        return None

def test_supabase_login():
    """Teste la connexion directe avec Supabase"""
    print("\n=== TEST CONNEXION SUPABASE ===")
    
    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Content-Type': 'application/json'
    }
    data = {
        'email': 'test@linguify.dev',
        'password': 'Test123456'
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erreur connexion: {response.text}")
            return None
            
    except Exception as e:
        print(f"Erreur: {e}")
        return None

def test_with_existing_user():
    """Teste avec l'utilisateur existant"""
    print("\n=== TEST AVEC UTILISATEUR EXISTANT ===")
    print("Entrez les credentials de votre utilisateur existant :")
    
    # Pour ce test, nous utiliserons des credentials par défaut
    # Dans un vrai test, vous devriez utiliser l'utilisateur visible dans votre dashboard
    
    test_emails = [
        'test@linguify.dev',
        'admin@linguify.dev', 
        'user@linguify.dev'
    ]
    
    for email in test_emails:
        print(f"\nTeste avec email: {email}")
        url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
        headers = {
            'apikey': SUPABASE_ANON_KEY,
            'Content-Type': 'application/json'
        }
        data = {
            'email': email,
            'password': 'Test123456'
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ Connexion réussie !")
                print(f"  User ID: {result.get('user', {}).get('id')}")
                print(f"  Email: {result.get('user', {}).get('email')}")
                return result
            else:
                print(f"  ❌ Échec: {response.text}")
                
        except Exception as e:
            print(f"  ❌ Erreur: {e}")
    
    return None

if __name__ == "__main__":
    print("🧪 TEST AUTHENTIFICATION SUPABASE DIRECTE")
    print("=" * 50)
    
    # 1. Essayer de créer un utilisateur de test
    signup_result = test_supabase_signup()
    
    # 2. Essayer de se connecter avec l'utilisateur de test
    login_result = test_supabase_login()
    
    # 3. Essayer avec l'utilisateur existant
    if not login_result:
        existing_result = test_with_existing_user()
    
    print("\n" + "=" * 50)
    print("🎯 RÉSULTATS :")
    print("- Si l'inscription fonctionne : L'utilisateur de test est créé")
    print("- Si la connexion fonctionne : L'authentification Supabase est OK") 
    print("- Si tout échoue : Il faut vérifier la configuration Supabase")
    print("\n💡 PROCHAINES ÉTAPES :")
    print("1. Créer un utilisateur dans le dashboard Supabase")
    print("2. Tester avec ce script")
    print("3. Une fois que ça marche, tester via votre frontend")