#!/usr/bin/env python3
"""
Simple test runner for Linguify backend using Django's manage.py
Usage: python run_tests.py [course|jobs|all]
"""

import sys
import subprocess
import os

def main():
    # Change to backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    
    # Set TEST_MODE environment variable for testing
    os.environ['TEST_MODE'] = 'True'
    
    if len(sys.argv) < 2:
        print("Usage: python run_tests.py [course|jobs|safe|quick]")
        print("  course - Run Course module tests")
        print("  jobs   - Run Jobs module tests") 
        print("  safe   - Run main working tests (course + jobs)")
        print("  quick  - Run basic course tests only")
        sys.exit(1)
    
    test_type = sys.argv[1].lower()
    
    # Check if Poetry is available and use it if possible
    def check_poetry():
        try:
            subprocess.run(["poetry", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    use_poetry = check_poetry()
    
    if use_poetry:
        print("Using Poetry environment...")
        base_cmd = ["poetry", "run", "python", "manage.py", "test"]
    else:
        # Use python3 if available, otherwise python
        python_cmd = "python3" if os.name != 'nt' else "python"
        base_cmd = [python_cmd, "manage.py", "test"]
    
    # Add keepdb flag to speed up tests by reusing test database
    base_cmd.append("--keepdb")
    
    # Map test types to Django test paths
    test_commands = {
        "course": base_cmd + ["apps.course.tests", "--verbosity=2"],
        "jobs": base_cmd + ["apps.jobs.tests", "--verbosity=2"],
        "safe": base_cmd + ["apps.course.tests", "apps.jobs.tests", "--verbosity=2"],
        "quick": base_cmd + ["apps.course.tests.test_01_basics", "--verbosity=2"]
    }
    
    if test_type not in test_commands:
        print(f"Unknown test type: {test_type}")
        print("Available options: course, jobs, safe, quick")
        sys.exit(1)
    
    # Run the tests
    try:
        print(f"🚀 Running {test_type} tests...")
        print("=" * 50)
        result = subprocess.run(test_commands[test_type], check=False)
        
        if result.returncode == 0:
            print("\n" + "=" * 50)
            print("✅ ALL TESTS PASSED!")
        else:
            print("\n" + "=" * 50)
            print(f"⚠️  Tests completed with errors (exit code: {result.returncode})")
        
        sys.exit(result.returncode)
        
    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()