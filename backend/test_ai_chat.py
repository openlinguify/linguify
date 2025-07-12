#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Test de l'IA
from apps.language_ai.ai_service import ai_provider
from apps.language_ai.ai_providers import HuggingFaceProvider

print(f"AI Provider configured: {os.environ.get('AI_PROVIDER', 'Not set')}")
print(f"HuggingFace token: {'Set' if os.environ.get('HUGGINGFACE_API_TOKEN') else 'Not set'}")

# Test direct du provider HuggingFace
hf_provider = HuggingFaceProvider()
print(f"\nHuggingFace provider available: {hf_provider.is_available()}")
print(f"HuggingFace token in provider: {'Set' if hf_provider.hf_token else 'Not set'}")

# Test simple
if hf_provider.is_available():
    print("\nTesting HuggingFace API...")
    test_messages = [
        {
            "role": "system",
            "content": "You are a friendly Spanish tutor. Always respond in Spanish."
        },
        {
            "role": "user",
            "content": "Hello, how are you?"
        }
    ]
    
    try:
        # Test avec un modèle conversationnel simple
        import requests
        
        # Essayons d'abord de voir ce qui est disponible
        headers = {"Authorization": f"Bearer {hf_provider.hf_token}"}
        
        # Essayons avec le modèle conversationnel de HuggingFace
        print("\nTrying conversational API...")
        
        api_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
        
        # Format pour l'API conversationnelle
        payload = {
            "inputs": {
                "past_user_inputs": [],
                "generated_responses": [],
                "text": "Hello, I want to learn Spanish. Can you help me?"
            },
            "parameters": {
                "max_length": 100,
                "temperature": 0.7
            }
        }
        
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        print(f"Conversational API Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        # Essayons aussi avec une API de text generation simple
        print("\n\nTrying text generation API...")
        api_url = "https://api-inference.huggingface.co/models/gpt2"
        
        payload = {
            "inputs": "The Spanish word for hello is",
        }
        
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        print(f"Text Gen Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("\nHuggingFace provider not available!")

# Test avec ai_provider global
print(f"\nGlobal AI provider type: {type(ai_provider).__name__}")
print(f"Global AI provider available: {ai_provider.is_available()}")