import os
import sys
import django

# Ajoutez le chemin vers le répertoire backend
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'apps'))

def pytest_configure():
    """Configure Django for pytest"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    os.environ.setdefault('DJANGO_SECRET_KEY', 'test_secret_key')

    # Use SQLite for testing instead of PostgreSQL
    os.environ.setdefault('TEST_MODE', 'True')

    # Auth0 test settings
    os.environ.setdefault('AUTH0_DOMAIN', 'test.auth0.com')
    os.environ.setdefault('AUTH0_CLIENT_ID', 'test_client_id')
    os.environ.setdefault('AUTH0_CLIENT_SECRET', 'test_client_secret')
    os.environ.setdefault('AUTH0_AUDIENCE', 'https://test-api')

    django.setup()