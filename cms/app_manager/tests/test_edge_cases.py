"""
Tests pour les cas limites et gestion d'erreurs app_manager
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection
from django.urls import reverse
from unittest.mock import patch, Mock, MagicMock
import json
from io import StringIO
import sys

from ..models import App, UserAppSettings, AppDataRetention
from ..services.cache_service import UserAppCacheService
from ..services.user_app_service import UserAppService

User = get_user_model()


class EdgeCasesModelTest(TestCase):
    """Tests pour les cas limites des modèles"""

    def setUp(self):
        """Configuration des tests"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_app_creation_with_empty_strings(self):
        """Test la création d'app avec des chaînes vides"""
        with self.assertRaises((ValidationError, IntegrityError)):
            App.objects.create(
                code='',  # Code vide
                display_name='Test App',
                description='',
                icon_name='',
                route_path='',
                category=''
            )

    def test_app_creation_with_very_long_strings(self):
        """Test la création d'app avec des chaînes très longues"""
        long_string = 'x' * 1000

        with self.assertRaises(ValidationError):
            app = App(
                code=long_string,  # Trop long pour le code
                display_name='Test App',
                description=long_string,
                icon_name='TestIcon',
                route_path='/test',
                category='productivity'
            )
            app.full_clean()

    def test_app_with_null_values(self):
        """Test la gestion des valeurs null"""
        # Les champs requis ne doivent pas accepter null
        with self.assertRaises((ValidationError, IntegrityError)):
            App.objects.create(
                code=None,
                display_name=None,
                description='Test',
                icon_name='TestIcon',
                route_path='/test',
                category='productivity'
            )

    def test_user_app_settings_with_deleted_user(self):
        """Test les paramètres d'app avec utilisateur supprimé"""
        user_settings = UserAppSettings.objects.create(user=self.user)

        # Supprimer l'utilisateur
        user_id = self.user.id
        self.user.delete()

        # Les paramètres doivent être supprimés en cascade
        self.assertFalse(UserAppSettings.objects.filter(user_id=user_id).exists())

    def test_user_app_settings_with_corrupted_data(self):
        """Test les paramètres avec données corrompues"""
        user_settings = UserAppSettings.objects.create(user=self.user)

        # Simuler des données corrompues dans enabled_apps
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE app_manager_userappsettings SET enabled_apps = %s WHERE id = %s",
                ['invalid_json_data', user_settings.id]
            )

        # Recharger les paramètres
        user_settings.refresh_from_db()

        # La méthode get_enabled_app_codes devrait gérer les données corrompues
        try:
            enabled_codes = user_settings.get_enabled_app_codes()
            # Devrait retourner une liste vide ou gérer l'erreur gracieusement
            self.assertIsInstance(enabled_codes, list)
        except Exception as e:
            self.fail(f"get_enabled_app_codes should handle corrupted data: {e}")

    def test_enable_app_with_special_characters(self):
        """Test l'activation d'apps avec caractères spéciaux"""
        # Créer une app avec des caractères spéciaux
        app = App.objects.create(
            code='special_äpp-123',
            display_name='Special Äpp',
            description='App with special chars',
            icon_name='SpecialIcon',
            route_path='/special',
            category='productivity'
        )

        user_settings = UserAppSettings.objects.create(user=self.user)
        result = user_settings.enable_app('special_äpp-123')

        self.assertTrue(result)
        self.assertTrue(user_settings.is_app_enabled('special_äpp-123'))

    def test_massive_app_activation(self):
        """Test l'activation d'un grand nombre d'apps"""
        # Créer 1000 apps
        apps = []
        for i in range(1000):
            apps.append(App(
                code=f'massive_app_{i}',
                display_name=f'Massive App {i}',
                category='productivity'
            ))

        App.objects.bulk_create(apps)

        user_settings = UserAppSettings.objects.create(user=self.user)

        # Activer toutes les apps
        for i in range(1000):
            user_settings.enable_app(f'massive_app_{i}')

        # Vérifier que toutes sont activées
        enabled_codes = user_settings.get_enabled_app_codes()
        self.assertEqual(len(enabled_codes), 1000)


class EdgeCasesAPITest(TestCase):
    """Tests pour les cas limites des APIs"""

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
            category='productivity'
        )

    def test_api_with_invalid_json(self):
        """Test l'API avec JSON invalide"""
        self.client.login(username='testuser', password='testpass123')

        response = self.client.post(
            reverse('app_manager:api_user_app_settings'),
            data='{"invalid": json}',  # JSON malformé
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

    def test_api_with_huge_payload(self):
        """Test l'API avec payload énorme"""
        self.client.login(username='testuser', password='testpass123')

        # Créer un payload très large
        huge_data = {
            'enabled_apps': ['test_app'] * 10000,  # Liste énorme
            'large_field': 'x' * 100000  # Champ très large
        }

        response = self.client.post(
            reverse('app_manager:api_user_app_settings'),
            data=json.dumps(huge_data),
            content_type='application/json'
        )

        # Devrait soit accepter soit rejeter gracieusement
        self.assertIn(response.status_code, [200, 400, 413])

    def test_concurrent_api_requests(self):
        """Test les requêtes API concurrentes"""
        self.client.login(username='testuser', password='testpass123')

        import threading
        import time

        results = []
        errors = []

        def make_request():
            try:
                response = self.client.post(
                    reverse('app_manager:api_app_toggle', kwargs={'app_id': self.app.id}),
                    content_type='application/json'
                )
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))

        # Lancer 10 requêtes simultanées
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()

        # Attendre que tous les threads se terminent
        for thread in threads:
            thread.join()

        # Vérifier qu'il n'y a pas d'erreurs critiques
        self.assertEqual(len(errors), 0)
        self.assertTrue(all(status in [200, 201, 400, 404] for status in results))

    def test_api_with_missing_csrf_token(self):
        """Test l'API sans token CSRF"""
        self.client.login(username='testuser', password='testpass123')

        # Désactiver la protection CSRF pour ce test
        response = self.client.post(
            reverse('app_manager:api_app_toggle', kwargs={'app_id': self.app.id}),
            content_type='application/json',
            HTTP_X_CSRFTOKEN=''  # Token vide
        )

        # La réponse dépend de la configuration CSRF
        self.assertIn(response.status_code, [200, 403])

    def test_api_rate_limiting_simulation(self):
        """Test la simulation de limitation de taux"""
        self.client.login(username='testuser', password='testpass123')

        # Faire beaucoup de requêtes rapidement
        responses = []
        for _ in range(100):
            response = self.client.get(reverse('app_manager:api_user_apps_fast'))
            responses.append(response.status_code)

        # Toutes les requêtes devraient réussir (pas de rate limiting implémenté)
        self.assertTrue(all(status == 200 for status in responses))


class EdgeCasesCacheTest(TestCase):
    """Tests pour les cas limites du cache"""

    def setUp(self):
        """Configuration des tests"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    @patch('django.core.cache.cache.get')
    @patch('django.core.cache.cache.set')
    def test_cache_failure_graceful_degradation(self, mock_set, mock_get):
        """Test la dégradation gracieuse en cas d'échec du cache"""
        # Simuler un échec du cache
        mock_get.side_effect = Exception("Cache connection failed")
        mock_set.side_effect = Exception("Cache connection failed")

        # Les fonctions de cache doivent continuer à fonctionner sans cache
        apps = UserAppCacheService.get_user_apps(self.user)

        self.assertIsNotNone(apps)
        self.assertIsInstance(apps, list)

    @patch('django.core.cache.cache.get')
    def test_cache_with_corrupted_data(self, mock_get):
        """Test le cache avec données corrompues"""
        # Simuler des données corrompues dans le cache
        mock_get.return_value = "corrupted_data_not_json"

        # Devrait retourner None et recalculer
        apps = UserAppCacheService.get_user_apps(self.user)

        self.assertIsNotNone(apps)
        self.assertIsInstance(apps, list)

    def test_cache_memory_pressure(self):
        """Test le cache sous pression mémoire"""
        # Créer beaucoup d'utilisateurs et remplir le cache
        users = []
        for i in range(100):
            user = User.objects.create_user(
                username=f'user_{i}',
                email=f'user_{i}@example.com',
                password='password'
            )
            users.append(user)

        # Remplir le cache pour tous les utilisateurs
        for user in users:
            UserAppCacheService.get_user_apps(user)

        # Le cache devrait continuer à fonctionner
        first_user_apps = UserAppCacheService.get_user_apps(users[0])
        self.assertIsNotNone(first_user_apps)


class EdgeCasesErrorHandlingTest(TestCase):
    """Tests pour la gestion d'erreurs"""

    def setUp(self):
        """Configuration des tests"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    @patch('app_manager.models.app_manager_models.App.objects.get')
    def test_database_connection_error(self, mock_get):
        """Test les erreurs de connexion à la base de données"""
        mock_get.side_effect = Exception("Database connection lost")

        try:
            UserAppService.toggle_app(self.user, 1)
        except Exception as e:
            # L'erreur devrait être gérée gracieusement
            self.assertIn("Database", str(e))

    def test_memory_exhaustion_simulation(self):
        """Test la simulation d'épuisement mémoire"""
        # Créer une situation qui pourrait épuiser la mémoire
        try:
            # Créer un grand nombre d'objets en mémoire
            large_list = []
            for i in range(10000):
                large_list.append({
                    'data': 'x' * 1000,
                    'index': i
                })

            # Tenter d'utiliser les services avec beaucoup d'objets en mémoire
            user_settings = UserAppSettings.objects.create(user=self.user)
            result = user_settings.enable_app('test_app')

            # Même avec la pression mémoire, les opérations de base devraient fonctionner
            self.assertIsInstance(result, bool)

        except MemoryError:
            self.skipTest("Memory exhaustion test skipped due to system limitations")

    def test_unicode_handling_edge_cases(self):
        """Test la gestion des cas limites Unicode"""
        # Caractères Unicode complexes
        unicode_strings = [
            '🚀🎉💻',  # Emojis
            'مرحبا',     # Arabe
            '你好',      # Chinois
            'Здравствуй', # Russe
            '🔥💯🚀',    # Emojis multiples
        ]

        for unicode_str in unicode_strings:
            try:
                app = App.objects.create(
                    code=f'unicode_app_{hash(unicode_str)}',
                    display_name=unicode_str,
                    category='productivity'
                )

                # Vérifier que l'Unicode est correctement géré
                self.assertEqual(app.display_name, unicode_str)
                self.assertEqual(str(app), unicode_str)

            except Exception as e:
                self.fail(f"Unicode string '{unicode_str}' should be handled: {e}")

    def test_sql_injection_prevention(self):
        """Test la prévention d'injection SQL"""
        malicious_inputs = [
            "'; DROP TABLE app_manager_app; --",
            "1' OR '1'='1",
            "'; UPDATE app_manager_app SET is_enabled=0; --",
            "<script>alert('xss')</script>",
        ]

        user_settings = UserAppSettings.objects.create(user=self.user)

        for malicious_input in malicious_inputs:
            try:
                # Ces inputs ne devraient pas causer d'injection SQL
                result = user_settings.enable_app(malicious_input)

                # L'opération devrait échouer gracieusement
                self.assertFalse(result)

                # Vérifier que l'app malicieuse n'a pas été créée
                self.assertFalse(
                    App.objects.filter(code=malicious_input).exists()
                )

            except Exception as e:
                # Les erreurs devraient être des ValidationError, pas des erreurs SQL
                self.assertNotIn("syntax error", str(e).lower())
                self.assertNotIn("sql", str(e).lower())

    def test_file_system_errors(self):
        """Test les erreurs du système de fichiers"""
        with patch('os.path.exists', side_effect=OSError("Permission denied")):
            try:
                # Les opérations qui dépendent du système de fichiers
                from ..services.app_icon_service import AppIconService
                app = App.objects.create(
                    code='fs_test_app',
                    display_name='FS Test App',
                    category='productivity'
                )

                # Devrait gérer l'erreur gracieusement
                icon_exists = AppIconService.icon_exists(app)
                self.assertIsInstance(icon_exists, bool)

            except ImportError:
                self.skipTest("AppIconService not available")
            except Exception as e:
                # L'erreur devrait être gérée, pas propagée
                self.assertNotIn("Permission denied", str(e))