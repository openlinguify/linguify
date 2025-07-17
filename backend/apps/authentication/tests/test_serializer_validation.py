#!/usr/bin/env python
"""
Test simple pour vérifier la validation case-insensitive dans ProfileUpdateSerializer
"""

# Ce script doit être exécuté dans l'environnement Django avec:
# python manage.py shell < test_serializer_validation.py

from django.contrib.auth import get_user_model
from apps.authentication.serializers.settings_serializers import ProfileUpdateSerializer

User = get_user_model()

print("🧪 Test de validation username case-insensitive dans ProfileUpdateSerializer")
print("=" * 60)

# Récupérer ou créer un utilisateur test
try:
    test_user = User.objects.get(username='DarkVador')
    print(f"✅ Utilisateur trouvé: {test_user.username}")
except User.DoesNotExist:
    print("❌ L'utilisateur DarkVador n'existe pas")
    exit()

# Essayer de mettre à jour avec un username existant (différente casse)
print("\n📝 Test: Essayer de changer 'DarkVador' en 'admin' (devrait échouer)")

serializer = ProfileUpdateSerializer(
    instance=test_user,
    data={'username': 'admin'},
    partial=True
)

if serializer.is_valid():
    print("❌ ERREUR: La validation devrait échouer!")
else:
    print("✅ Validation échouée comme prévu:")
    print(f"   Erreur: {serializer.errors}")

# Test avec différentes casses
test_cases = ['Admin', 'ADMIN', 'aDmIn']

for test_username in test_cases:
    print(f"\n📝 Test: Essayer de changer en '{test_username}'")
    serializer = ProfileUpdateSerializer(
        instance=test_user,
        data={'username': test_username},
        partial=True
    )
    
    if serializer.is_valid():
        print("❌ ERREUR: La validation devrait échouer!")
    else:
        print("✅ Validation échouée comme prévu:")
        print(f"   Erreur: {serializer.errors.get('username', ['Erreur inconnue'])[0]}")

print("\n✅ Tests terminés!")