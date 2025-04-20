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
    os.environ.setdefault('DB_NAME', 'test_db_linguify')
    os.environ.setdefault('DB_USER', 'postgres')
    os.environ.setdefault('DB_PASSWORD', 'postgres')
    os.environ.setdefault('DB_HOST', 'localhost')
    os.environ.setdefault('DB_PORT', '5432')
    os.environ.setdefault('AUTH0_DOMAIN', 'test.auth0.com')
    os.environ.setdefault('AUTH0_CLIENT_ID', 'test_client_id')
    os.environ.setdefault('AUTH0_CLIENT_SECRET', 'test_client_secret')
    os.environ.setdefault('AUTH0_AUDIENCE', 'https://test-api')
    
    django.setup()