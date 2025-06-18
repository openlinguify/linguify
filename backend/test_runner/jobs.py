#!/usr/bin/env python
"""
Jobs Module Test Runner
Specialized test runner for the Jobs module
"""

from typing import List
from .base import BaseTestRunner


class JobsTestRunner(BaseTestRunner):
    """Specialized test runner for Jobs module"""
    
    def get_test_modules(self) -> List[str]:
        """Return Jobs test modules"""
        return [
            'core.jobs.tests.test_models',
            'core.jobs.tests.test_api', 
            'core.jobs.tests.test_admin',
            'core.jobs.tests.test_email_system',
            'core.jobs.tests.test_utils',
        ]
    
    def get_runner_name(self) -> str:
        return "Tests Jobs Module - Système de Recrutement"
    
    def print_header(self):
        """Print Jobs-specific header"""
        super().print_header()
        print("🎯 Module Jobs:")
        print("  - API endpoints et filtres")
        print("  - Interface d'administration")
        print("  - Système d'emails automatiques")
        print("  - Modèles et validations")
        print("  - Utilitaires et helpers")
        print("=" * 60)
    
    def print_success_message(self):
        """Print Jobs-specific success message"""
        print("\n🎯 Fonctionnalités Jobs testées:")
        print("  ✅ Candidatures et CVs")
        print("  ✅ Gestion des postes")
        print("  ✅ Système d'emails")
        print("  ✅ Interface admin")
        print("  ✅ API et filtres")
        print("  ✅ Validation métier")
    
    def print_failure_message(self, failures: int):
        """Print Jobs-specific failure message"""
        super().print_failure_message(failures)
        print("\n🔧 Vérifiez:")
        print("  - Configuration SMTP pour les emails")
        print("  - Permissions et authentification")
        print("  - Validation des fichiers CV")