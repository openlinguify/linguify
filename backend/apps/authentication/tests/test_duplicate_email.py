# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

"""
Tests pour la gestion des emails dupliqués avec DuplicateEmailError
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from ..models.models import DuplicateEmailError
from ..forms.auth_forms import RegisterForm

User = get_user_model()


class DuplicateEmailErrorTest(TestCase):
    """Test de la classe DuplicateEmailError"""

    def test_duplicate_email_error_creation(self):
        """Test que l'erreur est créée avec les bons attributs"""
        email = "test@example.com"
        message = "Email already exists"

        error = DuplicateEmailError(message=message, email=email)

        self.assertEqual(error.message, message)
        self.assertEqual(error.email, email)
        self.assertEqual(str(error), message)


class DuplicateEmailRegistrationTest(TestCase):
    """Test de l'inscription avec email dupliqué"""

    def setUp(self):
        self.client = Client()

        # Créer un utilisateur existant
        self.existing_user = User.objects.create_user(
            username='existing_user',
            email='existing@example.com',
            password='TestPass123!'
        )

    def test_form_duplicate_email_validation(self):
        """Test que le formulaire détecte les emails dupliqués"""
        form_data = {
            'first_name': 'New',
            'last_name': 'User',
            'username': 'newuser',
            'email': 'existing@example.com',  # Email déjà existant
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'birthday': '1990-01-01',
            'gender': 'M',
            'interface_language': 'en',
            'terms': True
        }

        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('already exists', str(form.errors['email']))

    def test_user_manager_duplicate_email_error(self):
        """Test que UserManager lève DuplicateEmailError"""
        with self.assertRaises(DuplicateEmailError) as context:
            User.objects.create_user(
                username='another_user',
                email='existing@example.com',  # Email déjà existant
                password='TestPass123!'
            )

        error = context.exception
        self.assertEqual(error.email, 'existing@example.com')
        self.assertIn('already registered', error.message)


    def test_case_insensitive_email_duplicate_detection(self):
        """Test que la détection d'emails dupliqués est insensible à la casse"""
        form_data = {
            'first_name': 'New',
            'last_name': 'User',
            'username': 'newuser2',
            'email': 'EXISTING@EXAMPLE.COM',  # Même email en majuscules
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'birthday': '1990-01-01',
            'gender': 'M',
            'interface_language': 'en',
            'terms': True
        }

        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class DuplicateEmailAuditTest(TestCase):
    """Test de l'audit des tentatives d'inscription avec email dupliqué"""

    def setUp(self):
        self.client = Client()

        # Créer un utilisateur existant
        User.objects.create_user(
            username='existing_user',
            email='audit@example.com',
            password='TestPass123!'
        )

    def test_duplicate_email_logging(self):
        """Test que les tentatives avec email dupliqué génèrent un log warning"""
        import logging
        from unittest.mock import patch, MagicMock

        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'testuser',
            'email': 'audit@example.com',  # Email déjà existant
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'birthday': '1990-01-01',
            'gender': 'M',
            'interface_language': 'en',
            'terms': True
        }

        # Mock le logger
        with patch('apps.authentication.forms.auth_forms.logging.getLogger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            # Tester le formulaire avec email dupliqué
            form = RegisterForm(data=form_data)
            self.assertFalse(form.is_valid())

            # Vérifier que warning a été appelé
            mock_logger.warning.assert_called_once()
            call_args = mock_logger.warning.call_args[0][0]
            self.assertIn('duplicate email', call_args.lower())
            self.assertIn('audit@example.com', call_args)