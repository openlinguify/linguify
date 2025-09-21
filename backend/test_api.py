#!/usr/bin/env python
"""
Script de test pour l'API des modules d'unités
"""
import os
import sys
import django

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
os.environ.setdefault('DJANGO_ENV', 'development')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from apps.language_learning.models import CourseUnit, CourseModule

def test_api():
    # Créer un client de test
    client = Client()

    # Récupérer l'utilisateur
    User = get_user_model()
    user = User.objects.get(email='lplalou3@gmail.com')

    # Se connecter
    client.force_login(user)

    # Tester l'API
    unit_id = 15
    url = f'/language_learning/api/units/{unit_id}/modules/'

    print(f"🧪 Test de l'API: {url}")

    # Faire la requête avec un host valide
    response = client.get(url, HTTP_HOST='localhost:8000')

    print(f"📊 Status: {response.status_code}")
    print(f"📋 Content-Type: {response.get('Content-Type', 'N/A')}")

    if response.status_code == 200:
        print("✅ API fonctionne!")
        try:
            import json
            data = response.json()
            print(f"📦 Données retournées: {json.dumps(data, indent=2)}")
        except Exception as e:
            print(f"❌ Erreur parsing JSON: {e}")
            print(f"📄 Contenu brut: {response.content[:500]}")
    else:
        print(f"❌ Erreur API: {response.status_code}")
        print(f"📄 Contenu: {response.content[:500]}")

    # Vérifier les données en base
    print(f"\n🔍 Vérification en base:")
    unit = CourseUnit.objects.get(id=unit_id)
    modules = CourseModule.objects.filter(unit=unit).order_by('module_number')
    print(f"📚 Unité: {unit.title}")
    print(f"📖 Modules trouvés: {modules.count()}")
    for module in modules:
        print(f"   - {module.id}: {module.title}")

if __name__ == '__main__':
    test_api()