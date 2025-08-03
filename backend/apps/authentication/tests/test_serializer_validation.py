#!/usr/bin/env python
"""
Test case-insensitive username validation in ProfileUpdateSerializer
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.authentication.serializers.settings_serializers import ProfileUpdateSerializer

User = get_user_model()


class ProfileUpdateSerializerTest(TestCase):
    """Test ProfileUpdateSerializer validation"""
    
    def setUp(self):
        """Set up test user"""
        self.test_user = User.objects.create_user(
            username='DarkVador',
            email='darkvador@empire.com',
            password='testpass123'
        )
        
    def test_case_insensitive_username_validation(self):
        """Test that username validation is case-insensitive"""
        print("🧪 Test de validation username case-insensitive dans ProfileUpdateSerializer")
        print("=" * 60)
        
        print(f"✅ Utilisateur trouvé: {self.test_user.username}")
        
        # Test validation with existing username in different cases
        serializer = ProfileUpdateSerializer(instance=self.test_user)
        
        # This should pass since it's the same user
        data = {'username': 'DarkVador'}
        serializer_same = ProfileUpdateSerializer(instance=self.test_user, data=data)
        self.assertTrue(serializer_same.is_valid())
        
        # Create another user to test conflict
        other_user = User.objects.create_user(
            username='TestUser',
            email='test@test.com', 
            password='testpass123'
        )
        
        # This should fail - trying to use existing username with different case
        data_conflict = {'username': 'testuser'}  # lowercase version of TestUser
        serializer_conflict = ProfileUpdateSerializer(instance=self.test_user, data=data_conflict)
        self.assertFalse(serializer_conflict.is_valid())
        print("✅ Case-insensitive validation working correctly")
        
    def test_username_conflict_with_existing_admin(self):
        """Test that changing username to existing 'admin' fails"""
        # Create admin user
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123'
        )
        
        print("\n📝 Test: Essayer de changer 'DarkVador' en 'admin' (devrait échouer)")
        
        serializer = ProfileUpdateSerializer(
            instance=self.test_user,
            data={'username': 'admin'},
            partial=True
        )
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)
        print("✅ Validation échouée comme prévu:")
        print(f"   Erreur: {serializer.errors}")
        
    def test_username_case_variations(self):
        """Test username validation with different case variations"""
        # Create admin user
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123'
        )
        
        test_cases = ['Admin', 'ADMIN', 'aDmIn']
        
        for test_username in test_cases:
            with self.subTest(username=test_username):
                print(f"\n📝 Test: Essayer de changer en '{test_username}'")
                serializer = ProfileUpdateSerializer(
                    instance=self.test_user,
                    data={'username': test_username},
                    partial=True
                )
                
                self.assertFalse(serializer.is_valid())
                self.assertIn('username', serializer.errors)
                print("✅ Validation échouée comme prévu:")
                print(f"   Erreur: {serializer.errors.get('username', ['Erreur inconnue'])[0]}")
        
        print("\n✅ Tests terminés!")