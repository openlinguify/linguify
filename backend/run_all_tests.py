#!/usr/bin/env python
"""
Main test runner script for Linguify backend
Runs all application tests with proper setup
"""

import os
import sys
import django

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the comprehensive test runner
from test_runner.all_apps import AllAppsTestRunner


def main():
    """Main entry point for running all tests"""
    # Setup Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings_test')
    django.setup()
    
    # Create and run the test runner
    runner = AllAppsTestRunner(verbosity=2, interactive=False)
    failures = runner.run_tests()
    
    # Exit with appropriate code
    sys.exit(1 if failures else 0)


if __name__ == '__main__':
    main()