#!/usr/bin/env python
"""
Script pour tester l'endpoint /api/auth/profile/ et vérifier les données retournées
"""

import os
import sys
import django
from django.test import RequestFactory

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.authentication.models import User
from apps.authentication.serializers import UserSerializer
from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import AnonymousUser

def test_user_serializer():
    """Test le UserSerializer pour vérifier les champs retournés"""
    
    # Créer un utilisateur de test
    user = User.objects.filter(is_active=True).first()
    if not user:
        print("❌ Aucun utilisateur actif trouvé dans la base de données")
        return
    
    print(f"✅ Test avec l'utilisateur: {user.email}")
    print(f"   - Prénom: {user.first_name or 'Non défini'}")
    print(f"   - Nom: {user.last_name or 'Non défini'}")
    print(f"   - Username: {user.username}")
    
    # Créer une request factice
    factory = APIRequestFactory()
    request = factory.get('/api/auth/profile/')
    request.user = user
    
    # Sérialiser l'utilisateur
    serializer = UserSerializer(user, context={'request': request})
    data = serializer.data
    
    print("\n📋 Données retournées par le UserSerializer:")
    print("-" * 50)
    
    # Afficher tous les champs
    for key, value in data.items():
        if key == 'profile_picture' and value:
            print(f"   {key}: {value[:50]}..." if len(str(value)) > 50 else f"   {key}: {value}")
        else:
            print(f"   {key}: {value}")
    
    # Vérifier les champs importants
    print("\n🔍 Vérification des champs critiques:")
    print("-" * 50)
    
    critical_fields = ['name', 'first_name', 'last_name', 'email', 'username']
    for field in critical_fields:
        if field in data:
            print(f"   ✅ {field}: {data[field]}")
        else:
            print(f"   ❌ {field}: MANQUANT")
    
    # Vérifier la construction du nom complet
    if 'name' in data:
        expected_name = f"{user.first_name} {user.last_name}".strip() or user.username or user.email
        if data['name'] == expected_name:
            print(f"\n✅ Le champ 'name' est correctement construit: '{data['name']}'")
        else:
            print(f"\n❌ Le champ 'name' ne correspond pas:")
            print(f"   Attendu: '{expected_name}'")
            print(f"   Obtenu: '{data['name']}'")

def test_multiple_users():
    """Test avec plusieurs utilisateurs pour vérifier la cohérence"""
    print("\n\n📊 Test avec plusieurs utilisateurs:")
    print("=" * 70)
    
    users = User.objects.filter(is_active=True)[:5]
    
    for i, user in enumerate(users, 1):
        serializer = UserSerializer(user)
        data = serializer.data
        
        print(f"\n{i}. {user.email}")
        print(f"   - first_name: '{user.first_name}'")
        print(f"   - last_name: '{user.last_name}'")
        print(f"   - name (calculé): '{data.get('name', 'MANQUANT')}'")

if __name__ == "__main__":
    print("🧪 Test du UserSerializer pour l'endpoint /api/auth/profile/")
    print("=" * 70)
    
    test_user_serializer()
    test_multiple_users()
    
    print("\n\n✅ Test terminé!")