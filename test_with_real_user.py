#!/usr/bin/env python3
"""
Test avec l'utilisateur réel de votre dashboard Supabase
"""
import requests
import json

SUPABASE_URL = "https://bfsxhrpyotstyhddkvrf.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJmc3hocnB5b3RzdHloZGRrdnJmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg5MTAzODgsImV4cCI6MjA2NDQ4NjM4OH0.cXQKzrqcSKA8KzUtbP9QG21i1_e8soq3_9gnCt-X6_c"

def test_login(email, password):
    """Test de connexion avec email/password spécifiques"""
    print(f"🧪 Test connexion avec: {email}")
    
    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Content-Type': 'application/json'
    }
    data = {
        'email': email,
        'password': password
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ CONNEXION RÉUSSIE !")
            print(f"User ID: {result.get('user', {}).get('id')}")
            print(f"Email: {result.get('user', {}).get('email')}")
            print(f"Access Token: {result.get('access_token', '')[:50]}...")
            return True
        else:
            print(f"❌ Échec: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("🎯 TEST AVEC UTILISATEUR RÉEL")
    print("=" * 40)
    
    # REMPLACEZ CES VALEURS PAR L'UTILISATEUR DE VOTRE DASHBOARD
    real_email = input("Email de votre utilisateur Supabase: ")
    real_password = input("Mot de passe: ")
    
    if test_login(real_email, real_password):
        print("\n🎉 L'authentification Supabase fonctionne !")
        print("Vous pouvez maintenant tester votre frontend.")
    else:
        print("\n🔧 Vérifiez :")
        print("1. L'email est exact (vérifiez dans le dashboard)")
        print("2. Le mot de passe est correct")
        print("3. L'utilisateur est confirmé (Email confirm ✅)")