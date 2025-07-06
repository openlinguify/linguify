#!/usr/bin/env python
import os
import sys

# Add portal to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'portal'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')

print("🌐 Debug Portal Import...")
print(f"Python path: {sys.path[:3]}")  # First 3 entries
print(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")

try:
    import portal.settings
    print("✅ Portal settings imported successfully")
except ImportError as e:
    print(f"❌ Failed to import portal.settings: {e}")
    
try:
    import django
    django.setup()
    print("✅ Django setup successful")
except Exception as e:
    print(f"❌ Django setup failed: {e}")