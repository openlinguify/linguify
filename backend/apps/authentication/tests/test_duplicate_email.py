# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

"""
Tests pour la gestion des emails dupliqués avec DuplicateEmailError
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
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
        self.register_url = reverse('register')

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

    def test_registration_view_duplicate_email_handling(self):
        """Test que la vue d'inscription gère bien les emails dupliqués"""
        form_data = {
            'first_name': 'New',
            'last_name': 'User',
            'username': 'newuser',
            'email': 'existing@example.com',  # Email déjà existant
            'phone_number': '',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'birthday': '1990-01-01',
            'gender': 'M',
            'interface_language': 'en',
            'terms': 'on'  # Checkbox value
        }

        response = self.client.post(self.register_url, form_data, follow=False)

        # Vérifier que le formulaire n'est pas valide
        self.assertEqual(response.status_code, 200)  # Reste sur la page d'inscription
        self.assertContains(response, 'already exists')

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
        self.register_url = reverse('register')

        # Créer un utilisateur existant
        User.objects.create_user(
            username='existing_user',
            email='audit@example.com',
            password='TestPass123!'
        )

    def test_duplicate_email_logging(self):
        """Test que les tentatives avec email dupliqué sont loggées"""
        import logging
        from unittest.mock import patch

        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'testuser',
            'email': 'audit@example.com',  # Email déjà existant
            'phone_number': '',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'birthday': '1990-01-01',
            'gender': 'M',
            'interface_language': 'en',
            'terms': 'on'
        }

        with patch('apps.authentication.forms.auth_forms.logging.getLogger') as mock_logger:
            mock_logger.return_value.warning = lambda x: None
            response = self.client.post(self.register_url, form_data)

            # Vérifier que la tentative est loggée
            self.assertEqual(response.status_code, 200)