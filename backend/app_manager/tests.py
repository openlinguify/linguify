"""
Tests pour le module app_manager
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import App, UserAppSettings

User = get_user_model()


class AppModelTest(TestCase):
    """Tests pour le modèle App"""
    
    def setUp(self):
        """Configuration des tests"""
        self.app = App.objects.create(
            code='test_app',
            display_name='Test Application',
            description='Application de test',
            icon_name='TestIcon',
            route_path='/test',
            category='Test'
        )
    
    def test_app_creation(self):
        """Test la création d'une application"""
        self.assertEqual(self.app.code, 'test_app')
        self.assertEqual(self.app.display_name, 'Test Application')
        self.assertTrue(self.app.is_enabled)
    
    def test_app_str_method(self):
        """Test la méthode __str__ de App"""
        self.assertEqual(str(self.app), 'Test Application')


class UserAppSettingsTest(TestCase):
    """Tests pour le modèle UserAppSettings"""
    
    def setUp(self):
        """Configuration des tests"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.app = App.objects.create(
            code='test_app',
            display_name='Test Application',
            description='Application de test',
            icon_name='TestIcon',
            route_path='/test',
            category='Test'
        )
        self.user_settings = UserAppSettings.objects.create(user=self.user)
    
    def test_user_settings_creation(self):
        """Test la création des paramètres utilisateur"""
        self.assertEqual(self.user_settings.user, self.user)
        self.assertEqual(self.user_settings.enabled_apps.count(), 0)
    
    def test_enable_app(self):
        """Test l'activation d'une application"""
        result = self.user_settings.enable_app('test_app')
        self.assertTrue(result)
        self.assertTrue(self.user_settings.is_app_enabled('test_app'))
    
    def test_disable_app(self):
        """Test la désactivation d'une application"""
        self.user_settings.enable_app('test_app')
        result = self.user_settings.disable_app('test_app')
        self.assertTrue(result)
        self.assertFalse(self.user_settings.is_app_enabled('test_app'))
    
    def test_get_enabled_app_codes(self):
        """Test la récupération des codes d'apps activées"""
        self.user_settings.enable_app('test_app')
        enabled_codes = self.user_settings.get_enabled_app_codes()
        self.assertIn('test_app', enabled_codes)


class AppSystemIntegrationTest(TestCase):
    """Tests d'intégration du système d'applications"""
    
    def test_system_health_check(self):
        """Test de santé basique du système"""
        # Vérifier que le système peut créer des apps
        app_count_before = App.objects.count()
        App.objects.create(
            code='health_check',
            display_name='Health Check App',
            description='Test de santé',
            icon_name='HealthIcon',
            route_path='/health',
            category='System'
        )
        app_count_after = App.objects.count()
        self.assertEqual(app_count_after, app_count_before + 1)
        
        # Vérifier que le système peut créer des utilisateurs
        user_count_before = User.objects.count()
        User.objects.create_user(
            username='healthuser',
            email='health@example.com',
            password='healthpass123'
        )
        user_count_after = User.objects.count()
        self.assertEqual(user_count_after, user_count_before + 1)