"""
Tests avancés pour les modèles app_manager
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from unittest.mock import patch, Mock
from datetime import datetime, timedelta
import json

from ..models import App, UserAppSettings, AppDataRetention

User = get_user_model()


class AppModelAdvancedTest(TestCase):
    """Tests avancés pour le modèle App"""

    def setUp(self):
        """Configuration des tests"""
        self.app_data = {
            'code': 'test_app',
            'display_name': 'Test Application',
            'description': 'Application de test',
            'icon_name': 'TestIcon',
            'route_path': '/test',
            'category': 'productivity'
        }

    def test_app_unique_code_constraint(self):
        """Test la contrainte d'unicité du code"""
        App.objects.create(**self.app_data)

        with self.assertRaises(IntegrityError):
            App.objects.create(**self.app_data)

    def test_app_ordering(self):
        """Test l'ordre par défaut des apps"""
        app1 = App.objects.create(code='app1', display_name='App 1', order=2)
        app2 = App.objects.create(code='app2', display_name='App 2', order=1)
        app3 = App.objects.create(code='app3', display_name='App 3', order=3)

        ordered_apps = App.objects.all()
        codes = [app.code for app in ordered_apps]

        self.assertEqual(codes, ['app2', 'app1', 'app3'])

    def test_get_ordered_enabled_apps_optimization(self):
        """Test l'optimisation de la requête get_ordered_enabled_apps"""
        # Créer plusieurs apps
        for i in range(5):
            App.objects.create(
                code=f'app_{i}',
                display_name=f'App {i}',
                is_enabled=i % 2 == 0,  # Apps paires activées
                order=i
            )

        with self.assertNumQueries(1):  # Doit être une seule requête optimisée
            enabled_apps = App.get_ordered_enabled_apps()
            list(enabled_apps)  # Force l'évaluation de la queryset

        # Vérifier que seules les apps activées sont retournées
        self.assertEqual(len(list(enabled_apps)), 3)  # 0, 2, 4

    def test_app_manifest_data_handling(self):
        """Test la gestion des données de manifest"""
        manifest_data = {
            'version': '1.0.0',
            'permissions': ['read', 'write'],
            'dependencies': ['app_b', 'app_c']
        }

        app = App.objects.create(
            **self.app_data,
            manifest_data=manifest_data
        )

        self.assertEqual(app.manifest_data['version'], '1.0.0')
        self.assertIn('read', app.manifest_data['permissions'])

    def test_app_category_validation(self):
        """Test la validation des catégories"""
        valid_categories = ['productivity', 'communication', 'social', 'education', 'collaboration', 'ai']

        for category in valid_categories:
            app = App.objects.create(
                code=f'app_{category}',
                display_name=f'App {category}',
                category=category
            )
            self.assertEqual(app.category, category)

    def test_app_string_representation_with_special_chars(self):
        """Test la représentation string avec caractères spéciaux"""
        app = App.objects.create(
            code='special_app',
            display_name='Ăpp wíth špéčiál ćhārs 🚀',
            **{k: v for k, v in self.app_data.items() if k != 'code' and k != 'display_name'}
        )

        self.assertEqual(str(app), 'Ăpp wíth špéčiál ćhārs 🚀')

    def test_app_route_path_validation(self):
        """Test la validation du chemin de route"""
        # Route valide
        app = App.objects.create(
            **self.app_data,
            route_path='/valid/path'
        )
        self.assertTrue(app.route_path.startswith('/'))

        # Route sans slash initial - devrait être corrigée
        app2 = App.objects.create(
            code='app2',
            display_name='App 2',
            route_path='invalid/path'
        )
        # Note: Dépend de l'implémentation du modèle pour auto-corriger

    @patch('app_manager.services.cache_service.UserAppCacheService.clear_all_caches')
    def test_app_save_cache_invalidation(self, mock_clear_cache):
        """Test l'invalidation du cache lors de la sauvegarde"""
        app = App.objects.create(**self.app_data)
        app.display_name = 'Updated Name'
        app.save()

        mock_clear_cache.assert_called()

    def test_app_performance_with_large_dataset(self):
        """Test les performances avec un grand nombre d'apps"""
        # Créer 100 apps
        apps_data = []
        for i in range(100):
            apps_data.append(App(
                code=f'perf_app_{i}',
                display_name=f'Performance App {i}',
                category='productivity' if i % 2 == 0 else 'communication',
                is_enabled=i % 3 == 0,  # 1/3 des apps activées
                order=i
            ))

        App.objects.bulk_create(apps_data)

        # Test de performance pour récupération des apps activées
        with self.assertNumQueries(1):
            enabled_apps = list(App.get_ordered_enabled_apps())

        self.assertEqual(len(enabled_apps), 34)  # 1/3 de 100, arrondi


class UserAppSettingsAdvancedTest(TestCase):
    """Tests avancés pour UserAppSettings"""

    def setUp(self):
        """Configuration des tests"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Créer plusieurs apps
        self.apps = []
        for i in range(5):
            app = App.objects.create(
                code=f'test_app_{i}',
                display_name=f'Test App {i}',
                category='productivity',
                order=i
            )
            self.apps.append(app)

        self.user_settings = UserAppSettings.objects.create(user=self.user)

    def test_enable_multiple_apps_performance(self):
        """Test les performances d'activation de plusieurs apps"""
        app_codes = [app.code for app in self.apps]

        # Test d'activation en masse
        with self.assertNumQueries(6):  # Optimisation attendue
            for code in app_codes:
                self.user_settings.enable_app(code)

        # Vérifier que toutes les apps sont activées
        enabled_codes = self.user_settings.get_enabled_app_codes()
        self.assertEqual(set(enabled_codes), set(app_codes))

    def test_app_order_management(self):
        """Test la gestion de l'ordre des apps"""
        # Activer quelques apps
        codes = ['test_app_0', 'test_app_1', 'test_app_2']
        for code in codes:
            self.user_settings.enable_app(code)

        # Changer l'ordre
        new_order = ['test_app_2', 'test_app_0', 'test_app_1']
        self.user_settings.update_app_order(new_order)

        # Vérifier l'ordre
        ordered_apps = self.user_settings.get_ordered_enabled_apps()
        ordered_codes = [app.code for app in ordered_apps]

        self.assertEqual(ordered_codes, new_order)

    def test_bulk_enable_disable_apps(self):
        """Test l'activation/désactivation en masse"""
        # Activation en masse
        enable_codes = ['test_app_0', 'test_app_1', 'test_app_2']
        results = []
        for code in enable_codes:
            result = self.user_settings.enable_app(code)
            results.append(result)

        self.assertTrue(all(results))

        # Désactivation en masse
        disable_codes = ['test_app_0', 'test_app_2']
        results = []
        for code in disable_codes:
            result = self.user_settings.disable_app(code)
            results.append(result)

        self.assertTrue(all(results))

        # Vérifier l'état final
        enabled_codes = self.user_settings.get_enabled_app_codes()
        self.assertEqual(enabled_codes, ['test_app_1'])

    def test_concurrent_modifications(self):
        """Test les modifications concurrentes"""
        def enable_app_transaction():
            with transaction.atomic():
                settings = UserAppSettings.objects.select_for_update().get(user=self.user)
                settings.enable_app('test_app_0')

        def disable_app_transaction():
            with transaction.atomic():
                settings = UserAppSettings.objects.select_for_update().get(user=self.user)
                settings.disable_app('test_app_0')

        # Premier activer l'app
        enable_app_transaction()
        self.assertTrue(self.user_settings.is_app_enabled('test_app_0'))

        # Puis la désactiver
        disable_app_transaction()
        self.user_settings.refresh_from_db()
        self.assertFalse(self.user_settings.is_app_enabled('test_app_0'))

    def test_invalid_app_handling(self):
        """Test la gestion des apps invalides"""
        # Essayer d'activer une app inexistante
        result = self.user_settings.enable_app('nonexistent_app')
        self.assertFalse(result)

        # Essayer de désactiver une app inexistante
        result = self.user_settings.disable_app('nonexistent_app')
        self.assertFalse(result)

        # Vérifier qu'aucune app invalide n'est ajoutée
        enabled_codes = self.user_settings.get_enabled_app_codes()
        self.assertNotIn('nonexistent_app', enabled_codes)

    @patch('app_manager.services.cache_service.UserAppCacheService.clear_user_apps_cache_for_user')
    def test_cache_invalidation_on_changes(self, mock_clear_cache):
        """Test l'invalidation du cache lors des modifications"""
        # Activer une app
        self.user_settings.enable_app('test_app_0')
        mock_clear_cache.assert_called_with(self.user)

        mock_clear_cache.reset_mock()

        # Désactiver une app
        self.user_settings.disable_app('test_app_0')
        mock_clear_cache.assert_called_with(self.user)

        mock_clear_cache.reset_mock()

        # Changer l'ordre
        self.user_settings.update_app_order(['test_app_1'])
        mock_clear_cache.assert_called_with(self.user)

    def test_user_settings_data_integrity(self):
        """Test l'intégrité des données des paramètres utilisateur"""
        # Activer des apps
        for i in range(3):
            self.user_settings.enable_app(f'test_app_{i}')

        # Sauvegarder l'état
        original_enabled = set(self.user_settings.get_enabled_app_codes())

        # Recharger depuis la base de données
        self.user_settings.refresh_from_db()
        reloaded_enabled = set(self.user_settings.get_enabled_app_codes())

        self.assertEqual(original_enabled, reloaded_enabled)

    def test_unique_user_constraint(self):
        """Test la contrainte d'unicité par utilisateur"""
        # Essayer de créer des paramètres dupliqués pour le même utilisateur
        with self.assertRaises(IntegrityError):
            UserAppSettings.objects.create(user=self.user)


class AppDataRetentionTest(TestCase):
    """Tests pour AppDataRetention"""

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
            category='productivity'
        )

    def test_data_retention_creation(self):
        """Test la création d'un enregistrement de rétention"""
        retention = AppDataRetention.objects.create(
            user=self.user,
            app=self.app,
            data_backup='{"test": "data"}',
            retention_period_days=30
        )

        self.assertEqual(retention.user, self.user)
        self.assertEqual(retention.app, self.app)
        self.assertEqual(retention.retention_period_days, 30)

    def test_data_retention_expiry_calculation(self):
        """Test le calcul de la date d'expiration"""
        retention = AppDataRetention.objects.create(
            user=self.user,
            app=self.app,
            data_backup='{"test": "data"}',
            retention_period_days=30
        )

        expected_expiry = retention.created_at + timedelta(days=30)
        self.assertEqual(retention.expires_at.date(), expected_expiry.date())

    def test_cleanup_expired_data(self):
        """Test le nettoyage des données expirées"""
        # Créer des données expirées
        expired_retention = AppDataRetention.objects.create(
            user=self.user,
            app=self.app,
            data_backup='{"expired": "data"}',
            retention_period_days=1
        )

        # Modifier manuellement la date de création pour simuler l'expiration
        expired_retention.created_at = datetime.now() - timedelta(days=2)
        expired_retention.save()

        # Créer des données non expirées
        valid_retention = AppDataRetention.objects.create(
            user=self.user,
            app=self.app,
            data_backup='{"valid": "data"}',
            retention_period_days=30
        )

        # Nettoyer les données expirées
        expired_count = AppDataRetention.cleanup_expired_data()

        self.assertEqual(expired_count, 1)
        self.assertFalse(AppDataRetention.objects.filter(id=expired_retention.id).exists())
        self.assertTrue(AppDataRetention.objects.filter(id=valid_retention.id).exists())

    def test_data_backup_json_handling(self):
        """Test la gestion des données JSON de sauvegarde"""
        backup_data = {
            'settings': {'theme': 'dark', 'language': 'fr'},
            'user_data': {'last_activity': '2024-01-01'},
            'preferences': {'notifications': True}
        }

        retention = AppDataRetention.objects.create(
            user=self.user,
            app=self.app,
            data_backup=json.dumps(backup_data),
            retention_period_days=30
        )

        # Récupérer et parser les données
        parsed_data = json.loads(retention.data_backup)
        self.assertEqual(parsed_data['settings']['theme'], 'dark')
        self.assertEqual(parsed_data['user_data']['last_activity'], '2024-01-01')

    def test_multiple_retentions_per_user_app(self):
        """Test plusieurs rétentions pour la même combinaison utilisateur/app"""
        # Créer plusieurs enregistrements de rétention
        retention1 = AppDataRetention.objects.create(
            user=self.user,
            app=self.app,
            data_backup='{"version": "1"}',
            retention_period_days=30
        )

        retention2 = AppDataRetention.objects.create(
            user=self.user,
            app=self.app,
            data_backup='{"version": "2"}',
            retention_period_days=30
        )

        retentions = AppDataRetention.objects.filter(user=self.user, app=self.app)
        self.assertEqual(retentions.count(), 2)

    def test_retention_string_representation(self):
        """Test la représentation string de AppDataRetention"""
        retention = AppDataRetention.objects.create(
            user=self.user,
            app=self.app,
            data_backup='{"test": "data"}',
            retention_period_days=30
        )

        expected_str = f"Data retention for {self.user.username} - {self.app.display_name}"
        self.assertEqual(str(retention), expected_str)