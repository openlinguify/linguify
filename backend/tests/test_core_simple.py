"""
Tests simplifiés pour les fonctionnalités de base de l'application.
Ces tests n'importent pas directement les modèles pour éviter les conflits.
"""
import pytest
from django.conf import settings


@pytest.mark.django_db
class TestCoreSettings:
    """Tests pour vérifier les paramètres de base de l'application Django."""
    
    def test_installed_apps(self):
        """Vérifie que les applications nécessaires sont bien installées."""
        # Vérifier que les applications principales sont installées
        assert 'django.contrib.admin' in settings.INSTALLED_APPS
        assert 'django.contrib.auth' in settings.INSTALLED_APPS
        assert 'django.contrib.contenttypes' in settings.INSTALLED_APPS
        assert 'django.contrib.sessions' in settings.INSTALLED_APPS
        assert 'django.contrib.messages' in settings.INSTALLED_APPS
        assert 'django.contrib.staticfiles' in settings.INSTALLED_APPS
        
        # Vérifier que les applications de notre projet sont installées
        necessary_apps = [
            'rest_framework',
            'apps.authentication',
            'apps.course',
        ]
        
        for app in necessary_apps:
            installed = False
            for installed_app in settings.INSTALLED_APPS:
                if installed_app == app or installed_app.endswith(f'.{app}'):
                    installed = True
                    break
            assert installed, f"L'application {app} n'est pas installée"
    
    def test_database_config(self):
        """Vérifie que la configuration de la base de données est correcte."""
        # Vérifier que la configuration de la base de données est bien définie
        assert 'default' in settings.DATABASES
        
        # En mode test, Django utilise généralement une base de données in-memory SQLite
        # à moins que nous n'ayons configuré une base de données spécifique pour les tests
        db_config = settings.DATABASES['default']
        assert db_config is not None
        
        # Si nous utilisons une base de données PostgreSQL
        if 'postgresql' in db_config.get('ENGINE', ''):
            assert 'NAME' in db_config
            assert 'USER' in db_config
            assert 'PASSWORD' in db_config
            assert 'HOST' in db_config
            assert 'PORT' in db_config
    
    def test_rest_framework_settings(self):
        """Vérifie que les paramètres de REST Framework sont correctement configurés."""
        # Vérifier que REST_FRAMEWORK est configuré
        assert hasattr(settings, 'REST_FRAMEWORK')
        
        # Vérifier les paramètres courants de REST Framework
        rest_settings = getattr(settings, 'REST_FRAMEWORK', {})
        
        # Les modèles courants que nous pourrions vouloir vérifier
        pagination_keys = [
            'DEFAULT_PAGINATION_CLASS', 
            'PAGE_SIZE'
        ]
        
        # Si la pagination est configurée, vérifier qu'elle est correctement définie
        if any(key in rest_settings for key in pagination_keys):
            # Si DEFAULT_PAGINATION_CLASS est défini, PAGE_SIZE devrait aussi l'être
            if 'DEFAULT_PAGINATION_CLASS' in rest_settings:
                assert 'PAGE_SIZE' in rest_settings
                assert isinstance(rest_settings['PAGE_SIZE'], int)