# Tests for Backend System

This directory contains tests for the backend Django application.

**Note**: Tests for the `public_web` dynamic app management system have been moved to the `portal` project where the `public_web` module is located.

## Available Tests

Current tests in this directory:
- `test_settings.py` - Django settings configuration tests  
- `test_seo_imports.py` - SEO module import tests
- `conftest.py` - Pytest configuration

## Running Tests

### Quick Start
```bash
cd backend

# Run all backend tests
poetry run python manage.py test --settings=core.settings_test

# Run specific test files
poetry run python manage.py test tests.test_settings --settings=core.settings_test
poetry run python manage.py test tests.test_seo_imports --settings=core.settings_test
```

