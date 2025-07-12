#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Test simple du simulateur
from apps.language_ai.ai_service import ai_provider

print(f"AI Provider type: {type(ai_provider).__name__}")
print(f"AI Provider available: {ai_provider.is_available()}")

# Test avec des messages en espagnol
test_messages = [
    {
        "role": "system",
        "content": "You are a friendly Spanish tutor. Always respond in Spanish."
    },
    {
        "role": "user",
        "content": "hola que tal"
    }
]

response = ai_provider.generate_response(test_messages, "spanish", max_tokens=100)
print(f"\nUser: hola que tal")
print(f"AI: {response}")

# Test avec "muy bien"
test_messages2 = [
    {
        "role": "system",
        "content": "You are a friendly Spanish tutor. Always respond in Spanish."
    },
    {
        "role": "user",
        "content": "muy bien"
    }
]

response2 = ai_provider.generate_response(test_messages2, "spanish", max_tokens=100)
print(f"\nUser: muy bien")
print(f"AI: {response2}")