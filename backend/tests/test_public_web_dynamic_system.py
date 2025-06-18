"""
Tests for the dynamic app management system in public_web
"""
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from django.test import TestCase, RequestFactory, override_settings
from django.urls import reverse
from django.template import Context, Template
from django.http import Http404

from public_web.utils import AppManifestParser, manifest_parser
from public_web.views import DynamicAppDetailView, DynamicAppsListView
from public_web.templatetags.app_tags import dynamic_apps_dropdown, get_app_url, translate_app_name


class AppManifestParserTest(TestCase):
    """Test the manifest parser functionality"""
    
    def setUp(self):
        self.parser = AppManifestParser()
        
        # Create a temporary directory structure for testing
        self.temp_dir = tempfile.mkdtemp()
        self.apps_dir = Path(self.temp_dir) / 'apps'
        self.apps_dir.mkdir()
        
        # Mock the apps directory path
        self.parser.apps_dir = self.apps_dir
        
    def tearDown(self):
        # Clean up temporary files
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def create_test_manifest(self, app_name, manifest_content):
        """Helper to create a test manifest file"""
        app_dir = self.apps_dir / app_name
        app_dir.mkdir()
        
        manifest_file = app_dir / '__manifest__.py'
        manifest_file.write_text(f"__manifest__ = {manifest_content}")
        
        return manifest_file
    
    def test_load_manifest_valid(self):
        """Test loading a valid manifest"""
        manifest_content = """{
            'name': 'Test App',
            'version': '1.0.0',
            'installable': True,
            'application': True
        }"""
        
        self.create_test_manifest('test_app', manifest_content)
        
        manifests = self.parser.get_all_manifests()
        
        self.assertIn('test_app', manifests)
        self.assertEqual(manifests['test_app']['manifest']['name'], 'Test App')
        self.assertEqual(manifests['test_app']['app_name'], 'test_app')
    
    def test_load_manifest_not_installable(self):
        """Test that non-installable apps are excluded"""
        manifest_content = """{
            'name': 'Test App',
            'version': '1.0.0',
            'installable': False
        }"""
        
        self.create_test_manifest('test_app', manifest_content)
        
        manifests = self.parser.get_all_manifests()
        
        self.assertNotIn('test_app', manifests)
    
    def test_get_public_apps(self):
        """Test getting public apps with frontend components"""
        manifest_content = """{
            'name': 'Public App',
            'version': '1.0.0',
            'category': 'Education',
            'summary': 'A test app',
            'description': 'Test description',
            'installable': True,
            'application': True,
            'frontend_components': {
                'icon': 'book',
                'route': '/test',
                'menu_order': 1
            }
        }"""
        
        self.create_test_manifest('public_app', manifest_content)
        
        public_apps = self.parser.get_public_apps()
        
        self.assertEqual(len(public_apps), 1)
        app = public_apps[0]
        self.assertEqual(app['name'], 'Public App')
        self.assertEqual(app['slug'], 'public_app')
        self.assertEqual(app['icon'], 'book')
        self.assertEqual(app['menu_order'], 1)
    
    def test_get_public_apps_ordering(self):
        """Test that public apps are ordered by menu_order"""
        # Create apps with different menu orders
        apps_data = [
            ('app_a', {'menu_order': 3}),
            ('app_b', {'menu_order': 1}),
            ('app_c', {'menu_order': 2})
        ]
        
        for app_name, frontend_data in apps_data:
            manifest_content = f"""{{
                'name': '{app_name.title()}',
                'version': '1.0.0',
                'installable': True,
                'application': True,
                'frontend_components': {frontend_data}
            }}"""
            self.create_test_manifest(app_name, manifest_content)
        
        public_apps = self.parser.get_public_apps()
        
        # Should be ordered by menu_order: app_b (1), app_c (2), app_a (3)
        self.assertEqual([app['slug'] for app in public_apps], ['app_b', 'app_c', 'app_a'])
    
    def test_get_app_by_slug(self):
        """Test getting a specific app by slug"""
        manifest_content = """{
            'name': 'Test App',
            'version': '1.0.0',
            'installable': True,
            'application': True,
            'frontend_components': {'icon': 'test'}
        }"""
        
        self.create_test_manifest('test_app', manifest_content)
        
        app = self.parser.get_app_by_slug('test_app')
        
        self.assertIsNotNone(app)
        self.assertEqual(app['name'], 'Test App')
        self.assertEqual(app['slug'], 'test_app')
        
        # Test non-existent app
        app = self.parser.get_app_by_slug('non_existent')
        self.assertIsNone(app)
    
    def test_cache_functionality(self):
        """Test that manifests are cached properly"""
        manifest_content = """{
            'name': 'Cached App',
            'version': '1.0.0',
            'installable': True
        }"""
        
        self.create_test_manifest('cached_app', manifest_content)
        
        # First call should load from filesystem
        manifests1 = self.parser.get_all_manifests()
        
        # Second call should use cache
        manifests2 = self.parser.get_all_manifests()
        
        self.assertEqual(manifests1, manifests2)
        
        # Clear cache and verify it reloads
        self.parser.clear_cache()
        manifests3 = self.parser.get_all_manifests()
        
        self.assertEqual(manifests1, manifests3)


class DynamicViewsTest(TestCase):
    """Test the dynamic views"""
    
    def setUp(self):
        self.factory = RequestFactory()
        
    def test_dynamic_apps_list_view(self):
        """Test the dynamic apps list view"""
        mock_apps = [
            {
                'name': 'Test App 1',
                'slug': 'test_app_1',
                'summary': 'Test summary 1',
                'category': 'Education',
                'version': '1.0.0'
            },
            {
                'name': 'Test App 2',
                'slug': 'test_app_2',
                'summary': 'Test summary 2',
                'category': 'Productivity',
                'version': '2.0.0'
            }
        ]
        
        with patch('public_web.views.manifest_parser.get_public_apps', return_value=mock_apps):
            request = self.factory.get('/apps/')
            view = DynamicAppsListView()
            response = view.get(request)
            
            self.assertEqual(response.status_code, 200)
    
    def test_dynamic_app_detail_view_existing_app(self):
        """Test the dynamic app detail view for existing app"""
        mock_app = {
            'name': 'Test App',
            'slug': 'test_app',
            'summary': 'Test summary',
            'category': 'Education',
            'version': '1.0.0',
            'description': 'Test description'
        }
        
        with patch('public_web.views.manifest_parser.get_app_by_slug', return_value=mock_app):
            request = self.factory.get('/apps/test_app/')
            view = DynamicAppDetailView()
            response = view.get(request, app_slug='test_app')
            
            self.assertEqual(response.status_code, 200)
    
    def test_dynamic_app_detail_view_non_existent_app(self):
        """Test the dynamic app detail view for non-existent app"""
        with patch('public_web.views.manifest_parser.get_app_by_slug', return_value=None):
            request = self.factory.get('/apps/non_existent/')
            view = DynamicAppDetailView()
            
            with self.assertRaises(Http404):
                view.get(request, app_slug='non_existent')


class TemplateTagsTest(TestCase):
    """Test the custom template tags"""
    
    def test_dynamic_apps_dropdown(self):
        """Test the dynamic apps dropdown template tag"""
        mock_apps = [
            {
                'name': 'Test App',
                'slug': 'test_app',
                'icon': 'book'
            }
        ]
        
        with patch('public_web.templatetags.app_tags.manifest_parser.get_public_apps', return_value=mock_apps):
            result = dynamic_apps_dropdown()
            
            self.assertEqual(result['apps'], mock_apps)
    
    def test_get_app_url_valid(self):
        """Test getting URL for valid app"""
        with patch('public_web.templatetags.app_tags.reverse') as mock_reverse:
            mock_reverse.return_value = '/apps/test/'
            
            url = get_app_url('test_app')
            
            self.assertEqual(url, '/apps/test/')
            mock_reverse.assert_called_once_with('public_web:dynamic_app_detail', kwargs={'app_slug': 'test_app'})
    
    def test_get_app_url_invalid(self):
        """Test getting URL for invalid app (should return #)"""
        with patch('public_web.templatetags.app_tags.reverse', side_effect=Exception):
            url = get_app_url('invalid_app')
            
            self.assertEqual(url, '#')
    
    def test_translate_app_name(self):
        """Test app name translation filter"""
        # Test that the filter calls Django's translation function
        with patch('public_web.templatetags.app_tags._') as mock_gettext:
            mock_gettext.return_value = 'Translated Name'
            
            result = translate_app_name('Test App')
            
            self.assertEqual(result, 'Translated Name')
            mock_gettext.assert_called_once_with('Test App')


class IntegrationTest(TestCase):
    """Integration tests for the dynamic system"""
    
    def test_template_rendering(self):
        """Test that templates render correctly with templatetags"""
        mock_apps = [
            {
                'name': 'Test App',
                'slug': 'test_app',
                'icon': 'book'
            }
        ]
        
        template_content = """
        {% load app_tags %}
        {% dynamic_apps_dropdown %}
        """
        
        with patch('public_web.templatetags.app_tags.manifest_parser.get_public_apps', return_value=mock_apps):
            template = Template(template_content)
            context = Context({})
            
            # Should not raise an exception
            rendered = template.render(context)
            self.assertIsInstance(rendered, str)
    
    def test_url_routing(self):
        """Test that URL routing works for dynamic apps"""
        # This would test the actual URL patterns, but since we're in a unit test
        # environment, we'll verify the URL pattern exists
        from public_web.urls import urlpatterns
        
        dynamic_pattern = None
        for pattern in urlpatterns:
            if hasattr(pattern, 'pattern') and 'app_slug' in str(pattern.pattern):
                dynamic_pattern = pattern
                break
        
        self.assertIsNotNone(dynamic_pattern, "Dynamic app URL pattern should exist")


class GlobalManifestParserTest(TestCase):
    """Test the global manifest parser instance"""
    
    def test_global_instance_exists(self):
        """Test that the global manifest parser instance exists"""
        from public_web.utils import manifest_parser
        
        self.assertIsInstance(manifest_parser, AppManifestParser)
    
    def test_clear_cache_method(self):
        """Test the clear cache functionality"""
        # Store original cached value
        original_cache = manifest_parser._cached_manifests
        
        # Set some cache
        manifest_parser._cached_manifests = {'test': 'data'}
        
        # Clear cache
        manifest_parser.clear_cache()
        
        # Verify cache is cleared
        self.assertIsNone(manifest_parser._cached_manifests)
        
        # Restore original state
        manifest_parser._cached_manifests = original_cache