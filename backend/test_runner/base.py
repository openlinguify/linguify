#!/usr/bin/env python
"""
Base test runner for Linguify Django applications
Provides common functionality for all test scripts
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple


class BaseTestRunner(ABC):
    """Base class for all Linguify test runners"""
    
    def __init__(self, verbosity: int = 2, interactive: bool = False, keepdb: bool = False):
        self.verbosity = verbosity
        self.interactive = interactive
        self.keepdb = keepdb
        self.setup_django()
    
    def setup_django(self):
        """Setup Django environment for testing"""
        # Add the project root to the Python path
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.append(project_root)
        
        # Set the Django settings module to test settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings_test')
        
        # Set minimum required environment variables for testing
        os.environ.setdefault('SECRET_KEY', 'test-secret-key-for-linguify-tests')
        os.environ.setdefault('DEBUG', 'True')
        
        # Setup Django
        django.setup()
    
    @abstractmethod
    def get_test_modules(self) -> List[str]:
        """Return list of test modules to run"""
        pass
    
    @abstractmethod
    def get_runner_name(self) -> str:
        """Return the name of this test runner"""
        pass
    
    def print_header(self):
        """Print formatted header for test run"""
        print(f"🚀 {self.get_runner_name()}")
        print("=" * 60)
    
    def print_test_modules(self, modules: List[str]):
        """Print list of test modules being executed"""
        print("📋 Tests à exécuter:")
        for module in modules:
            print(f"  - {module}")
        print("\n" + "=" * 60)
        print("▶️  Début des tests...")
        print("=" * 60)
    
    def print_results(self, failures: int, test_count: int = None):
        """Print formatted test results"""
        print("\n" + "=" * 60)
        if failures == 0:
            print("✅ TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS!")
            self.print_success_message()
        else:
            print(f"⚠️  Tests terminés avec {failures} erreur(s)")
            self.print_failure_message(failures)
    
    def print_success_message(self):
        """Print success message specific to this runner"""
        pass
    
    def print_failure_message(self, failures: int):
        """Print failure message specific to this runner"""
        print(f"\n🔍 Vérifiez les erreurs ci-dessus pour plus de détails.")
    
    def run_tests(self) -> int:
        """Run the tests and return failure count"""
        self.print_header()
        
        test_modules = self.get_test_modules()
        self.print_test_modules(test_modules)
        
        # Configure Django test runner
        TestRunner = get_runner(settings)
        test_runner = TestRunner(
            verbosity=self.verbosity, 
            interactive=self.interactive, 
            keepdb=self.keepdb
        )
        
        # Run the tests
        failures = test_runner.run_tests(test_modules)
        
        # Print results
        self.print_results(failures)
        
        return failures


class ModuleTestRunner(BaseTestRunner):
    """Generic test runner for specific Django modules"""
    
    def __init__(self, module_name: str, test_modules: List[str], 
                 description: str = None, **kwargs):
        self.module_name = module_name
        self.test_modules = test_modules
        self.description = description or f"Tests {module_name}"
        super().__init__(**kwargs)
    
    def get_test_modules(self) -> List[str]:
        return self.test_modules
    
    def get_runner_name(self) -> str:
        return self.description


def create_test_runner(module_name: str, test_modules: List[str], 
                      description: str = None) -> ModuleTestRunner:
    """Factory function to create a test runner for a specific module"""
    return ModuleTestRunner(module_name, test_modules, description)