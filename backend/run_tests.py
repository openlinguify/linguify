#!/usr/bin/env python
"""
Main test runner entry point
Delegates to the appropriate test runner based on arguments
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    # Default to running all tests
    if len(sys.argv) == 1 or sys.argv[1] == 'all':
        from test_runner.run_all_tests import main
        main()
    elif sys.argv[1] == 'ci':
        from test_runner.run_ci_tests import main
        sys.exit(main())
    elif sys.argv[1] == 'dynamic':
        from test_runner.run_dynamic_system_tests import run_tests
        run_tests()
    elif sys.argv[1] == 'quick':
        from test_runner.all_apps import QuickTestRunner
        runner = QuickTestRunner(verbosity=2, interactive=False)
        failures = runner.run_tests()
        sys.exit(1 if failures else 0)
    else:
        print("Usage: python run_tests.py [all|ci|dynamic|quick]")
        print("  all     - Run all tests (default)")
        print("  ci      - Run CI/CD tests only")
        print("  dynamic - Run dynamic system tests only")
        print("  quick   - Run quick core tests only")
        sys.exit(1)