"""
Tests pour le système de drag & drop des applications
"""
import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.cache import cache
from app_manager.models import App, UserAppSettings
from app_manager.services import UserAppService

User = get_user_model()


class DragDropTestCase(TestCase):
    """Tests pour le drag & drop des applications"""
    
    def setUp(self):
        """Configuration initiale pour les tests"""
        # Créer un utilisateur de test
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Créer des applications de test
        self.apps = []
        app_data = [
            {'code': 'app1', 'display_name': 'Application 1', 'route_path': '/app1/', 'icon_name': 'bi-app'},
            {'code': 'app2', 'display_name': 'Application 2', 'route_path': '/app2/', 'icon_name': 'bi-app'},
            {'code': 'app3', 'display_name': 'Application 3', 'route_path': '/app3/', 'icon_name': 'bi-app'},
            {'code': 'app4', 'display_name': 'Application 4', 'route_path': '/app4/', 'icon_name': 'bi-app'},
        ]
        
        for i, data in enumerate(app_data):
            app = App.objects.create(
                code=data['code'],
                display_name=data['display_name'],
                description=f"Description de {data['display_name']}",
                icon_name=data['icon_name'],
                route_path=data['route_path'],
                order=i,
                is_enabled=True,
                installable=True
            )
            self.apps.append(app)
        
        # Créer les settings utilisateur et activer toutes les apps
        self.user_settings = UserAppSettings.objects.create(user=self.user)
        self.user_settings.enabled_apps.set(self.apps)
        
        # Client de test
        self.client = Client()
        
        # Clear cache
        cache.clear()
    
    def test_user_app_settings_creation(self):
        """Test de création des settings utilisateur"""
        # Test avec un nouvel utilisateur
        new_user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='newpass123'
        )
        
        # Vérifier que les settings sont créés automatiquement
        user_settings = UserAppService.get_or_create_user_settings(new_user)
        self.assertIsNotNone(user_settings)
        self.assertEqual(user_settings.user, new_user)
    
    def test_app_order_update(self):
        """Test de mise à jour de l'ordre des applications"""
        # Ordre initial (vide = ordre par défaut)
        self.assertEqual(self.user_settings.app_order, [])
        
        # Nouveau test d'ordre
        new_order = ['Application 3', 'Application 1', 'Application 4', 'Application 2']
        
        # Mettre à jour l'ordre
        success = self.user_settings.update_app_order(new_order)
        self.assertTrue(success)
        
        # Vérifier que l'ordre a été sauvegardé
        self.user_settings.refresh_from_db()
        self.assertEqual(self.user_settings.app_order, new_order)
    
    def test_get_ordered_enabled_apps(self):
        """Test de récupération des apps dans l'ordre personnalisé"""
        # Définir un ordre personnalisé
        custom_order = ['Application 2', 'Application 4', 'Application 1', 'Application 3']
        self.user_settings.update_app_order(custom_order)
        
        # Récupérer les apps ordonnées
        ordered_apps = self.user_settings.get_ordered_enabled_apps()
        
        # Vérifier que l'ordre est correct
        app_names = [app.display_name for app in ordered_apps]
        self.assertEqual(app_names, custom_order)
    
    def test_get_ordered_apps_with_missing_apps(self):
        """Test avec des apps manquantes dans l'ordre personnalisé"""
        # Ordre partiel (ne contient que 2 apps sur 4)
        partial_order = ['Application 3', 'Application 1']
        self.user_settings.update_app_order(partial_order)
        
        # Récupérer les apps ordonnées
        ordered_apps = self.user_settings.get_ordered_enabled_apps()
        
        # Vérifier que toutes les apps sont présentes
        self.assertEqual(len(ordered_apps), 4)
        
        # Vérifier que les 2 premières suivent l'ordre personnalisé
        app_names = [app.display_name for app in ordered_apps]
        self.assertEqual(app_names[:2], partial_order)
        
        # Les autres apps doivent être ajoutées à la fin
        remaining_apps = app_names[2:]
        self.assertIn('Application 2', remaining_apps)
        self.assertIn('Application 4', remaining_apps)
    
    def test_user_app_service_format_app_data(self):
        """Test du formatage des données d'applications"""
        app = self.apps[0]
        formatted_data = UserAppService._format_app_data(app)
        
        # Vérifier la structure des données
        expected_keys = ['name', 'display_name', 'url', 'icon', 'static_icon', 'color_gradient']
        for key in expected_keys:
            self.assertIn(key, formatted_data)
        
        # Vérifier les valeurs
        self.assertEqual(formatted_data['name'], app.code)
        self.assertEqual(formatted_data['display_name'], app.display_name)
        self.assertEqual(formatted_data['url'], app.route_path + '/')  # Should end with /
        self.assertEqual(formatted_data['icon'], app.icon_name)
    
    def test_get_user_installed_apps(self):
        """Test de récupération des apps installées formatées"""
        # Définir un ordre personnalisé
        custom_order = ['Application 4', 'Application 1', 'Application 3', 'Application 2']
        self.user_settings.update_app_order(custom_order)
        
        # Clear cache pour forcer le rechargement
        cache_key = f"user_installed_apps_{self.user.id}"
        cache.delete(cache_key)
        
        # Récupérer les apps installées
        installed_apps = UserAppService.get_user_installed_apps(self.user)
        
        # Vérifier la structure
        self.assertEqual(len(installed_apps), 4)
        
        # Vérifier l'ordre
        app_names = [app['display_name'] for app in installed_apps]
        self.assertEqual(app_names, custom_order)
        
        # Vérifier la structure de chaque app
        for app_data in installed_apps:
            self.assertIn('display_name', app_data)
            self.assertIn('url', app_data)
            self.assertIn('icon', app_data)


class SaveAppOrderAPITestCase(TestCase):
    """Tests pour l'API de sauvegarde de l'ordre des applications"""
    
    def setUp(self):
        """Configuration initiale pour les tests API"""
        # Créer un utilisateur de test
        self.user = User.objects.create_user(
            username='apitest',
            email='apitest@example.com',
            password='apitest123'
        )
        
        # Créer des applications de test
        self.apps = []
        for i in range(3):
            app = App.objects.create(
                code=f'apiapp{i+1}',
                display_name=f'API App {i+1}',
                description=f'API Test App {i+1}',
                icon_name='bi-app',
                route_path=f'/apiapp{i+1}/',
                order=i,
                is_enabled=True,
                installable=True
            )
            self.apps.append(app)
        
        # Créer les settings utilisateur
        self.user_settings = UserAppSettings.objects.create(user=self.user)
        self.user_settings.enabled_apps.set(self.apps)
        
        # Client de test
        self.client = Client()
        self.client.force_login(self.user)
        
        # URL de l'API
        self.save_order_url = reverse('saas_web:save_app_order')
    
    def test_save_app_order_success(self):
        """Test de sauvegarde réussie de l'ordre des applications"""
        new_order = ['API App 3', 'API App 1', 'API App 2']
        
        response = self.client.post(
            self.save_order_url,
            data=json.dumps({'app_order': new_order}),
            content_type='application/json'
        )
        
        # Vérifier la réponse
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertIn('message', response_data)
        
        # Vérifier que l'ordre a été sauvegardé
        self.user_settings.refresh_from_db()
        self.assertEqual(self.user_settings.app_order[:3], new_order)
    
    def test_save_app_order_invalid_json(self):
        """Test avec des données JSON invalides"""
        response = self.client.post(
            self.save_order_url,
            data='invalid json',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('Invalid JSON', response_data['error'])
    
    def test_save_app_order_invalid_data_type(self):
        """Test avec un type de données incorrect"""
        response = self.client.post(
            self.save_order_url,
            data=json.dumps({'app_order': 'not a list'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('must be a list', response_data['error'])
    
    def test_save_app_order_unauthorized(self):
        """Test sans authentification"""
        # Se déconnecter
        self.client.logout()
        
        response = self.client.post(
            self.save_order_url,
            data=json.dumps({'app_order': ['App 1']}),
            content_type='application/json'
        )
        
        # Doit rediriger vers la page de login
        self.assertEqual(response.status_code, 302)
    
    def test_save_app_order_with_invalid_apps(self):
        """Test avec des noms d'applications invalides"""
        # Inclure des apps qui n'existent pas ou ne sont pas activées
        new_order = ['API App 1', 'Nonexistent App', 'API App 2']
        
        response = self.client.post(
            self.save_order_url,
            data=json.dumps({'app_order': new_order}),
            content_type='application/json'
        )
        
        # Doit réussir mais filtrer les apps invalides
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # Vérifier que seules les apps valides ont été sauvegardées
        self.user_settings.refresh_from_db()
        saved_order = self.user_settings.app_order
        self.assertIn('API App 1', saved_order)
        self.assertIn('API App 2', saved_order)
        self.assertNotIn('Nonexistent App', saved_order)


class DragDropIntegrationTestCase(TestCase):
    """Tests d'intégration pour le système complet de drag & drop"""
    
    def setUp(self):
        """Configuration pour les tests d'intégration"""
        # Créer un utilisateur
        self.user = User.objects.create_user(
            username='integration',
            email='integration@example.com',
            password='integration123'
        )
        
        # Créer plusieurs applications
        self.apps = []
        app_names = ['Teaching', 'Révision', 'Quiz', 'Notes', 'Community']
        for i, name in enumerate(app_names):
            app = App.objects.create(
                code=name.lower(),
                display_name=name,
                description=f'Description de {name}',
                icon_name='bi-app',
                route_path=f'/{name.lower()}/',
                order=i,
                is_enabled=True,
                installable=True
            )
            self.apps.append(app)
        
        # Créer settings utilisateur
        self.user_settings = UserAppSettings.objects.create(user=self.user)
        self.user_settings.enabled_apps.set(self.apps)
        
        self.client = Client()
        self.client.force_login(self.user)
    
    def test_full_drag_drop_workflow(self):
        """Test du workflow complet de drag & drop"""
        # 1. Récupérer l'ordre initial
        initial_apps = UserAppService.get_user_installed_apps(self.user)
        initial_order = [app['display_name'] for app in initial_apps]
        
        # 2. Simuler un drag & drop (inverser l'ordre)
        new_order = list(reversed(initial_order))
        
        # 3. Sauvegarder via l'API
        response = self.client.post(
            reverse('saas_web:save_app_order'),
            data=json.dumps({'app_order': new_order}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # 4. Vérifier que le cache a été invalidé et le nouvel ordre appliqué
        cache_key = f"user_installed_apps_{self.user.id}"
        cache.delete(cache_key)  # Simule l'invalidation du cache
        
        updated_apps = UserAppService.get_user_installed_apps(self.user)
        updated_order = [app['display_name'] for app in updated_apps]
        
        self.assertEqual(updated_order, new_order)
        
        # 5. Vérifier la persistence en base
        self.user_settings.refresh_from_db()
        self.assertEqual(self.user_settings.app_order, new_order)
    
    def test_dashboard_page_with_drag_drop(self):
        """Test que le dashboard charge correctement avec le système de drag & drop"""
        # Définir un ordre personnalisé
        custom_order = ['Community', 'Teaching', 'Quiz', 'Notes', 'Révision']
        self.user_settings.update_app_order(custom_order)
        
        # Accéder au dashboard
        response = self.client.get(reverse('saas_web:dashboard'))
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que le JavaScript drag & drop est présent
        content = response.content.decode('utf-8')
        self.assertIn('dashboard.js', content)
        self.assertIn('apps-grid-container', content)
        self.assertIn('app-link', content)
        
        # Vérifier que les apps sont dans le bon ordre dans le HTML
        # (Note: ce test est basique car l'ordre exact dans le HTML dépend du template)
        for app_name in custom_order:
            self.assertIn(app_name, content)
    
    def test_multiple_users_independent_orders(self):
        """Test que différents utilisateurs ont des ordres indépendants"""
        # Créer un second utilisateur
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='user2123'
        )
        
        user2_settings = UserAppSettings.objects.create(user=user2)
        user2_settings.enabled_apps.set(self.apps)
        
        # Définir des ordres différents
        order1 = ['Teaching', 'Quiz', 'Notes', 'Community', 'Révision']
        order2 = ['Révision', 'Community', 'Teaching', 'Notes', 'Quiz']
        
        self.user_settings.update_app_order(order1)
        user2_settings.update_app_order(order2)
        
        # Vérifier que chaque utilisateur a son propre ordre
        apps1 = UserAppService.get_user_installed_apps(self.user)
        apps2 = UserAppService.get_user_installed_apps(user2)
        
        order1_result = [app['display_name'] for app in apps1]
        order2_result = [app['display_name'] for app in apps2]
        
        self.assertEqual(order1_result, order1)
        self.assertEqual(order2_result, order2)
        self.assertNotEqual(order1_result, order2_result)


class DragDropErrorHandlingTestCase(TestCase):
    """Tests de gestion d'erreurs pour le drag & drop"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='errortest',
            email='errortest@example.com',
            password='errortest123'
        )
        self.client = Client()
        self.client.force_login(self.user)
    
    def test_save_order_with_no_user_settings(self):
        """Test quand l'utilisateur n'a pas encore de settings"""
        # L'utilisateur n'a pas de UserAppSettings créé
        
        response = self.client.post(
            reverse('saas_web:save_app_order'),
            data=json.dumps({'app_order': ['App1', 'App2']}),
            content_type='application/json'
        )
        
        # Doit créer automatiquement les settings
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que les settings ont été créés
        user_settings = UserAppSettings.objects.filter(user=self.user).first()
        self.assertIsNotNone(user_settings)
    
    def test_save_order_empty_list(self):
        """Test avec une liste vide"""
        UserAppSettings.objects.create(user=self.user)
        
        response = self.client.post(
            reverse('saas_web:save_app_order'),
            data=json.dumps({'app_order': []}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])