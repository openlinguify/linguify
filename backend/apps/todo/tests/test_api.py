#!/usr/bin/env python
"""
Test direct de l'API Todo Settings
"""

import os
import django
import requests

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client

def test_api():
    print("🧪 Test de l'API Todo Settings")
    print("=" * 50)
    
    # Créer un client de test
    client = Client()
    
    # Récupérer un utilisateur
    User = get_user_model()
    user = User.objects.first()
    
    # Se connecter
    client.force_login(user)
    print(f"👤 Connecté en tant que: {user.username}")
    
    # Tester GET
    print("\n🔍 Test GET /api/v1/todo/settings/")
    response = client.get('/api/v1/todo/settings/')
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        import json
        data = response.json()
        print("✅ GET réussi!")
        print("Settings récupérées:")
        print(f"  auto_archive_completed: {data.get('auto_archive_completed')}")
        print(f"  auto_archive_days: {data.get('auto_archive_days')}")
        print(f"  auto_delete_archived: {data.get('auto_delete_archived')}")
        print(f"  auto_delete_archive_days: {data.get('auto_delete_archive_days')}")
        
        # Tester POST
        print("\n📝 Test POST /api/v1/todo/settings/")
        test_data = {
            'auto_archive_completed': True,
            'auto_archive_days': 15,
            'auto_delete_archived': False,
            'auto_delete_archive_days': 45,
        }
        
        response = client.post('/api/v1/todo/settings/', 
                              data=json.dumps(test_data),
                              content_type='application/json')
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ POST réussi!")
            result = response.json()
            print(f"Message: {result.get('message')}")
        else:
            print("❌ POST échoué")
            print(f"Error: {response.content.decode()}")
            
    else:
        print("❌ GET échoué")
        print(f"Error: {response.content.decode()}")

if __name__ == "__main__":
    test_api()