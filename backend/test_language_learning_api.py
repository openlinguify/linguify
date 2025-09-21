#!/usr/bin/env python
"""
Script de test pour l'API Language Learning
"""
import os
import django
import json

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
os.environ.setdefault('DJANGO_ENV', 'development')
django.setup()

from django.test.client import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

def test_api_endpoints():
    """Test des endpoints API Language Learning"""
    print("🧪 Test de l'API Language Learning DRF")
    print("=" * 50)

    # Créer un client de test avec le bon host
    client = Client(SERVER_NAME='localhost:8000')

    # Essayer de récupérer ou créer un utilisateur de test
    try:
        user = User.objects.get(email='lplalou3@gmail.com')
        print(f"✅ Utilisateur trouvé: {user.username}")
    except User.DoesNotExist:
        print("❌ Utilisateur de test non trouvé")
        return

    # Se connecter avec l'utilisateur
    client.force_login(user)
    print(f"🔐 Connecté en tant que: {user.username}")

    # Test des endpoints
    endpoints = [
        ('/language_learning/api/', 'API Root'),
        ('/language_learning/api/languages/', 'Languages List'),
        ('/language_learning/api/course-units/', 'Course Units'),
        ('/language_learning/api/user-progress/', 'User Progress'),
        ('/language_learning/api/learning-interface/', 'Learning Interface'),
    ]

    print("\n📡 Test des endpoints:")
    print("-" * 30)

    for endpoint, name in endpoints:
        try:
            response = client.get(endpoint, HTTP_ACCEPT='application/json')
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {name}: {response.status_code}")

            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict) and 'results' in data:
                        print(f"   📊 Résultats: {len(data['results'])} éléments")
                    elif isinstance(data, list):
                        print(f"   📊 Résultats: {len(data)} éléments")
                    elif isinstance(data, dict):
                        print(f"   📊 Clés: {list(data.keys())}")
                except:
                    print(f"   ⚠️  Réponse non-JSON")

        except Exception as e:
            print(f"❌ {name}: Erreur - {str(e)}")

    print("\n" + "=" * 50)
    print("🎯 Test terminé")

if __name__ == '__main__':
    test_api_endpoints()