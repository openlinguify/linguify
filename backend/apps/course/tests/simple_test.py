#!/usr/bin/env python3

import os
import django
import requests

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.course.models import Unit
from django.contrib.auth import get_user_model

User = get_user_model()

def test_data():
    """Vérifier les données"""
    print("🔍 Vérification des données...")
    
    # Vérifier les units
    units_count = Unit.objects.count()
    print(f"   📚 Nombre d'units: {units_count}")
    
    units = Unit.objects.all()
    for unit in units:
        print(f"   📖 Unit {unit.id}: {unit.title_en} - Prix: €{unit.price} - Gratuit: {unit.is_free}")
    
    # Vérifier les utilisateurs
    users_count = User.objects.count()
    print(f"   👥 Nombre d'utilisateurs: {users_count}")
    
    if users_count > 0:
        user = User.objects.first()
        print(f"   👤 Premier utilisateur: {user.username}")
    
    return units_count > 0 and users_count > 0

def test_api_with_curl():
    """Test avec curl-like approach"""
    print("\n🌐 Test de l'API...")
    
    # Test direct de l'endpoint sans authentification d'abord
    try:
        response = requests.get('http://127.0.0.1:8000/api/v1/course/units/', timeout=5)
        print(f"   📡 Status Code: {response.status_code}")
        print(f"   📄 Content Type: {response.headers.get('content-type', 'Unknown')}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   📊 Units retournées: {len(data)}")
            if data:
                print(f"   📝 Premier unit: {data[0].get('title_en', 'N/A')}")
        elif response.status_code == 401:
            print("   🔐 Authentification requise")
        elif response.status_code == 500:
            print("   ❌ Erreur serveur 500")
            print(f"   📄 Réponse: {response.text[:200]}")
        else:
            print(f"   ⚠️  Code inattendu: {response.status_code}")
            print(f"   📄 Réponse: {response.text[:200]}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Impossible de se connecter au serveur")
        print("   💡 Assurez-vous que le serveur Django tourne sur port 8000")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")

if __name__ == "__main__":
    print("🚀 Test simple des données et API")
    print("=" * 40)
    
    data_ok = test_data()
    if data_ok:
        print("✅ Données OK")
        test_api_with_curl()
    else:
        print("❌ Problème avec les données")
    
    print("\n" + "=" * 40)
    print("💡 Pour tester manuellement:")
    print("   curl http://127.0.0.1:8000/api/v1/course/units/")
    print("   ou visitez: http://127.0.0.1:8000/learning/?tab=my-learning")