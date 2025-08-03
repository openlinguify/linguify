"""
Django settings configuration view and tests
"""
from django.test import TestCase
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render


def test_settings(request):
    """Django view to display settings information"""
    context = {
        'debug': settings.DEBUG,
        'secret_key_length': len(settings.SECRET_KEY) if settings.SECRET_KEY else 0,
        'database_engine': settings.DATABASES['default'].get('ENGINE', 'Not configured'),
        'database_name': settings.DATABASES['default'].get('NAME', 'Not configured'),
        'installed_apps_count': len(settings.INSTALLED_APPS),
        'language_code': settings.LANGUAGE_CODE,
        'time_zone': settings.TIME_ZONE,
    }
    
    return HttpResponse(f"""
    <html>
    <head><title>Django Settings Test</title></head>
    <body>
        <h1>Django Settings Information</h1>
        <ul>
            <li>DEBUG: {context['debug']}</li>
            <li>SECRET_KEY length: {context['secret_key_length']}</li>
            <li>Database Engine: {context['database_engine']}</li>
            <li>Database Name: {context['database_name']}</li>
            <li>Installed Apps Count: {context['installed_apps_count']}</li>
            <li>Language Code: {context['language_code']}</li>
            <li>Time Zone: {context['time_zone']}</li>
        </ul>
    </body>
    </html>
    """)


class SettingsTest(TestCase):
    """Test Django settings configuration"""
    
    def test_database_configuration(self):
        """Test database settings are valid"""
        db_config = settings.DATABASES['default']
        self.assertIn('ENGINE', db_config)
        self.assertIn('NAME', db_config)
        
    def test_debug_setting(self):
        """Test DEBUG setting is configured"""
        self.assertIn('DEBUG', dir(settings))
        
    def test_secret_key_exists(self):
        """Test SECRET_KEY is configured"""
        self.assertTrue(settings.SECRET_KEY)
        self.assertGreater(len(settings.SECRET_KEY), 10)