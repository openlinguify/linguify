#!/usr/bin/env python
"""
All Apps Test Runner
Comprehensive test runner for all Linguify applications
"""

import os
from typing import List, Dict
from .base import BaseTestRunner


class AllAppsTestRunner(BaseTestRunner):
    """Comprehensive test runner for all Linguify applications"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.force_sqlite_for_testing()
    
    def force_sqlite_for_testing(self):
        """Force SQLite for testing to avoid PostgreSQL dependency"""
        os.environ.pop('DB_NAME', None)
        os.environ.pop('DB_USER', None) 
        os.environ.pop('DB_PASSWORD', None)
        os.environ.pop('DB_HOST', None)
        os.environ.pop('DB_PORT', None)
    
    def get_test_modules(self) -> List[str]:
        """Return all application test modules"""
        return [
            # Authentication (high priority - other modules depend on it)
            'apps.authentication.tests',
            
            # Jobs (standalone, well-tested)
            'core.jobs.tests',
            
            # Course (core learning functionality)
            'apps.course.tests',
            
            # Supporting modules
            'apps.revision.tests',
            'apps.notebook.tests',
            'apps.language_ai.tests',
        ]
    
    def get_runner_name(self) -> str:
        return "Tests COMPLETS Linguify - Toutes Applications"
    
    def print_header(self):
        """Print comprehensive header"""
        super().print_header()
        print("🗑️  Suppression de la base de test existante pour éviter les conflits...")
        print("📋 Applications testées:")
        print("  - authentication (utilisateurs, profils, termes)")
        print("  - jobs (recrutement, candidatures, emails)")
        print("  - course (cours, exercices, contenu)")
        print("  - revision (flashcards, répétition espacée)")
        print("  - notebook (notes, organisation)")
        print("  - language_ai (IA conversationnelle)")
        print("=" * 60)
    
    def get_app_stats(self) -> Dict[str, int]:
        """Return expected test counts per application (approximate)"""
        return {
            'authentication': 15,
            'jobs': 69,
            'course': 56,  # After fixes and skips
            'revision': 8,
            'notebook': 6,
            'language_ai': 3,
        }
    
    def print_success_message(self):
        """Print comprehensive success message"""
        print("\n🎉 TOUS LES TESTS LINGUIFY SONT PASSÉS!")
        print("\n🎯 Systèmes validés:")
        print("  ✅ Authentification et gestion utilisateurs")
        print("  ✅ Système de recrutement complet")
        print("  ✅ Plateforme d'apprentissage (Course)")
        print("  ✅ Révision et mémorisation")
        print("  ✅ Prise de notes et organisation")
        print("  ✅ Intelligence artificielle")
        print("\n🚀 Linguify est prêt pour la production!")
    
    def print_failure_message(self, failures: int):
        """Print comprehensive failure message"""
        super().print_failure_message(failures)
        print(f"\n🔍 Pour débugger une application spécifique:")
        print("  python test_runner/run_authentication.py  # Tests auth uniquement")
        print("  python test_runner/run_jobs.py           # Tests jobs uniquement")
        print("  python test_runner/run_course.py         # Tests course uniquement")
        
        expected_total = sum(self.get_app_stats().values())
        print(f"\n📊 Tests attendus: ~{expected_total} total")
    
    def run_tests(self) -> int:
        """Override to clean test database first"""
        # Clean any existing test database
        self.clean_test_database()
        return super().run_tests()
    
    def clean_test_database(self):
        """Clean existing test database to avoid conflicts"""
        try:
            import sqlite3
            db_path = 'test_db_linguify_dev'
            if os.path.exists(db_path):
                os.remove(db_path)
                print(f"🗑️  Base de test supprimée: {db_path}")
        except Exception as e:
            print(f"⚠️  Impossible de supprimer la base de test: {e}")


class QuickTestRunner(AllAppsTestRunner):
    """Quick test runner for rapid feedback (core tests only)"""
    
    def get_test_modules(self) -> List[str]:
        """Return only core/fast test modules"""
        return [
            'apps.course.tests.test_01_basics',
            'apps.course.tests.test_02_models_basic',
            'apps.jobs.tests.test_models',
            'apps.authentication.tests.test_models_pytest',
        ]
    
    def get_runner_name(self) -> str:
        return "Tests RAPIDES Linguify - Core Modules"
    
    def print_header(self):
        """Print quick test header"""
        super().print_header()
        print("⚡ Mode rapide - Tests essentiels uniquement")
        print("🎯 Pour tests complets: python test_runner/run_all.py")
        print("=" * 60)