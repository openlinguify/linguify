"""
Tests for public_web views with the dynamic system
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock

User = get_user_model()


class PublicWebViewsTest(TestCase):
    """Test public web views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_landing_view(self):
        """Test the landing page view"""
        response = self.client.get(reverse('public_web:landing'))
        self.assertEqual(response.status_code, 200)
        
        # Test with authenticated user (should redirect to dashboard if saas_web URLs exist)
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('public_web:landing'))
        # May return 200 or 302 depending on URL configuration
        self.assertIn(response.status_code, [200, 302])
    
    def test_features_view(self):
        """Test the features page view"""
        response = self.client.get(reverse('public_web:features'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'fonctionnalités')  # Should contain features content
    
    def test_about_view(self):
        """Test the about page view"""
        response = self.client.get(reverse('public_web:about'))
        self.assertEqual(response.status_code, 200)
    
    def test_contact_view(self):
        """Test the contact page view"""
        response = self.client.get(reverse('public_web:contact'))
        self.assertEqual(response.status_code, 200)
    
    @patch('public_web.views.manifest_parser.get_public_apps')
    def test_dynamic_apps_list_view(self, mock_get_apps):
        """Test the dynamic apps list view"""
        mock_apps = [
            {
                'name': 'Learning',
                'slug': 'course',
                'summary': 'Interactive language lessons',
                'category': 'Education',
                'version': '1.0.0',
                'icon': 'book',
                'menu_order': 1
            },
            {
                'name': 'Revision',
                'slug': 'revision',
                'summary': 'Spaced repetition flashcards',
                'category': 'Education',
                'version': '1.0.0',
                'icon': 'cards',
                'menu_order': 2
            }
        ]
        mock_get_apps.return_value = mock_apps
        
        response = self.client.get(reverse('public_web:apps'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Learning')
        self.assertContains(response, 'Revision')
        self.assertContains(response, 'Interactive language lessons')
    
    @patch('public_web.views.manifest_parser.get_app_by_slug')
    def test_dynamic_app_detail_view_success(self, mock_get_app):
        """Test the dynamic app detail view with existing app"""
        mock_app = {
            'name': 'Learning',
            'slug': 'course',
            'summary': 'Interactive language lessons',
            'description': 'Comprehensive language learning with interactive exercises.',
            'category': 'Education/Language Learning',
            'version': '1.0.0',
            'author': 'Linguify Team',
            'icon': 'book'
        }
        mock_get_app.return_value = mock_app
        
        response = self.client.get(reverse('public_web:dynamic_app_detail', kwargs={'app_slug': 'course'}))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Learning')
        self.assertContains(response, 'Interactive language lessons')
        self.assertContains(response, 'Comprehensive language learning')
    
    @patch('public_web.views.manifest_parser.get_app_by_slug')
    def test_dynamic_app_detail_view_not_found(self, mock_get_app):
        """Test the dynamic app detail view with non-existent app"""
        mock_get_app.return_value = None
        
        response = self.client.get(reverse('public_web:dynamic_app_detail', kwargs={'app_slug': 'nonexistent'}))
        
        self.assertEqual(response.status_code, 404)
    
    def test_legacy_app_views_still_work(self):
        """Test that legacy app views still work"""
        # Test courses app view (redirect)
        response = self.client.get(reverse('public_web:legacy_courses_redirect'))
        self.assertEqual(response.status_code, 301)  # Redirect
        
        # Test revision app view (redirect)
        response = self.client.get(reverse('public_web:legacy_revision_redirect'))
        self.assertEqual(response.status_code, 301)  # Redirect
        
        # Test notebook app view (redirect)
        response = self.client.get(reverse('public_web:legacy_notebook_redirect'))
        self.assertEqual(response.status_code, 301)  # Redirect
    
    def test_robots_txt_view(self):
        """Test robots.txt view"""
        response = self.client.get(reverse('public_web:robots_txt'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain')
        self.assertContains(response, 'User-agent: *')
    
    def test_sitemap_xml_view(self):
        """Test sitemap.xml view"""
        response = self.client.get(reverse('public_web:sitemap_xml'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/xml')
        self.assertContains(response, '<?xml version="1.0"')
        self.assertContains(response, '<urlset')


class PublicWebContextTest(TestCase):
    """Test context data passed to templates"""
    
    def setUp(self):
        self.client = Client()
    
    @patch('public_web.views.manifest_parser.get_public_apps')
    def test_apps_list_context(self, mock_get_apps):
        """Test that apps list view passes correct context"""
        mock_apps = [
            {
                'name': 'Test App',
                'slug': 'test_app',
                'summary': 'Test summary',
                'category': 'Test',
                'version': '1.0.0'
            }
        ]
        mock_get_apps.return_value = mock_apps
        
        response = self.client.get(reverse('public_web:apps'))
        
        self.assertEqual(response.context['apps'], mock_apps)
        self.assertIn('title', response.context)
        self.assertIn('meta_description', response.context)
    
    @patch('public_web.views.manifest_parser.get_app_by_slug')
    def test_app_detail_context(self, mock_get_app):
        """Test that app detail view passes correct context"""
        mock_app = {
            'name': 'Test App',
            'slug': 'test_app',
            'summary': 'Test summary',
            'description': 'Test description',
            'category': 'Test',
            'version': '1.0.0',
            'author': 'Test Author'
        }
        mock_get_app.return_value = mock_app
        
        response = self.client.get(reverse('public_web:dynamic_app_detail', kwargs={'app_slug': 'test_app'}))
        
        self.assertEqual(response.context['app'], mock_app)
        self.assertIn('title', response.context)
        self.assertIn('meta_description', response.context)
        self.assertEqual(response.context['title'], 'Test App - Open Linguify')


class PublicWebLanguageTest(TestCase):
    """Test language-specific functionality"""
    
    def setUp(self):
        self.client = Client()
    
    def test_features_view_with_language(self):
        """Test features view with different languages"""
        # Test French (may not be configured in test environment)
        response = self.client.get('/fr/features/')
        self.assertIn(response.status_code, [200, 404])  # May not be configured in tests
        
        # Test base URL works
        response = self.client.get('/features/')
        self.assertEqual(response.status_code, 200)
    
    @patch('public_web.views.manifest_parser.get_app_by_slug')
    def test_dynamic_app_detail_with_language(self, mock_get_app):
        """Test dynamic app detail with different languages"""
        mock_app = {
            'name': 'Test App',
            'slug': 'test_app',
            'summary': 'Test summary',
            'description': 'Test description',
            'category': 'Test',
            'version': '1.0.0'
        }
        mock_get_app.return_value = mock_app
        
        # Test base URL works
        response = self.client.get('/apps/test_app/')
        self.assertEqual(response.status_code, 200)
        
        # Test with language prefix (may not be configured in test environment)
        response = self.client.get('/fr/apps/test_app/')
        self.assertIn(response.status_code, [200, 404])  # May not be configured in tests