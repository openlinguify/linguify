#!/usr/bin/env python3
"""
Test script to check student admin access
"""
import os
import sys
import django

# Add the current directory to Python path
sys.path.insert(0, '/mnt/c/Users/louis/WebstormProjects/linguify')

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms.settings')

# Setup Django
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth import get_user_model
from lms.apps.tenants.models import Organization, OrganizationMembership

def test_student_admin_access():
    print("=== TEST STUDENT ADMIN ACCESS ===")
    
    # Create a test client
    client = Client()
    
    # Try to get admin user
    User = get_user_model()
    try:
        admin_user = User.objects.get(username='admin')
        print(f"Found admin user: {admin_user.username}")
        print(f"- is_superuser: {admin_user.is_superuser}")
        print(f"- is_staff: {admin_user.is_staff}")
        
        # Login the admin user
        login_success = client.login(username='admin', password='admin123')
        print(f"Login successful: {login_success}")
        
        if login_success:
            # Try to access Stanford student admin
            response = client.get('/org/stanford/students/admin/')
            print(f"Response status: {response.status_code}")
            print(f"Response content type: {response.get('Content-Type', 'unknown')}")
            
            if response.status_code == 200:
                print("✅ SUCCESS: Admin can access student interface!")
                print("Content preview:", str(response.content)[:200])
            else:
                print("❌ FAILED: Admin cannot access student interface")
                print("Response content:", response.content.decode('utf-8')[:500])
        else:
            print("❌ FAILED: Could not login admin user")
            
    except User.DoesNotExist:
        print("❌ FAILED: Admin user not found")
        
        # List all users
        users = User.objects.all()
        print(f"Available users ({users.count()}): {[u.username for u in users]}")

if __name__ == '__main__':
    test_student_admin_access()