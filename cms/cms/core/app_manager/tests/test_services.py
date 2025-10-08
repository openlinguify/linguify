"""
Tests pour les services app_manager
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache
from unittest.mock import patch, Mock, MagicMock
import json

from ..models import App, UserAppSettings
try:
    from ..services.cache_service import UserAppCacheService
    from ..services.user_app_service import UserAppService
except ImportError:
    UserAppCacheService = None
    UserAppService = None

try:
    from ..services.app_settings_service import AppSettingsService
    from ..services.app_icon_service import AppIconService
    from ..services.app_readiness_service import AppReadinessService
except ImportError:
    AppSettingsService = None
    AppIconService = None
    AppReadinessService = None

User = get_user_model()


class UserAppCacheServiceTest(TestCase):
    """Tests pour UserAppCacheService"""

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

        self.user_settings = UserAppSettings.objects.create(user=self.user)
        self.user_settings.enable_app('test_app')

        # Clear cache before each test
        cache.clear()

    def test_get_user_apps_cache_key(self):
        """Test la génération de clé de cache"""
        key = UserAppCacheService.get_user_apps_cache_key(self.user)
        expected = f"user_apps_v2_{self.user.id}"
        self.assertEqual(key, expected)

    def test_get_user_apps_from_cache_miss(self):
        """Test récupération avec cache miss"""
        apps = UserAppCacheService.get_user_apps(self.user)

        self.assertIsNotNone(apps)
        self.assertEqual(len(apps), 1)
        self.assertEqual(apps[0]['code'], 'test_app')

    def test_get_user_apps_from_cache_hit(self):
        """Test récupération avec cache hit"""
        # Premier appel pour mettre en cache
        apps1 = UserAppCacheService.get_user_apps(self.user)

        # Mock the database query to ensure we're using cache
        with patch('app_manager.models.app_manager_models.App.objects') as mock_apps:
            apps2 = UserAppCacheService.get_user_apps(self.user)

            # Should not query database on second call
            mock_apps.filter.assert_not_called()

        self.assertEqual(len(apps2), len(apps1))

    def test_clear_user_apps_cache_for_user(self):
        """Test l'invalidation du cache utilisateur"""
        # Mettre en cache
        UserAppCacheService.get_user_apps(self.user)

        # Vérifier que le cache existe
        cache_key = UserAppCacheService.get_user_apps_cache_key(self.user)
        self.assertIsNotNone(cache.get(cache_key))

        # Invalider le cache
        UserAppCacheService.clear_user_apps_cache_for_user(self.user)

        # Vérifier que le cache est vide
        self.assertIsNone(cache.get(cache_key))

    def test_get_app_store_data_cache(self):
        """Test le cache des données du store"""
        data = UserAppCacheService.get_app_store_data()

        self.assertIn('apps', data)
        self.assertIn('categories', data)
        self.assertGreater(len(data['apps']), 0)

    def test_clear_all_caches(self):
        """Test l'invalidation de tous les caches"""
        # Mettre en cache plusieurs éléments
        UserAppCacheService.get_user_apps(self.user)
        UserAppCacheService.get_app_store_data()

        # Invalider tous les caches
        UserAppCacheService.clear_all_caches()

        # Vérifier que les caches sont vides
        user_cache_key = UserAppCacheService.get_user_apps_cache_key(self.user)
        self.assertIsNone(cache.get(user_cache_key))


class UserAppServiceTest(TestCase):
    """Tests pour UserAppService"""

    def setUp(self):
        """Configuration des tests"""
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
            is_enabled=True,
            order=1
        )

        self.app2 = App.objects.create(
            code='test_app_2',
            display_name='Test App 2',
            description='Application de test 2',
            icon_name='TestIcon2',
            route_path='/test2',
            category='communication',
            is_enabled=True,
            order=2
        )

        self.user_settings = UserAppSettings.objects.create(user=self.user)

    def test_get_user_enabled_apps(self):
        """Test la récupération des apps activées pour un utilisateur"""
        # Activer une app
        self.user_settings.enable_app('test_app_1')

        apps = UserAppService.get_user_enabled_apps(self.user)

        self.assertEqual(len(apps), 1)
        self.assertEqual(apps[0].code, 'test_app_1')

    def test_get_user_enabled_apps_ordered(self):
        """Test l'ordre des apps activées"""
        # Activer les deux apps
        self.user_settings.enable_app('test_app_1')
        self.user_settings.enable_app('test_app_2')

        apps = UserAppService.get_user_enabled_apps(self.user)

        # Vérifier l'ordre
        self.assertEqual(len(apps), 2)
        self.assertEqual(apps[0].code, 'test_app_1')  # order=1
        self.assertEqual(apps[1].code, 'test_app_2')  # order=2

    def test_toggle_app_enable(self):
        """Test l'activation d'une app"""
        result = UserAppService.toggle_app(self.user, self.app1.id)

        self.assertTrue(result['success'])
        self.assertTrue(result['is_enabled'])
        self.assertTrue(self.user_settings.is_app_enabled('test_app_1'))

    def test_toggle_app_disable(self):
        """Test la désactivation d'une app"""
        # Activer d'abord
        self.user_settings.enable_app('test_app_1')

        result = UserAppService.toggle_app(self.user, self.app1.id)

        self.assertTrue(result['success'])
        self.assertFalse(result['is_enabled'])
        self.assertFalse(self.user_settings.is_app_enabled('test_app_1'))

    def test_toggle_nonexistent_app(self):
        """Test toggle d'une app inexistante"""
        result = UserAppService.toggle_app(self.user, 99999)

        self.assertFalse(result['success'])
        self.assertIn('error', result)

    def test_toggle_disabled_app(self):
        """Test toggle d'une app globalement désactivée"""
        self.app1.is_enabled = False
        self.app1.save()

        result = UserAppService.toggle_app(self.user, self.app1.id)

        self.assertFalse(result['success'])
        self.assertIn('error', result)

    def test_get_user_app_settings_creates_if_not_exists(self):
        """Test la création automatique des paramètres utilisateur"""
        # Supprimer les paramètres existants
        UserAppSettings.objects.filter(user=self.user).delete()

        settings = UserAppService.get_user_app_settings(self.user)

        self.assertIsNotNone(settings)
        self.assertEqual(settings.user, self.user)

    def test_bulk_toggle_apps(self):
        """Test l'activation/désactivation en masse"""
        app_configs = [
            {'app_id': self.app1.id, 'enabled': True},
            {'app_id': self.app2.id, 'enabled': False}
        ]

        results = UserAppService.bulk_toggle_apps(self.user, app_configs)

        self.assertEqual(len(results), 2)
        self.assertTrue(all(r['success'] for r in results))

        # Vérifier les états
        self.assertTrue(self.user_settings.is_app_enabled('test_app_1'))
        self.assertFalse(self.user_settings.is_app_enabled('test_app_2'))


class AppSettingsServiceTest(TestCase):
    """Tests pour AppSettingsService"""

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

    def test_get_app_settings_for_user(self):
        """Test la récupération des paramètres pour un utilisateur"""
        settings = AppSettingsService.get_app_settings_for_user(self.user)

        self.assertIn('enabled_apps', settings)
        self.assertIn('available_apps', settings)
        self.assertIsInstance(settings['enabled_apps'], list)

    def test_update_user_app_settings(self):
        """Test la mise à jour des paramètres utilisateur"""
        new_settings = {
            'enabled_apps': ['test_app'],
            'app_order': ['test_app']
        }

        result = AppSettingsService.update_user_app_settings(self.user, new_settings)

        self.assertTrue(result['success'])

        # Vérifier que les paramètres ont été appliqués
        user_settings = UserAppSettings.objects.get(user=self.user)
        self.assertTrue(user_settings.is_app_enabled('test_app'))

    def test_update_invalid_app(self):
        """Test la mise à jour avec une app invalide"""
        new_settings = {
            'enabled_apps': ['nonexistent_app']
        }

        result = AppSettingsService.update_user_app_settings(self.user, new_settings)

        # Devrait continuer sans erreur mais ignorer l'app invalide
        self.assertTrue(result['success'])

    def test_export_user_settings(self):
        """Test l'export des paramètres utilisateur"""
        # Activer une app
        user_settings = UserAppSettings.objects.create(user=self.user)
        user_settings.enable_app('test_app')

        exported = AppSettingsService.export_user_settings(self.user)

        self.assertIn('enabled_apps', exported)
        self.assertIn('test_app', exported['enabled_apps'])
        self.assertIn('export_date', exported)

    def test_import_user_settings(self):
        """Test l'import des paramètres utilisateur"""
        settings_data = {
            'enabled_apps': ['test_app'],
            'app_order': ['test_app']
        }

        result = AppSettingsService.import_user_settings(self.user, settings_data)

        self.assertTrue(result['success'])

        # Vérifier que les paramètres ont été importés
        user_settings = UserAppSettings.objects.get(user=self.user)
        self.assertTrue(user_settings.is_app_enabled('test_app'))


class AppIconServiceTest(TestCase):
    """Tests pour AppIconService"""

    def setUp(self):
        """Configuration des tests"""
        self.app = App.objects.create(
            code='test_app',
            display_name='Test App',
            description='Application de test',
            icon_name='TestIcon',
            route_path='/test',
            category='productivity',
            is_enabled=True
        )

    def test_get_app_icon_url(self):
        """Test la récupération de l'URL d'icône"""
        icon_url = AppIconService.get_app_icon_url(self.app)

        self.assertIsNotNone(icon_url)
        self.assertIn('test_app', icon_url)

    def test_get_default_icon_for_category(self):
        """Test l'icône par défaut pour une catégorie"""
        icon = AppIconService.get_default_icon_for_category('productivity')

        self.assertIsNotNone(icon)
        self.assertIsInstance(icon, str)

    @patch('app_manager.services.app_icon_service.os.path.exists')
    def test_icon_exists_check(self, mock_exists):
        """Test la vérification d'existence d'icône"""
        mock_exists.return_value = True

        exists = AppIconService.icon_exists(self.app)

        self.assertTrue(exists)
        mock_exists.assert_called_once()

    def test_get_icon_variants(self):
        """Test la récupération des variantes d'icône"""
        variants = AppIconService.get_icon_variants(self.app)

        self.assertIsInstance(variants, dict)
        self.assertIn('default', variants)


class AppReadinessServiceTest(TestCase):
    """Tests pour AppReadinessService"""

    def setUp(self):
        """Configuration des tests"""
        self.app = App.objects.create(
            code='test_app',
            display_name='Test App',
            description='Application de test',
            icon_name='TestIcon',
            route_path='/test',
            category='productivity',
            is_enabled=True
        )

    def test_check_app_readiness(self):
        """Test la vérification de disponibilité d'une app"""
        readiness = AppReadinessService.check_app_readiness(self.app)

        self.assertIn('ready', readiness)
        self.assertIn('checks', readiness)
        self.assertIsInstance(readiness['checks'], list)

    def test_check_all_apps_readiness(self):
        """Test la vérification de toutes les apps"""
        readiness_report = AppReadinessService.check_all_apps_readiness()

        self.assertIn('total_apps', readiness_report)
        self.assertIn('ready_apps', readiness_report)
        self.assertIn('failed_apps', readiness_report)
        self.assertIn('details', readiness_report)

    @patch('app_manager.services.app_readiness_service.os.path.exists')
    def test_check_route_exists(self, mock_exists):
        """Test la vérification d'existence de route"""
        mock_exists.return_value = True

        route_check = AppReadinessService.check_route_exists(self.app)

        self.assertIn('exists', route_check)
        self.assertIn('path', route_check)

    def test_check_dependencies(self):
        """Test la vérification des dépendances"""
        deps_check = AppReadinessService.check_dependencies(self.app)

        self.assertIn('satisfied', deps_check)
        self.assertIn('missing', deps_check)
        self.assertIsInstance(deps_check['missing'], list)

    def test_performance_check(self):
        """Test la vérification de performance"""
        perf_check = AppReadinessService.performance_check(self.app)

        self.assertIn('response_time', perf_check)
        self.assertIn('status', perf_check)
        self.assertIsInstance(perf_check['response_time'], (int, float))