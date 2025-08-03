"""
Basic backend tests
"""
from django.test import TestCase
from django.conf import settings


class BackendBasicTest(TestCase):
    """Basic backend functionality tests"""
    
    def test_settings_configured(self):
        """Test that Django settings are properly configured"""
        self.assertTrue(hasattr(settings, 'SECRET_KEY'))
        self.assertTrue(hasattr(settings, 'DATABASES'))
        
    def test_apps_installed(self):
        """Test that required apps are in INSTALLED_APPS"""
        installed_apps = settings.INSTALLED_APPS
        required_apps = [
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'rest_framework',
        ]
        
        for app in required_apps:
            self.assertIn(app, installed_apps, f"Required app {app} not found in INSTALLED_APPS")