# Tests for Dynamic App Management System

This directory contains comprehensive tests for the dynamic app management system implemented in `public_web`.

## Test Structure

### 1. `test_public_web_dynamic_system.py`
**Core functionality tests**
- `AppManifestParserTest`: Tests for manifest parsing, caching, and app discovery
- `DynamicViewsTest`: Tests for dynamic view classes
- `TemplateTagsTest`: Unit tests for custom template tags
- `IntegrationTest`: Basic integration testing
- `GlobalManifestParserTest`: Tests for the global parser instance

### 2. `test_public_web_views.py`
**View layer tests**
- `PublicWebViewsTest`: Tests for all public web views (landing, features, apps, etc.)
- `PublicWebContextTest`: Tests for context data passed to templates
- `PublicWebLanguageTest`: Tests for multi-language functionality

### 3. `test_public_web_templatetags.py`
**Template tag tests**
- `AppTagsTest`: Unit tests for custom template tags
- `TemplateRenderingTest`: Tests for template rendering with tags
- `TemplateTagErrorHandlingTest`: Error handling in template tags
- `TemplateTagRegistrationTest`: Tests for proper tag registration
- `TemplateTagIntegrationTest`: Integration tests with realistic data

### 4. `test_public_web_integration.py`
**Full system integration tests**
- `URLRoutingIntegrationTest`: URL pattern and routing tests
- `FullSystemIntegrationTest`: End-to-end system tests
- `TemplateIntegrationTest`: Template system integration
- `ErrorHandlingIntegrationTest`: Error handling across the system
- `PerformanceIntegrationTest`: Performance and caching tests
- `SecurityIntegrationTest`: Security validation tests
- `RealWorldIntegrationTest`: Tests with realistic manifest data

## Running Tests

### Quick Start
```bash
cd backend

# Run all dynamic system tests (recommended)
make test-dynamic

# Or use PowerShell on Windows
./test_dynamic_system.ps1

# Or use bash script
./test_dynamic_system.sh
```

### Run All Dynamic System Tests
```bash
cd backend
export DJANGO_SETTINGS_MODULE=core.settings_test
python run_dynamic_system_tests.py
```

### Run Specific Test Files
```bash
cd backend
export DJANGO_SETTINGS_MODULE=core.settings_test
python manage.py test tests.test_public_web_dynamic_system --verbosity=2
python manage.py test tests.test_public_web_views --verbosity=2
python manage.py test tests.test_public_web_templatetags --verbosity=2
python manage.py test tests.test_public_web_integration --verbosity=2
```

### Run Specific Test Classes
```bash
cd backend
export DJANGO_SETTINGS_MODULE=core.settings_test
python manage.py test tests.test_public_web_dynamic_system.AppManifestParserTest --verbosity=2
python manage.py test tests.test_public_web_views.PublicWebViewsTest --verbosity=2
```

### Windows PowerShell
```powershell
cd backend
$env:DJANGO_SETTINGS_MODULE = "core.settings_test"
python manage.py test tests.test_public_web_dynamic_system --verbosity=2
```

### With Make (Unix/Linux/Mac)
```bash
cd backend
make test-dynamic          # Run dynamic system tests
make test-fast             # Run all tests with SQLite (faster)
make test-coverage         # Run tests with coverage report
make validate-manifests    # Validate app manifests
```

### Run with Pytest (if available)
```bash
cd backend
export DJANGO_SETTINGS_MODULE=core.settings_test
pytest tests/test_public_web_*.py -v
```

### Troubleshooting

**Database Issues (PostgreSQL)**
If you encounter database issues, use the test settings:
```bash
export DJANGO_SETTINGS_MODULE=core.settings_test
```

**Missing Dependencies**
```bash
poetry install
poetry add --group dev pytest-django pytest-mock
```

**Clear Test Database**
```bash
# If PostgreSQL test DB is locked
dropdb test_postgres
# Or use SQLite for tests (faster)
export DJANGO_SETTINGS_MODULE=core.settings_test
```

## Test Coverage

The tests cover:

✅ **Manifest Parser**
- Loading and parsing manifest files
- App discovery and filtering
- Caching mechanism
- Error handling for invalid manifests

✅ **Dynamic Views**
- Apps list view functionality
- App detail view with fallback system
- 404 handling for non-existent apps
- Context data validation

✅ **Template Tags**
- Dynamic dropdown generation
- URL generation for apps
- Translation filtering
- Error handling in templates

✅ **URL Routing**
- Dynamic URL pattern resolution
- Multi-language URL support
- Legacy URL compatibility

✅ **Integration**
- End-to-end workflow testing
- Template rendering with real data
- Cross-component interaction

✅ **Security**
- Input validation and sanitization
- XSS prevention in templates
- Safe slug handling

✅ **Performance**
- Caching behavior validation
- Efficient data loading

## Mock Data

Tests use realistic mock data that mirrors the actual manifest structure:

```python
{
    'name': 'Learning',
    'slug': 'course',
    'category': 'Education/Language Learning',
    'summary': 'Interactive language lessons and exercises',
    'description': 'Comprehensive language learning platform.',
    'icon': 'GraduationCap',
    'menu_order': 1,
    'version': '1.0.0',
    'author': 'Linguify Team'
}
```

## Test Philosophy

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test component interaction
3. **End-to-End Tests**: Test complete user workflows
4. **Error Handling**: Validate graceful failure modes
5. **Security**: Ensure safe handling of user input
6. **Performance**: Validate caching and efficiency

## Adding New Tests

When adding new functionality to the dynamic system:

1. Add unit tests to the appropriate test file
2. Add integration tests if components interact
3. Update mock data if new manifest fields are added
4. Test both success and failure scenarios
5. Validate security implications

## Common Test Patterns

### Testing with Mock Apps
```python
@patch('public_web.views.manifest_parser.get_public_apps')
def test_something(self, mock_get_apps):
    mock_get_apps.return_value = self.mock_apps
    # Test code here
```

### Testing Template Rendering
```python
template_content = "{% load app_tags %}{% dynamic_apps_dropdown %}"
template = Template(template_content)
rendered = template.render(Context({}))
self.assertIn('expected_content', rendered)
```

### Testing URL Resolution
```python
url = reverse('public_web:dynamic_app_detail', kwargs={'app_slug': 'test'})
resolver = resolve('/apps/test/')
self.assertEqual(resolver.view_name, 'public_web:dynamic_app_detail')
```