#!/usr/bin/env python3
"""
Test simple et direct du service IA flashcard
"""

import os
import sys

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.append('/mnt/c/Users/louis/WebstormProjects/linguify/backend')

import django
django.setup()

from core.vocal.claude_service import claude_service

def test_claude_direct():
    """Test direct du service Claude"""
    print("🔧 TEST DIRECT SERVICE CLAUDE")
    print("=" * 40)
    
    # Test 1: Service disponible ?
    print(f"Service Claude disponible: {claude_service.is_available()}")
    
    # Test 2: Analyser une commande flashcard
    user_context = {
        'username': 'test',
        'native_language': 'FR',
        'target_language': 'EN',
        'language_level': 'A2'
    }
    
    command = "créer une flashcard avec bonjour et hello"
    print(f"\nCommande à analyser: '{command}'")
    
    result = claude_service.analyze_voice_command(command, user_context)
    
    print(f"Résultat:")
    print(f"  - Succès: {result.get('success')}")
    print(f"  - Action: {result.get('action')}")
    print(f"  - Intention: {result.get('intention')}")
    print(f"  - Claude utilisé: {result.get('claude_used')}")
    print(f"  - IA enhanced: {result.get('ai_enhanced')}")
    print(f"  - Réponse: {result.get('response')}")
    
    if result.get('params'):
        print(f"  - Paramètres:")
        for key, value in result['params'].items():
            print(f"    * {key}: {value}")
    
    # Test 3: Autre commande
    command2 = "ajouter le mot important à mes révisions"
    print(f"\nCommande 2: '{command2}'")
    result2 = claude_service.analyze_voice_command(command2, user_context)
    print(f"  - Succès: {result2.get('success')}")
    print(f"  - Action: {result2.get('action')}")
    print(f"  - IA enhanced: {result2.get('ai_enhanced')}")

if __name__ == "__main__":
    test_claude_direct()