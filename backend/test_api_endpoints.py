#!/usr/bin/env python3

import os
import sys
import django
from django.test import RequestFactory
from django.contrib.auth import get_user_model

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.course.api.viewsets import UserProgressViewSet

User = get_user_model()

def test_api_endpoints():
    """Test API endpoints that are called by the learning page"""
    
    print("Testing API endpoints...")
    
    try:
        # Create a test user if none exists
        user = User.objects.first()
        if not user:
            print("! No users found in database")
            return False
            
        print(f"✓ Using test user: {user.username}")
        
        # Test the statistics endpoint
        factory = RequestFactory()
        request = factory.get('/api/v1/course/progress/statistics/')
        request.user = user
        
        viewset = UserProgressViewSet()
        viewset.request = request
        
        # Test the statistics method
        response = viewset.statistics(request)
        print(f"✓ Statistics endpoint works - Status: {response.status_code}")
        
        if hasattr(response, 'data'):
            print(f"✓ Statistics data: {list(response.data.keys())}")
            
    except Exception as e:
        print(f"✗ Error testing statistics endpoint: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    try:
        # Test the dashboard endpoint
        response = viewset.dashboard(request)
        print(f"✓ Dashboard endpoint works - Status: {response.status_code}")
        
        if hasattr(response, 'data'):
            print(f"✓ Dashboard data: {list(response.data.keys())}")
            
    except Exception as e:
        print(f"✗ Error testing dashboard endpoint: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("API endpoints are working correctly!")
    return True

if __name__ == "__main__":
    success = test_api_endpoints()
    sys.exit(0 if success else 1)