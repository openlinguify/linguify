#!/usr/bin/env python
"""
Simplified test runner for Supabase profile picture tests
Run this after fixing the database migration issue
"""
import os
import sys
import django
from django.test.utils import get_runner
from django.conf import settings

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

def run_supabase_tests():
    """Run only the Supabase profile picture tests"""
    try:
        django.setup()
        
        # Get the test runner
        TestRunner = get_runner(settings)
        test_runner = TestRunner()
        
        # Run specific test classes
        test_labels = [
            'apps.authentication.tests.test_profile_pictures.SupabaseProfilePictureTestCase.test_supabase_upload_success',
            'apps.authentication.tests.test_profile_pictures.SupabaseProfilePictureTestCase.test_supabase_upload_failure',
            'apps.authentication.tests.test_profile_pictures.SupabaseProfilePictureTestCase.test_ajax_response_includes_updated_url',
        ]
        
        print("Running Supabase profile picture tests...")
        failures = test_runner.run_tests(test_labels)
        
        if failures:
            print(f"❌ {failures} test(s) failed")
            return False
        else:
            print("✅ All Supabase profile picture tests passed!")
            return True
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

if __name__ == '__main__':
    success = run_supabase_tests()
    sys.exit(0 if success else 1)