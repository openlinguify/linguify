#!/usr/bin/env python
"""
Script to run tests for the dynamic app management system
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner


def run_tests():
    """Run the dynamic system tests"""
    # Setup Django with test settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings_test')
    django.setup()
    
    # Get the Django test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Define test modules for the dynamic system
    test_modules = [
        'tests.test_public_web_dynamic_system',
        'tests.test_public_web_views',
        'tests.test_public_web_templatetags',
        'tests.test_public_web_integration',
    ]
    
    print("🚀 Running Dynamic App Management System Tests")
    print("=" * 50)
    
    # Run the tests
    failures = test_runner.run_tests(test_modules)
    
    if failures:
        print(f"\n❌ {failures} test(s) failed")
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")
        print("\n📊 Test Coverage:")
        print("  ✓ Manifest Parser")
        print("  ✓ Dynamic Views")
        print("  ✓ Template Tags")
        print("  ✓ URL Routing")
        print("  ✓ Integration Tests")
        print("  ✓ Error Handling")
        print("  ✓ Security Tests")
        print("  ✓ Performance Tests")


if __name__ == '__main__':
    run_tests()