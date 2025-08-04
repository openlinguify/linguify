"""
Pytest configuration for backend tests
Note: public_web tests moved to portal project
"""
import pytest
import django
from django.conf import settings
from django.test.utils import get_runner
from django.apps import apps


@pytest.fixture(scope='session')
def django_db_setup():
    """Set up the Django database for testing"""
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }


@pytest.fixture
def mock_apps_data():
    """Fixture providing mock app data for tests"""
    return [
        {
            'name': 'Learning',
            'slug': 'course',
            'category': 'Education/Language Learning',
            'summary': 'Interactive language lessons and exercises',
            'description': 'Comprehensive language learning platform.',
            'icon': 'GraduationCap',
            'route': '/learning',
            'menu_order': 1,
            'version': '1.0.0',
            'author': 'Linguify Team',
            'django_app': 'apps.course'
        },
        {
            'name': 'Revision',
            'slug': 'revision',
            'category': 'Education/Memory',
            'summary': 'Spaced repetition system with smart flashcards',
            'description': 'Advanced spaced repetition system.',
            'icon': 'Cards',
            'route': '/revision',
            'menu_order': 2,
            'version': '1.0.0',
            'author': 'Linguify Team',
            'django_app': 'apps.revision'
        },
        {
            'name': 'Notebook',
            'slug': 'notebook',
            'category': 'Productivity',
            'summary': 'Centralized note-taking with intelligent organization',
            'description': 'Advanced note-taking and organization system.',
            'icon': 'Journal',
            'route': '/notebook',
            'menu_order': 3,
            'version': '1.0.0',
            'author': 'Linguify Team',
            'django_app': 'apps.notebook'
        }
    ]


@pytest.fixture
def mock_manifest_data():
    """Fixture providing mock manifest data for tests"""
    return {
        'course': {
            'app_name': 'course',
            'manifest': {
                'name': 'Learning',
                'version': '1.0.0',
                'category': 'Education/Language Learning',
                'summary': 'Interactive language lessons and exercises',
                'installable': True,
                'application': True,
                'frontend_components': {
                    'main_component': 'LearningView',
                    'route': '/learning',
                    'icon': 'GraduationCap',
                    'menu_order': 1,
                }
            },
            'django_app': 'apps.course'
        },
        'revision': {
            'app_name': 'revision',
            'manifest': {
                'name': 'Revision',
                'version': '1.0.0',
                'category': 'Education/Memory',
                'summary': 'Spaced repetition system with smart flashcards',
                'installable': True,
                'application': True,
                'frontend_components': {
                    'main_component': 'RevisionView',
                    'route': '/revision',
                    'icon': 'Cards',
                    'menu_order': 2,
                }
            },
            'django_app': 'apps.revision'
        }
    }