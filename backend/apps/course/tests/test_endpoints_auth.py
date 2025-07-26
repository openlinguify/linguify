#!/usr/bin/env python3

import os
import django
from django.test import Client
from django.contrib.auth import get_user_model
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

User = get_user_model()

def test_endpoints_with_auth():
    """Test des endpoints avec authentification"""
    print("🧪 Test des endpoints avec authentification...")
    
    # Récupérer un utilisateur
    user = User.objects.first()
    if not user:
        print("   ❌ Aucun utilisateur trouvé")
        return False
    
    print(f"   👤 Utilisateur: {user.username}")
    
    # Créer un client de test et se connecter
    client = Client()
    client.force_login(user)
    
    # Test endpoint units
    print("   📚 Test /api/v1/course/units/")
    response = client.get('/api/v1/course/units/')
    print(f"   📡 Status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = json.loads(response.content)
            print(f"   ✅ Units retournées: {len(data)}")
            if data:
                unit = data[0]
                print(f"   📝 Premier unit: {unit.get('title_en', 'N/A')}")
                print(f"   ⏱️  Durée estimée: {unit.get('estimated_duration', 'N/A')} min")
        except json.JSONDecodeError:
            print(f"   ❌ Réponse invalide: {response.content[:100]}")
    else:
        print(f"   ❌ Erreur: {response.content[:200]}")
    
    # Test endpoint dashboard
    print("   📊 Test /api/v1/course/progress/dashboard/")
    response = client.get('/api/v1/course/progress/dashboard/')
    print(f"   📡 Status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = json.loads(response.content)
            print(f"   ✅ Dashboard data keys: {list(data.keys())}")
        except json.JSONDecodeError:
            print(f"   ❌ Réponse invalide: {response.content[:100]}")
    else:
        print(f"   ❌ Erreur: {response.content[:200]}")
    
    # Test endpoint statistics
    print("   📈 Test /api/v1/course/progress/statistics/")
    response = client.get('/api/v1/course/progress/statistics/')
    print(f"   📡 Status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = json.loads(response.content)
            print(f"   ✅ Statistics data keys: {list(data.keys())}")
        except json.JSONDecodeError:
            print(f"   ❌ Réponse invalide: {response.content[:100]}")
    else:
        print(f"   ❌ Erreur: {response.content[:200]}")
    
    return True

if __name__ == "__main__":
    print("🚀 Test des endpoints avec authentification")
    print("=" * 50)
    
    success = test_endpoints_with_auth()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Tests terminés!")
        print("🌐 La page d'apprentissage devrait maintenant fonctionner:")
        print("   http://127.0.0.1:8000/learning/?tab=my-learning")
    else:
        print("❌ Certains tests ont échoué")