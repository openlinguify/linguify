"""
Tests pour les vues app_manager
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.http import JsonResponse
from unittest.mock import patch, Mock
from rest_framework.test import APITestCase, APIClient
import json

from ..models import App, UserAppSettings
from ..views.app_manager_views import AppStoreView, AppToggleAPI
from ..views.app_manager_settings_views import AppManagerSettingsView, UserAppSettingsView

User = get_user_model()


class AppStoreViewTest(TestCase):
    """Tests pour AppStoreView"""

    def setUp(self):
        """Configuration des tests"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Ensure user is active
        self.user.is_active = True
        self.user.save()

        # Créer quelques apps de test
        self.app1 = App.objects.create(
            code='test_app_1',
            display_name='Test App 1',
            description='Application de test 1',
            icon_name='TestIcon1',
            route_path='/test1',
            category='productivity',
            is_enabled=True
        )

        self.app2 = App.objects.create(
            code='test_app_2',
            display_name='Test App 2',
            description='Application de test 2',
            icon_name='TestIcon2',
            route_path='/test2',
            category='communication',
            is_enabled=True
        )

        self.app_disabled = App.objects.create(
            code='disabled_app',
            display_name='Disabled App',
            description='Application désactivée',
            icon_name='DisabledIcon',
            route_path='/disabled',
            category='productivity',
            is_enabled=False
        )

    def test_app_store_view_authenticated(self):
        """Test l'affichage du store pour un utilisateur connecté"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('app_manager:app_store'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test App 1')
        self.assertContains(response, 'Test App 2')
        self.assertNotContains(response, 'Disabled App')  # App désactivée non visible

    def test_app_store_view_unauthenticated(self):
        """Test redirection pour utilisateur non connecté"""
        response = self.client.get(reverse('app_manager:app_store'))
        self.assertEqual(response.status_code, 302)  # Redirection vers login

    def test_app_store_filtering_by_category(self):
        """Test le filtrage par catégorie"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('app_manager:app_store'))

        # Vérifier que les catégories sont présentes
        self.assertContains(response, 'productivity')
        self.assertContains(response, 'communication')

    def test_app_store_with_user_settings(self):
        """Test l'affichage avec paramètres utilisateur"""
        self.client.force_login(self.user)

        # Créer des paramètres utilisateur
        user_settings = UserAppSettings.objects.create(user=self.user)
        user_settings.enable_app('test_app_1')

        response = self.client.get(reverse('app_manager:app_store'))
        self.assertEqual(response.status_code, 200)


class AppToggleAPITest(TestCase):
    """Tests pour AppToggleAPI"""

    def setUp(self):
        """Configuration des tests"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Ensure user is active
        self.user.is_active = True
        self.user.save()

        self.app = App.objects.create(
            code='test_app',
            display_name='Test App',
            description='Application de test',
            icon_name='TestIcon',
            route_path='/test',
            category='productivity',
            is_enabled=True
        )

        self.user_settings, _ = UserAppSettings.objects.get_or_create(user=self.user)

    def test_toggle_app_enable(self):
        """Test l'activation d'une app"""
        self.client.force_login(self.user)

        url = reverse('app_manager:api_app_toggle', kwargs={'app_id': self.app.id})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertTrue(data['is_enabled'])

        # Vérifier que l'app est activée
        self.user_settings.refresh_from_db()
        self.assertTrue(self.user_settings.is_app_enabled('test_app'))

    def test_toggle_app_disable(self):
        """Test la désactivation d'une app"""
        self.client.force_login(self.user)

        # Activer d'abord l'app
        self.user_settings.enable_app('test_app')

        url = reverse('app_manager:api_app_toggle', kwargs={'app_id': self.app.id})
        response = self.client.post(url, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertFalse(data['is_enabled'])

        # Vérifier que l'app est désactivée
        self.user_settings.refresh_from_db()
        self.assertFalse(self.user_settings.is_app_enabled('test_app'))

    def test_toggle_nonexistent_app(self):
        """Test toggle d'une app inexistante"""
        self.client.force_login(self.user)

        url = reverse('app_manager:api_app_toggle', kwargs={'app_id': 99999})
        response = self.client.post(url, content_type='application/json')

        self.assertEqual(response.status_code, 404)

    def test_toggle_unauthenticated(self):
        """Test toggle sans authentification"""
        url = reverse('app_manager:api_app_toggle', kwargs={'app_id': self.app.id})
        response = self.client.post(url, content_type='application/json')

        self.assertEqual(response.status_code, 302)  # Redirection vers login

    def test_toggle_disabled_app(self):
        """Test toggle d'une app globalement désactivée"""
        self.client.force_login(self.user)

        # Désactiver l'app globalement
        self.app.is_enabled = False
        self.app.save()

        url = reverse('app_manager:api_app_toggle', kwargs={'app_id': self.app.id})
        response = self.client.post(url, content_type='application/json')

        self.assertEqual(response.status_code, 404)

    @patch('app_manager.services.cache_service.UserAppCacheService.clear_user_apps_cache_for_user')
    def test_toggle_clears_cache(self, mock_clear_cache):
        """Test que le toggle invalide le cache"""
        self.client.force_login(self.user)

        url = reverse('app_manager:api_app_toggle', kwargs={'app_id': self.app.id})
        response = self.client.post(url, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        mock_clear_cache.assert_called_once_with(self.user)


class AppManagerSettingsViewTest(TestCase):
    """Tests pour AppManagerSettingsView"""

    def setUp(self):
        """Configuration des tests"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        self.app = App.objects.create(
            code='test_app',
            display_name='Test App',
            description='Application de test',
            icon_name='TestIcon',
            route_path='/test',
            category='productivity',
            is_enabled=True
        )

    def test_settings_view_authenticated(self):
        """Test l'affichage des paramètres pour un utilisateur connecté"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('app_manager:app_settings'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test App')

    def test_settings_view_unauthenticated(self):
        """Test redirection pour utilisateur non connecté"""
        response = self.client.get(reverse('app_manager:app_settings'))
        self.assertEqual(response.status_code, 302)


class UserAppSettingsViewTest(APITestCase):
    """Tests pour UserAppSettingsView API"""

    def setUp(self):
        """Configuration des tests"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        self.app1 = App.objects.create(
            code='test_app_1',
            display_name='Test App 1',
            description='Application de test 1',
            icon_name='TestIcon1',
            route_path='/test1',
            category='productivity',
            is_enabled=True
        )

        self.app2 = App.objects.create(
            code='test_app_2',
            display_name='Test App 2',
            description='Application de test 2',
            icon_name='TestIcon2',
            route_path='/test2',
            category='communication',
            is_enabled=True
        )

        self.user_settings, _ = UserAppSettings.objects.get_or_create(user=self.user)
        self.user_settings.enable_app('test_app_1')

    def test_get_user_settings(self):
        """Test la récupération des paramètres utilisateur"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse('app_manager:api_user_app_settings'))

        self.assertEqual(response.status_code, 200)

        self.assertIn('enabled_apps', response.data)
        enabled_app_codes = [app['code'] for app in response.data['enabled_apps']]
        self.assertIn('test_app_1', enabled_app_codes)
        self.assertNotIn('test_app_2', enabled_app_codes)

    def test_update_user_settings(self):
        """Test la mise à jour des paramètres utilisateur"""
        self.client.force_authenticate(user=self.user)

        update_data = {
            'enabled_app_codes': ['test_app_1', 'test_app_2']
        }

        response = self.client.put(
            reverse('app_manager:api_user_app_settings'),
            data=update_data,
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('enabled_apps', response.data)

        # Vérifier que les paramètres ont été mis à jour
        self.user_settings.refresh_from_db()
        self.assertTrue(self.user_settings.is_app_enabled('test_app_1'))
        self.assertTrue(self.user_settings.is_app_enabled('test_app_2'))

    def test_invalid_json_data(self):
        """Test avec données JSON invalides"""
        self.client.force_authenticate(user=self.user)

        # Envoyer des données invalides
        response = self.client.put(
            reverse('app_manager:api_user_app_settings'),
            data={'enabled_app_codes': 'invalid_format'},
            format='json'
        )

        self.assertEqual(response.status_code, 400)

    def test_unauthenticated_request(self):
        """Test requête sans authentification"""
        response = self.client.get(reverse('app_manager:api_user_app_settings'))
        # DRF renvoie 403 au lieu de 401 pour les permissions IsAuthenticated
        self.assertEqual(response.status_code, 403)


class FastAPITest(APITestCase):
    """Tests pour les APIs de performance"""

    def setUp(self):
        """Configuration des tests"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        self.app = App.objects.create(
            code='test_app',
            display_name='Test App',
            description='Application de test',
            icon_name='TestIcon',
            route_path='/test',
            category='productivity',
            is_enabled=True
        )

        self.user_settings, _ = UserAppSettings.objects.get_or_create(user=self.user)
        self.user_settings.enable_app('test_app')

    def test_user_apps_fast_api(self):
        """Test l'API rapide des apps utilisateur"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse('app_manager:api_user_apps_fast'))

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        self.assertIn('apps', data)
        self.assertGreaterEqual(len(data['apps']), 0)

    def test_categories_fast_api(self):
        """Test l'API rapide des catégories"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse('app_manager:api_categories'))

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        self.assertIn('categories', data)
        self.assertTrue(data['success'])

    def test_installation_status_api(self):
        """Test l'API de statut d'installation"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse('app_manager:api_installation_status'), {'app_ids': [self.app.id]})

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        self.assertIn('status', data)
        self.assertTrue(data['success'])