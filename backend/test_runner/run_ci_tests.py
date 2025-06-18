#!/usr/bin/env python
"""
CI/CD Test Runner
Runs a subset of tests suitable for continuous integration
"""
import os
import sys
import django
from django.core.management import call_command

def main():
    """Run CI tests"""
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings_test')
    django.setup()
    
    print("🚀 Running CI Tests")
    print("=" * 60)
    
    # List of specific test modules to run
    test_modules = [
        # Authentication tests (Django auth only, no Auth0)
        'apps.authentication.tests.test_models_pytest',
        # Note: excluding test_middleware as it tests obsolete Auth0 functionality
        
        # Jobs tests - full suite
        'core.jobs.tests',
        
        # Dynamic system tests
        'tests.test_public_web_views',
        'tests.test_public_web_templatetags',
    ]
    
    print("📋 Running tests for:")
    for module in test_modules:
        print(f"  - {module}")
    print("")
    
    # Run tests
    try:
        call_command('test', *test_modules, verbosity=2, keepdb=True)
        print("\n✅ All CI tests passed!")
        return 0
    except SystemExit as e:
        if e.code != 0:
            print(f"\n❌ Tests failed with exit code: {e.code}")
            return e.code
        return 0
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())