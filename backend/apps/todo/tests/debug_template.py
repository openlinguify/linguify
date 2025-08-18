#!/usr/bin/env python
"""
Debug script to check rendered template content
"""
import os
import django
from django.test import Client
from django.contrib.auth import get_user_model

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

User = get_user_model()

def debug_template():
    """Debug template rendering"""
    print("🔍 Debugging Template Rendering")
    print("=" * 50)
    
    # Create a test client
    client = Client(HTTP_HOST='localhost:8083')
    
    # Get test user
    user = User.objects.get(username='admin')
    client.force_login(user)
    
    # Get the page
    response = client.get('/todo/')
    content = response.content.decode()
    
    # Check for our classes
    classes_to_check = [
        'todo-workspace',
        'todo-sidebar',
        'todo-content',
        'todo-main'
    ]
    
    print("Looking for CSS classes:")
    for cls in classes_to_check:
        count = content.count(cls)
        if count > 0:
            print(f"  ✅ {cls}: Found {count} times")
        else:
            print(f"  ❌ {cls}: Not found")
    
    # Print first 2000 characters to see structure
    print("\n📄 Template content (first 2000 chars):")
    print(content[:2000])
    
    # Check for specific IDs
    ids_to_check = [
        'todoSidebar',
        'tasksList',
        'welcomeState',
        'taskDetails'
    ]
    
    print("\n🆔 Looking for element IDs:")
    for element_id in ids_to_check:
        if f'id="{element_id}"' in content:
            print(f"  ✅ {element_id}: Found")
        else:
            print(f"  ❌ {element_id}: Not found")

if __name__ == '__main__':
    debug_template()