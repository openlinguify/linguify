#!/usr/bin/env python
"""
Test Runner Utilities
Common utilities and validation functions for test runners
"""

import os
import sys
from typing import List, Dict, Tuple
import importlib.util


def validate_test_modules(modules: List[str]) -> Tuple[List[str], List[str]]:
    """
    Validate that test modules exist and can be imported
    
    Returns:
        Tuple of (valid_modules, invalid_modules)
    """
    valid_modules = []
    invalid_modules = []
    
    for module in modules:
        try:
            # Convert Django test path to file path
            parts = module.split('.')
            if 'tests' in parts:
                # Handle both 'apps.module.tests' and 'apps.module.tests.test_file'
                if parts[-1] == 'tests':
                    # Directory-based tests
                    test_dir = os.path.join(*parts)
                    if os.path.exists(test_dir) and os.path.isdir(test_dir):
                        valid_modules.append(module)
                    else:
                        invalid_modules.append(module)
                else:
                    # File-based tests
                    test_file = os.path.join(*parts[:-1]) + f"/{parts[-1]}.py"
                    if os.path.exists(test_file):
                        valid_modules.append(module)
                    else:
                        invalid_modules.append(module)
            else:
                valid_modules.append(module)  # Assume valid if not tests
        except Exception:
            invalid_modules.append(module)
    
    return valid_modules, invalid_modules


def count_tests_in_modules(modules: List[str]) -> Dict[str, int]:
    """
    Count approximate number of tests in each module
    
    Returns:
        Dictionary mapping module names to test counts
    """
    test_counts = {}
    
    for module in modules:
        try:
            # Convert module path to file system path
            parts = module.split('.')
            if parts[-1] == 'tests':
                # Directory with multiple test files
                test_dir = os.path.join(*parts)
                count = count_tests_in_directory(test_dir)
            else:
                # Single test file
                test_file = os.path.join(*parts[:-1]) + f"/{parts[-1]}.py"
                count = count_tests_in_file(test_file)
            
            test_counts[module] = count
        except Exception:
            test_counts[module] = 0
    
    return test_counts


def count_tests_in_file(file_path: str) -> int:
    """Count test methods in a single Python file"""
    if not os.path.exists(file_path):
        return 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Count methods starting with 'test_'
            return content.count('def test_')
    except Exception:
        return 0


def count_tests_in_directory(dir_path: str) -> int:
    """Count test methods in all Python files in a directory"""
    if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
        return 0
    
    total_count = 0
    try:
        for filename in os.listdir(dir_path):
            if filename.startswith('test_') and filename.endswith('.py'):
                file_path = os.path.join(dir_path, filename)
                total_count += count_tests_in_file(file_path)
    except Exception:
        pass
    
    return total_count


def get_test_summary(modules: List[str]) -> Dict[str, any]:
    """
    Get comprehensive summary of test modules
    
    Returns:
        Dictionary with validation results and statistics
    """
    valid_modules, invalid_modules = validate_test_modules(modules)
    test_counts = count_tests_in_modules(valid_modules)
    
    return {
        'total_modules': len(modules),
        'valid_modules': len(valid_modules),
        'invalid_modules': len(invalid_modules),
        'valid_module_list': valid_modules,
        'invalid_module_list': invalid_modules,
        'test_counts': test_counts,
        'estimated_total_tests': sum(test_counts.values())
    }


def print_test_summary(modules: List[str]):
    """Print formatted test summary"""
    summary = get_test_summary(modules)
    
    print("📊 Résumé des tests:")
    print(f"  📁 Modules: {summary['valid_modules']}/{summary['total_modules']} valides")
    print(f"  🧪 Tests estimés: ~{summary['estimated_total_tests']}")
    
    if summary['invalid_modules']:
        print(f"  ⚠️  Modules invalides: {summary['invalid_modules']}")
        for module in summary['invalid_module_list']:
            print(f"    - {module}")
    
    print(f"  📋 Détail par module:")
    for module, count in summary['test_counts'].items():
        module_short = module.split('.')[-1] if '.' in module else module
        print(f"    - {module_short}: ~{count} tests")


class TestEnvironmentValidator:
    """Validate test environment and dependencies"""
    
    @staticmethod
    def validate_django_setup() -> bool:
        """Validate Django is properly configured"""
        try:
            import django
            from django.conf import settings
            django.setup()
            return True
        except Exception as e:
            print(f"❌ Django setup failed: {e}")
            return False
    
    @staticmethod
    def validate_database_config() -> bool:
        """Validate database configuration for testing"""
        try:
            from django.db import connection
            connection.ensure_connection()
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    @staticmethod
    def validate_dependencies() -> Dict[str, bool]:
        """Validate required dependencies are available"""
        dependencies = {
            'django': False,
            'psycopg2': False,
            'redis': False,
        }
        
        for dep in dependencies:
            try:
                importlib.util.find_spec(dep)
                dependencies[dep] = True
            except ImportError:
                dependencies[dep] = False
        
        return dependencies
    
    @classmethod
    def full_validation(cls) -> bool:
        """Run full environment validation"""
        print("🔍 Validation de l'environnement de test...")
        
        django_ok = cls.validate_django_setup()
        db_ok = cls.validate_database_config()
        deps = cls.validate_dependencies()
        
        all_ok = django_ok and db_ok and all(deps.values())
        
        if all_ok:
            print("✅ Environnement de test validé")
        else:
            print("⚠️  Problèmes détectés dans l'environnement")
            if not django_ok:
                print("  - Django non configuré")
            if not db_ok:
                print("  - Base de données non accessible")
            for dep, ok in deps.items():
                if not ok:
                    print(f"  - Dépendance manquante: {dep}")
        
        return all_ok