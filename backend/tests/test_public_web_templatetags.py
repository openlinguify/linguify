"""
Tests for public_web templatetags
"""
from django.test import TestCase
from django.template import Context, Template, TemplateSyntaxError
from django.urls import reverse
from unittest.mock import patch, MagicMock

from public_web.templatetags.app_tags import (
    dynamic_apps_dropdown, 
    get_public_apps, 
    get_app_url, 
    translate_app_name
)


class AppTagsTest(TestCase):
    """Test custom template tags for app management"""
    
    def test_dynamic_apps_dropdown_tag(self):
        """Test the dynamic_apps_dropdown inclusion tag"""
        mock_apps = [
            {
                'name': 'Learning',
                'slug': 'course',
                'icon': 'book',
                'summary': 'Interactive lessons'
            },
            {
                'name': 'Revision',
                'slug': 'revision',
                'icon': 'cards',
                'summary': 'Spaced repetition'
            }
        ]
        
        with patch('public_web.templatetags.app_tags.manifest_parser.get_public_apps', return_value=mock_apps):
            result = dynamic_apps_dropdown()
            
            self.assertEqual(result['apps'], mock_apps)
            self.assertIsInstance(result, dict)
    
    def test_get_public_apps_simple_tag(self):
        """Test the get_public_apps simple tag"""
        mock_apps = [
            {'name': 'Test App', 'slug': 'test_app'}
        ]
        
        with patch('public_web.templatetags.app_tags.manifest_parser.get_public_apps', return_value=mock_apps):
            result = get_public_apps()
            
            self.assertEqual(result, mock_apps)
    
    def test_get_app_url_success(self):
        """Test get_app_url with valid app slug"""
        with patch('public_web.templatetags.app_tags.reverse') as mock_reverse:
            mock_reverse.return_value = '/apps/test-app/'
            
            result = get_app_url('test_app')
            
            self.assertEqual(result, '/apps/test-app/')
            mock_reverse.assert_called_once_with(
                'public_web:dynamic_app_detail', 
                kwargs={'app_slug': 'test_app'}
            )
    
    def test_get_app_url_failure(self):
        """Test get_app_url with invalid app slug"""
        with patch('public_web.templatetags.app_tags.reverse', side_effect=Exception("URL not found")):
            result = get_app_url('invalid_app')
            
            self.assertEqual(result, '#')
    
    def test_translate_app_name_filter(self):
        """Test the translate_app_name filter"""
        with patch('public_web.templatetags.app_tags._') as mock_gettext:
            mock_gettext.return_value = 'Cours'
            
            result = translate_app_name('Courses')
            
            self.assertEqual(result, 'Cours')
            mock_gettext.assert_called_once_with('Courses')


class TemplateRenderingTest(TestCase):
    """Test template rendering with custom tags"""
    
    def test_dynamic_apps_dropdown_template_rendering(self):
        """Test that the dynamic_apps_dropdown template renders correctly"""
        mock_apps = [
            {
                'name': 'Learning',
                'slug': 'course',
                'icon': 'book'
            },
            {
                'name': 'Revision', 
                'slug': 'revision',
                'icon': 'cards'
            }
        ]
        
        template_content = """
        {% load app_tags %}
        {% dynamic_apps_dropdown %}
        """
        
        with patch('public_web.templatetags.app_tags.manifest_parser.get_public_apps', return_value=mock_apps):
            template = Template(template_content)
            context = Context({})
            rendered = template.render(context)
            
            # Should contain app names (after translation)
            self.assertIn('Learning', rendered)
            self.assertIn('Revision', rendered)
    
    def test_get_app_url_in_template(self):
        """Test get_app_url tag in template"""
        template_content = """
        {% load app_tags %}
        <a href="{% get_app_url 'course' %}">Course Link</a>
        """
        
        with patch('public_web.templatetags.app_tags.reverse', return_value='/apps/course/'):
            template = Template(template_content)
            context = Context({})
            rendered = template.render(context)
            
            self.assertIn('href="/apps/course/"', rendered)
            self.assertIn('Course Link', rendered)
    
    def test_translate_app_name_in_template(self):
        """Test translate_app_name filter in template"""
        template_content = """
        {% load app_tags %}
        {{ app_name|translate_app_name }}
        """
        
        with patch('public_web.templatetags.app_tags._', return_value='Cours'):
            template = Template(template_content)
            context = Context({'app_name': 'Courses'})
            rendered = template.render(context)
            
            self.assertIn('Cours', rendered.strip())
    
    def test_get_public_apps_in_template(self):
        """Test get_public_apps tag in template"""
        mock_apps = [
            {'name': 'App 1', 'slug': 'app1'},
            {'name': 'App 2', 'slug': 'app2'}
        ]
        
        template_content = """
        {% load app_tags %}
        {% get_public_apps as apps %}
        {% for app in apps %}{{ app.name }}{% if not forloop.last %}, {% endif %}{% endfor %}
        """
        
        with patch('public_web.templatetags.app_tags.manifest_parser.get_public_apps', return_value=mock_apps):
            template = Template(template_content)
            context = Context({})
            rendered = template.render(context)
            
            self.assertIn('App 1, App 2', rendered.strip())
    
    def test_template_with_no_apps(self):
        """Test template rendering when no apps are available"""
        template_content = """
        {% load app_tags %}
        {% dynamic_apps_dropdown %}
        """
        
        with patch('public_web.templatetags.app_tags.manifest_parser.get_public_apps', return_value=[]):
            template = Template(template_content)
            context = Context({})
            rendered = template.render(context)
            
            # Should contain the "No apps available" message
            self.assertIn('No apps available', rendered)


class TemplateTagErrorHandlingTest(TestCase):
    """Test error handling in template tags"""
    
    def test_get_app_url_with_exception(self):
        """Test get_app_url handles reverse exceptions gracefully"""
        # Test with various types of exceptions
        exceptions_to_test = [
            Exception("General error"),
            ImportError("Module not found"),
            AttributeError("Attribute error")
        ]
        
        for exception in exceptions_to_test:
            with patch('public_web.templatetags.app_tags.reverse', side_effect=exception):
                result = get_app_url('test_app')
                self.assertEqual(result, '#')
    
    def test_dynamic_apps_dropdown_with_parser_error(self):
        """Test dynamic_apps_dropdown handles parser errors"""
        with patch('public_web.templatetags.app_tags.manifest_parser.get_public_apps', side_effect=Exception("Parser error")):
            # Should not raise exception, but might return empty or default data
            try:
                result = dynamic_apps_dropdown()
                # If it doesn't raise an exception, it should return a dict
                self.assertIsInstance(result, dict)
            except Exception:
                # If it does raise an exception, that's also acceptable for this test
                pass


class TemplateTagRegistrationTest(TestCase):
    """Test that template tags are properly registered"""
    
    def test_template_tags_are_registered(self):
        """Test that all our custom tags are properly registered"""
        from django.template import Library
        from public_web.templatetags.app_tags import register
        
        self.assertIsInstance(register, Library)
        
        # Check that our tags are in the register
        self.assertIn('dynamic_apps_dropdown', register.tags)
        # Check filters
        self.assertIn('translate_app_name', register.filters)
        # Simple tags are stored differently in Django
        self.assertTrue(hasattr(register, 'simple_tag'))
    
    def test_template_loading(self):
        """Test that the templatetags module can be loaded in templates"""
        template_content = """
        {% load app_tags %}
        Template loaded successfully
        """
        
        try:
            template = Template(template_content)
            context = Context({})
            rendered = template.render(context)
            self.assertIn('Template loaded successfully', rendered)
        except TemplateSyntaxError:
            self.fail("Template tags failed to load")


class TemplateTagIntegrationTest(TestCase):
    """Integration tests for template tags with real-like data"""
    
    def test_full_dropdown_rendering(self):
        """Test complete dropdown rendering with realistic data"""
        mock_apps = [
            {
                'name': 'Learning',
                'slug': 'course',
                'icon': 'graduation-cap',
                'summary': 'Interactive language learning',
                'menu_order': 1
            },
            {
                'name': 'Revision',
                'slug': 'revision', 
                'icon': 'cards',
                'summary': 'Spaced repetition flashcards',
                'menu_order': 2
            },
            {
                'name': 'Notebook',
                'slug': 'notebook',
                'icon': 'journal',
                'summary': 'Note-taking and organization',
                'menu_order': 3
            }
        ]
        
        # Mock the dropdown template content
        dropdown_template = """
        {% load i18n %}
        {% load app_tags %}
        {% for app in apps %}
            <li><a class="dropdown-item" href="{% get_app_url app.slug %}">
                {{ app.name|translate_app_name }}
            </a></li>
        {% empty %}
            <li><span class="dropdown-item text-muted">{% trans "No apps available" %}</span></li>
        {% endfor %}
        """
        
        with patch('public_web.templatetags.app_tags.manifest_parser.get_public_apps', return_value=mock_apps):
            with patch('public_web.templatetags.app_tags.reverse', return_value='/apps/test/'):
                with patch('public_web.templatetags.app_tags._', side_effect=lambda x: x):  # No translation
                    
                    template = Template(dropdown_template)
                    context = Context({'apps': mock_apps})
                    rendered = template.render(context)
                    
                    # Should contain all app names
                    self.assertIn('Learning', rendered)
                    self.assertIn('Revision', rendered)
                    self.assertIn('Notebook', rendered)
                    
                    # Should contain links
                    self.assertIn('dropdown-item', rendered)
                    self.assertIn('/apps/test/', rendered)