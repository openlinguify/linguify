#!/usr/bin/env python
"""
Test complet pour l'enregistrement d'utilisateurs
Tests de validation, création, et intégration avec UserLearningProfile
"""

from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from datetime import date
from apps.authentication.forms.auth_forms import RegisterForm
from django.conf import settings
try:
    from apps.language_learning.models import UserLearningProfile, LANGUAGE_CHOICES
    HAS_LANGUAGE_LEARNING = True
except ImportError:
    HAS_LANGUAGE_LEARNING = False

User = get_user_model()


class RegisterFormTest(TestCase):
    """Tests complets pour RegisterForm"""

    def setUp(self):
        """Configuration initiale pour les tests"""
        self.valid_form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'strongpassword123',
            'password2': 'strongpassword123',
            'birthday': date(1990, 1, 1),
            'gender': 'M',
            'interface_language': 'en',
            'terms': True
        }

    def test_form_fields_present(self):
        """Test que tous les champs requis sont présents dans le formulaire"""
        form = RegisterForm()
        expected_fields = [
            'username', 'email', 'first_name', 'last_name',
            'password1', 'password2', 'birthday', 'gender',
            'interface_language', 'phone_number', 'terms'
        ]

        for field in expected_fields:
            self.assertIn(field, form.fields, f"Le champ '{field}' devrait être présent dans le formulaire")

        print(f"✅ Tous les champs requis sont présents: {len(expected_fields)} champs")

    def test_interface_language_choices(self):
        """Test que les choix de langue d'interface sont corrects"""
        form = RegisterForm()
        interface_choices = form.fields['interface_language'].choices
        expected_choices = settings.LANGUAGES

        self.assertEqual(interface_choices, expected_choices)
        print(f"✅ Choix de langue d'interface corrects: {len(expected_choices)} langues disponibles")

    def test_valid_form_data(self):
        """Test avec des données valides"""
        form = RegisterForm(data=self.valid_form_data)
        self.assertTrue(form.is_valid(), f"Le formulaire devrait être valide. Erreurs: {form.errors}")
        print("✅ Formulaire avec données valides accepté")

    def test_missing_required_fields(self):
        """Test validation avec champs obligatoires manquants"""
        required_fields = ['username', 'email', 'first_name', 'last_name',
                         'password1', 'password2', 'birthday', 'gender', 'terms']

        for field in required_fields:
            with self.subTest(missing_field=field):
                incomplete_data = self.valid_form_data.copy()
                del incomplete_data[field]

                form = RegisterForm(data=incomplete_data)
                self.assertFalse(form.is_valid(), f"Le formulaire devrait être invalide sans '{field}'")
                self.assertIn(field, form.errors, f"Une erreur devrait être présente pour le champ '{field}'")

        print(f"✅ Validation des champs obligatoires fonctionne pour {len(required_fields)} champs")

    def test_password_mismatch(self):
        """Test validation avec mots de passe différents"""
        data = self.valid_form_data.copy()
        data['password2'] = 'differentpassword'

        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
        print("✅ Validation des mots de passe différents fonctionne")

    def test_weak_password(self):
        """Test validation avec mot de passe faible"""
        weak_passwords = ['123', 'password', 'abc', '12345678']

        for weak_password in weak_passwords:
            with self.subTest(password=weak_password):
                data = self.valid_form_data.copy()
                data['password1'] = weak_password
                data['password2'] = weak_password

                form = RegisterForm(data=data)
                self.assertFalse(form.is_valid(), f"Le mot de passe '{weak_password}' devrait être rejeté")

        print(f"✅ Validation des mots de passe faibles fonctionne pour {len(weak_passwords)} cas testés")

    def test_email_validation(self):
        """Test validation des adresses email"""
        invalid_emails = ['invalid', 'test@', '@domain.com', 'test..test@domain.com']

        for invalid_email in invalid_emails:
            with self.subTest(email=invalid_email):
                data = self.valid_form_data.copy()
                data['email'] = invalid_email

                form = RegisterForm(data=data)
                self.assertFalse(form.is_valid(), f"L'email '{invalid_email}' devrait être rejeté")
                self.assertIn('email', form.errors)

        print(f"✅ Validation des emails invalides fonctionne pour {len(invalid_emails)} cas testés")

    def test_username_validation(self):
        """Test validation des noms d'utilisateur"""
        invalid_usernames = ['', 'a', 'a' * 151, 'user@name', 'user name']

        for invalid_username in invalid_usernames:
            with self.subTest(username=invalid_username):
                data = self.valid_form_data.copy()
                data['username'] = invalid_username

                form = RegisterForm(data=data)
                self.assertFalse(form.is_valid(), f"Le nom d'utilisateur '{invalid_username}' devrait être rejeté")

        print(f"✅ Validation des noms d'utilisateur invalides fonctionne pour {len(invalid_usernames)} cas testés")

    def test_terms_acceptance_required(self):
        """Test que l'acceptation des termes est obligatoire"""
        # Test sans le champ terms
        data = self.valid_form_data.copy()
        data['terms'] = False

        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())
        print("✅ Validation de l'acceptation des termes (False) fonctionne")

        # Test en supprimant complètement le champ
        data = self.valid_form_data.copy()
        del data['terms']

        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())
        print("✅ Validation de l'acceptation des termes (manquant) fonctionne")

    def test_interface_language_default(self):
        """Test que la langue d'interface par défaut est correcte"""
        form = RegisterForm()
        default_language = form.fields['interface_language'].initial
        self.assertEqual(default_language, 'en')
        print(f"✅ Langue d'interface par défaut correcte: {default_language}")


class UserCreationTest(TransactionTestCase):
    """Tests pour la création d'utilisateurs et l'intégration avec UserLearningProfile"""

    def setUp(self):
        """Configuration initiale"""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        self.valid_form_data = {
            'username': f'newuser{unique_id}',
            'email': f'newuser{unique_id}@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'strongpassword123',
            'password2': 'strongpassword123',
            'birthday': date(1995, 5, 15),
            'gender': 'F',
            'interface_language': 'fr',
            'terms': True
        }

    def test_user_creation_success(self):
        """Test création d'utilisateur réussie"""
        form = RegisterForm(data=self.valid_form_data)
        self.assertTrue(form.is_valid(), f"Le formulaire devrait être valide. Erreurs: {form.errors}")

        user = form.save()

        # Vérifier que l'utilisateur a été créé
        self.assertIsNotNone(user.id)
        self.assertTrue(user.username.startswith('newuser'))
        self.assertTrue(user.email.startswith('newuser'))
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'User')
        self.assertEqual(user.interface_language, 'fr')
        self.assertFalse(user.is_active)  # Utilisateur inactif jusqu'à vérification email

        print(f"✅ Utilisateur créé avec succès: {user.username} (ID: {user.id})")

    def test_user_password_encrypted(self):
        """Test que le mot de passe est bien chiffré"""
        form = RegisterForm(data=self.valid_form_data)
        self.assertTrue(form.is_valid())

        user = form.save()

        # Le mot de passe ne devrait pas être stocké en clair
        self.assertNotEqual(user.password, 'strongpassword123')
        self.assertTrue(user.check_password('strongpassword123'))

        print("✅ Mot de passe correctement chiffré")

    def test_duplicate_username_prevention(self):
        """Test prévention des noms d'utilisateur en double"""
        import uuid
        unique_id = str(uuid.uuid4())[:8]

        # Créer le premier utilisateur
        User.objects.create_user(
            username=f'existinguser{unique_id}',
            email=f'existing{unique_id}@example.com',
            password='password123'
        )

        # Tenter de créer un utilisateur avec le même nom
        data = self.valid_form_data.copy()
        data['username'] = f'existinguser{unique_id}'
        data['email'] = f'different{unique_id}@example.com'

        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

        print("✅ Prévention des noms d'utilisateur en double fonctionne")

    def test_duplicate_email_prevention(self):
        """Test prévention des emails en double"""
        import uuid
        unique_id = str(uuid.uuid4())[:8]

        # Créer le premier utilisateur
        User.objects.create_user(
            username=f'user1{unique_id}',
            email=f'duplicate{unique_id}@example.com',
            password='password123'
        )

        # Tenter de créer un utilisateur avec le même email
        data = self.valid_form_data.copy()
        data['username'] = f'differentuser{unique_id}'
        data['email'] = f'duplicate{unique_id}@example.com'

        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

        print("✅ Prévention des emails en double fonctionne")

    def test_user_learning_profile_creation(self):
        """Test création automatique du profil d'apprentissage via signal"""
        if not HAS_LANGUAGE_LEARNING:
            self.skipTest("Module language_learning non disponible")

        form = RegisterForm(data=self.valid_form_data)
        self.assertTrue(form.is_valid())

        user = form.save()

        # Vérifier que le UserLearningProfile a été créé automatiquement
        try:
            learning_profile = user.learning_profile
            self.assertIsNotNone(learning_profile)
            self.assertEqual(learning_profile.user, user)
            self.assertIn(learning_profile.native_language, [choice[0] for choice in LANGUAGE_CHOICES])
            self.assertIn(learning_profile.target_language, [choice[0] for choice in LANGUAGE_CHOICES])

            print(f"✅ Profil d'apprentissage créé automatiquement:")
            print(f"   - Langue native: {learning_profile.native_language}")
            print(f"   - Langue cible: {learning_profile.target_language}")

        except AttributeError:
            self.fail("UserLearningProfile n'a pas été créé automatiquement")

    def test_terms_acceptance_recorded(self):
        """Test que l'acceptation des termes est enregistrée"""
        form = RegisterForm(data=self.valid_form_data)
        self.assertTrue(form.is_valid())

        user = form.save()

        self.assertTrue(user.terms_accepted)
        self.assertIsNotNone(user.terms_accepted_at)
        self.assertIsNotNone(user.terms_version)

        print("✅ Acceptation des termes correctement enregistrée")

    def test_user_defaults(self):
        """Test que les valeurs par défaut sont correctement définies"""
        form = RegisterForm(data=self.valid_form_data)
        self.assertTrue(form.is_valid())

        user = form.save()

        # Vérifier les valeurs par défaut
        self.assertFalse(user.is_active)  # Utilisateur inactif jusqu'à vérification
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_coach)
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.public_id)

        print("✅ Valeurs par défaut correctement définies")


class RegisterFormIntegrationTest(TransactionTestCase):
    """Tests d'intégration pour RegisterForm"""

    def test_complete_registration_flow(self):
        """Test du flux complet d'enregistrement"""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        initial_user_count = User.objects.count()

        form_data = {
            'username': f'integrationtest{unique_id}',
            'email': f'integration{unique_id}@test.com',
            'first_name': 'Integration',
            'last_name': 'Test',
            'password1': 'veryStrongPassword123!',
            'password2': 'veryStrongPassword123!',
            'birthday': date(1988, 12, 25),
            'gender': 'O',  # Autre
            'interface_language': 'es',  # Espagnol
            'terms': True
        }

        # 1. Créer et valider le formulaire
        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Formulaire invalide: {form.errors}")
        print("✅ Étape 1: Formulaire validé")

        # 2. Sauvegarder l'utilisateur
        user = form.save()
        self.assertIsNotNone(user)
        print(f"✅ Étape 2: Utilisateur créé (ID: {user.id})")

        # 3. Vérifier l'incrémentation du nombre d'utilisateurs
        self.assertEqual(User.objects.count(), initial_user_count + 1)
        print("✅ Étape 3: Nombre d'utilisateurs incrémenté")

        # 4. Vérifier toutes les propriétés de l'utilisateur
        saved_user = User.objects.get(id=user.id)
        self.assertEqual(saved_user.username, f'integrationtest{unique_id}')
        self.assertEqual(saved_user.email, f'integration{unique_id}@test.com')
        self.assertEqual(saved_user.interface_language, 'es')
        self.assertEqual(saved_user.gender, 'O')
        print("✅ Étape 4: Propriétés utilisateur vérifiées")

        # 5. Vérifier la création du profil d'apprentissage (si disponible)
        if HAS_LANGUAGE_LEARNING:
            try:
                learning_profile = saved_user.learning_profile
                self.assertIsNotNone(learning_profile)
                print("✅ Étape 5: Profil d'apprentissage créé")
            except AttributeError:
                print("⚠️  Étape 5: Profil d'apprentissage non créé automatiquement")

        print("🎉 Test d'intégration complet réussi!")


if __name__ == '__main__':
    import unittest
    unittest.main()