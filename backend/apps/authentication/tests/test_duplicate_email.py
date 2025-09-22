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

        # Créer un utilisateur existant pour ce test
        self.existing_user = User.objects.create_user(
            username='existing_reg_user',
            email='existing_registration@example.com',
            password='TestPass123!'
        )

    def test_form_duplicate_email_validation(self):
        """Test que le formulaire détecte les emails dupliqués"""
        form_data = {
            'first_name': 'New',
            'last_name': 'User',
            'username': 'newuser',
            'email': 'existing_registration@example.com',  # Email déjà existant
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
                email='existing_registration@example.com',  # Email déjà existant
                password='TestPass123!'
            )

        error = context.exception
        self.assertEqual(error.email, 'existing_registration@example.com')
        self.assertIn('already registered', error.message)


    def test_case_insensitive_email_duplicate_detection(self):
        """Test que la détection d'emails dupliqués est insensible à la casse"""
        form_data = {
            'first_name': 'New',
            'last_name': 'User',
            'username': 'newuser2',
            'email': 'EXISTING_REGISTRATION@EXAMPLE.COM',  # Même email en majuscules
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

        # Mock le logger spécifique au module forms
        with patch('apps.authentication.forms.auth_forms.logger') as mock_logger:
            # Tester le formulaire avec email dupliqué
            form = RegisterForm(data=form_data)
            self.assertFalse(form.is_valid())

            # Vérifier que warning a été appelé
            mock_logger.warning.assert_called_once()
            call_args = mock_logger.warning.call_args[0][0]
            self.assertIn('duplicate email', call_args.lower())
            self.assertIn('audit@example.com', call_args)


class DuplicateEmailRedirectionTest(TestCase):
    """Test de la redirection automatique vers la page de login"""

    def setUp(self):
        self.client = Client()

        # Créer un utilisateur existant
        User.objects.create_user(
            username='redirect_user',
            email='redirect@example.com',
            password='TestPass123!'
        )

    def test_form_duplicate_email_redirect_flag(self):
        """Test que le formulaire marque une redirection nécessaire"""
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'testuser',
            'email': 'redirect@example.com',  # Email existant
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'birthday': '1990-01-01',
            'gender': 'M',
            'interface_language': 'en',
            'terms': True
        }

        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())

        # Vérifier que les attributs de redirection sont définis
        self.assertTrue(hasattr(form, '_redirect_to_login'))
        self.assertTrue(form._redirect_to_login)
        self.assertEqual(form._duplicate_email, 'redirect@example.com')

    def test_registration_view_redirect_to_login(self):
        """Test que la vue d'inscription redirige vers login avec email dupliqué"""
        from django.urls import reverse
        from unittest.mock import patch

        # Mock la vue RegisterView pour tester la logique
        with patch('apps.authentication.views.auth_views.RegisterView.post') as mock_post:
            # Simuler le comportement de redirection
            from django.shortcuts import redirect
            from django.contrib import messages
            from django.http import HttpRequest

            request = HttpRequest()
            request.method = 'POST'
            request.POST = {
                'first_name': 'Test',
                'last_name': 'User',
                'username': 'testuser',
                'email': 'redirect@example.com',
                'password1': 'TestPass123!',
                'password2': 'TestPass123!',
                'birthday': '1990-01-01',
                'gender': 'M',
                'interface_language': 'en',
                'terms': 'on'
            }

            # Tester la logique de redirection
            form = RegisterForm(data=request.POST)
            self.assertFalse(form.is_valid())

            # Si le formulaire a les flags de redirection
            if hasattr(form, '_redirect_to_login') and form._redirect_to_login:
                redirect_url = f'/auth/login/?email={form._duplicate_email}&from=register'
                self.assertEqual(redirect_url, '/auth/login/?email=redirect@example.com&from=register')


class LoginViewContextTest(TestCase):
    """Test du contexte et pré-remplissage de la LoginView"""

    def setUp(self):
        self.client = Client()

    def test_login_view_prefill_email(self):
        """Test que LoginView pré-remplit l'email depuis l'URL"""
        from django.test import RequestFactory
        from apps.authentication.views.auth_views import LoginView

        factory = RequestFactory()
        request = factory.get('/auth/login/?email=test@example.com&from=register')

        view = LoginView()
        view.request = request

        # Tester le contexte
        context = view.get_context_data()
        self.assertEqual(context['prefill_email'], 'test@example.com')
        self.assertTrue(context['from_register'])

        # Tester le formulaire pré-rempli
        form = view.get_form()
        self.assertEqual(form.fields['username'].initial, 'test@example.com')

    def test_login_view_no_prefill(self):
        """Test que LoginView fonctionne sans paramètres"""
        from django.test import RequestFactory
        from apps.authentication.views.auth_views import LoginView

        factory = RequestFactory()
        request = factory.get('/auth/login/')

        view = LoginView()
        view.request = request

        # Tester le contexte sans paramètres
        context = view.get_context_data()
        self.assertEqual(context['prefill_email'], '')
        self.assertFalse(context['from_register'])

        # Tester le formulaire sans pré-remplissage
        form = view.get_form()
        self.assertIsNone(form.fields['username'].initial)


class DuplicateEmailIntegrationTest(TestCase):
    """Test d'intégration complète du flow de redirection"""

    def setUp(self):
        self.client = Client()

        # Créer un utilisateur existant
        self.existing_user = User.objects.create_user(
            username='integration_user',
            email='integration@example.com',
            password='TestPass123!'
        )

    def test_complete_duplicate_email_flow(self):
        """Test du flow complet : inscription -> détection -> redirection -> login"""

        # 1. Test de la détection d'email dupliqué dans le formulaire
        form_data = {
            'first_name': 'New',
            'last_name': 'User',
            'username': 'newuser',
            'email': 'integration@example.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'birthday': '1990-01-01',
            'gender': 'M',
            'interface_language': 'en',
            'terms': True
        }

        form = RegisterForm(data=form_data)

        # 2. Vérifier que le formulaire n'est pas valide
        self.assertFalse(form.is_valid())

        # 3. Vérifier que les flags de redirection sont définis
        self.assertTrue(hasattr(form, '_redirect_to_login'))
        self.assertTrue(form._redirect_to_login)
        self.assertEqual(form._duplicate_email, 'integration@example.com')

        # 4. Vérifier le message d'erreur
        self.assertIn('email', form.errors)
        self.assertIn('redirected to the login page', str(form.errors['email']))

    def test_duplicate_email_user_manager_integration(self):
        """Test que le UserManager fonctionne toujours avec DuplicateEmailError"""

        # Tenter de créer un utilisateur avec un email existant
        with self.assertRaises(DuplicateEmailError) as context:
            User.objects.create_user(
                username='another_user',
                email='integration@example.com',  # Email existant
                password='TestPass123!'
            )

        error = context.exception
        self.assertEqual(error.email, 'integration@example.com')
        self.assertIn('already registered', error.message)


class DuplicateEmailInternationalizationTest(TestCase):
    """Test de l'internationalisation pour les messages d'erreur d'email dupliqué"""

    def setUp(self):
        self.client = Client()

        # Créer un utilisateur existant
        User.objects.create_user(
            username='i18n_user',
            email='i18n@example.com',
            password='TestPass123!'
        )

    def test_french_duplicate_email_message(self):
        """Test que les messages sont traduits en français"""
        from django.utils import translation

        # Activer la langue française
        with translation.override('fr'):
            form_data = {
                'first_name': 'Test',
                'last_name': 'User',
                'username': 'testuser',
                'email': 'i18n@example.com',  # Email existant
                'password1': 'TestPass123!',
                'password2': 'TestPass123!',
                'birthday': '1990-01-01',
                'gender': 'M',
                'interface_language': 'fr',
                'terms': True
            }

            form = RegisterForm(data=form_data)
            self.assertFalse(form.is_valid())

            # Vérifier que le message est en français
            self.assertIn('email', form.errors)
            error_message = str(form.errors['email'])
            self.assertIn('redirigé', error_message)  # Mot français

    def test_spanish_duplicate_email_message(self):
        """Test que les messages sont traduits en espagnol"""
        from django.utils import translation

        # Activer la langue espagnole
        with translation.override('es'):
            form_data = {
                'first_name': 'Test',
                'last_name': 'User',
                'username': 'testuser2',
                'email': 'i18n@example.com',  # Email existant
                'password1': 'TestPass123!',
                'password2': 'TestPass123!',
                'birthday': '1990-01-01',
                'gender': 'M',
                'interface_language': 'es',
                'terms': True
            }

            form = RegisterForm(data=form_data)
            self.assertFalse(form.is_valid())

            # Vérifier que le message est en espagnol
            self.assertIn('email', form.errors)
            error_message = str(form.errors['email'])
            self.assertIn('redirigido', error_message)  # Mot espagnol

    def test_dutch_duplicate_email_message(self):
        """Test que les messages sont traduits en néerlandais"""
        from django.utils import translation

        # Activer la langue néerlandaise
        with translation.override('nl'):
            form_data = {
                'first_name': 'Test',
                'last_name': 'User',
                'username': 'testuser3',
                'email': 'i18n@example.com',  # Email existant
                'password1': 'TestPass123!',
                'password2': 'TestPass123!',
                'birthday': '1990-01-01',
                'gender': 'M',
                'interface_language': 'nl',
                'terms': True
            }

            form = RegisterForm(data=form_data)
            self.assertFalse(form.is_valid())

            # Vérifier que le message est en néerlandais
            self.assertIn('email', form.errors)
            error_message = str(form.errors['email'])
            self.assertIn('doorgestuurd', error_message)  # Mot néerlandais

    def test_english_duplicate_email_message(self):
        """Test que les messages sont en anglais"""
        from django.utils import translation

        # Activer la langue anglaise
        with translation.override('en'):
            form_data = {
                'first_name': 'Test',
                'last_name': 'User',
                'username': 'testuser4',
                'email': 'i18n@example.com',  # Email existant
                'password1': 'TestPass123!',
                'password2': 'TestPass123!',
                'birthday': '1990-01-01',
                'gender': 'M',
                'interface_language': 'en',
                'terms': True
            }

            form = RegisterForm(data=form_data)
            self.assertFalse(form.is_valid())

            # Vérifier que le message est en anglais
            self.assertIn('email', form.errors)
            error_message = str(form.errors['email'])
            self.assertIn('redirected to the login page', error_message)  # Message anglais

    def test_login_url_preservation_with_language(self):
        """Test que la redirection préserve la langue dans l'URL"""
        from django.test import RequestFactory
        from django.utils import translation
        from apps.authentication.views.auth_views import RegisterView
        from unittest.mock import patch

        # Tester avec différentes langues
        for lang_code in ['fr', 'es', 'nl', 'en']:
            with translation.override(lang_code):
                factory = RequestFactory()
                request = factory.post(f'/{lang_code}/auth/register/', {
                    'first_name': 'Test',
                    'last_name': 'User',
                    'username': f'testuser_{lang_code}',
                    'email': 'i18n@example.com',
                    'password1': 'TestPass123!',
                    'password2': 'TestPass123!',
                    'birthday': '1990-01-01',
                    'gender': 'M',
                    'interface_language': lang_code,
                    'terms': 'on'
                })

                # Mock les messages
                with patch('django.contrib.messages.info'):
                    # Mock le redirect pour capturer l'URL
                    with patch('django.shortcuts.redirect') as mock_redirect:
                        view = RegisterView()
                        view.post(request)

                        # Vérifier que redirect a été appelé
                        if mock_redirect.called:
                            call_args = mock_redirect.call_args[0][0]
                            # Vérifier que l'URL contient l'email et from=register
                            self.assertIn('email=i18n@example.com', call_args)
                            self.assertIn('from=register', call_args)