#!/usr/bin/env python
"""
Test script for Todo app functionality
"""
import os
import django
from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

User = get_user_model()

def test_todo_functionality():
    """Test todo app functionality end-to-end"""
    print("🧪 Testing Todo App Functionality")
    print("=" * 50)
    
    # Create a test client with proper host
    client = Client(HTTP_HOST='localhost:8082')
    
    # Get test user
    try:
        user = User.objects.get(username='admin')
        print(f"✅ Test user found: {user.username}")
    except User.DoesNotExist:
        print("❌ No test user found")
        return False
    
    # Login the user
    client.force_login(user)
    print("✅ User logged in")
    
    # Test 1: Main todo page
    print("\n🔍 Test 1: Main todo page")
    response = client.get('/todo/')
    if response.status_code == 200:
        print("✅ Todo main page loads successfully")
        # Check for key elements
        content = response.content.decode()
        if 'todo-container' in content:
            print("✅ Todo container found")
        if 'todo-sidebar' in content:
            print("✅ Todo sidebar found")
        if 'todo-study' in content:
            print("✅ Todo study area found")
    else:
        print(f"❌ Todo page failed: {response.status_code}")
        return False
    
    # Test 2: API Tasks endpoint
    print("\n🔍 Test 2: API Tasks endpoint")
    response = client.get('/api/v1/todo/tasks/')
    if response.status_code == 200:
        data = response.json()
        tasks_count = len(data) if isinstance(data, list) else len(data.get('results', []))
        print(f"✅ Tasks API works: {tasks_count} tasks found")
    else:
        print(f"❌ Tasks API failed: {response.status_code}")
        return False
    
    # Test 3: API Stages endpoint
    print("\n🔍 Test 3: API Stages endpoint")
    response = client.get('/api/v1/todo/stages/')
    if response.status_code == 200:
        data = response.json()
        stages_count = len(data) if isinstance(data, list) else len(data.get('results', []))
        print(f"✅ Stages API works: {stages_count} stages found")
    else:
        print(f"❌ Stages API failed: {response.status_code}")
        return False
    
    # Test 4: API Tags endpoint
    print("\n🔍 Test 4: API Tags endpoint")
    response = client.get('/api/v1/todo/tags/')
    if response.status_code == 200:
        data = response.json()
        tags_count = len(data) if isinstance(data, list) else len(data.get('results', []))
        print(f"✅ Tags API works: {tags_count} tags found")
    else:
        print(f"❌ Tags API failed: {response.status_code}")
        return False
    
    # Test 5: Task creation via API
    print("\n🔍 Test 5: Task creation via API")
    response = client.post('/api/v1/todo/tasks/quick_create/', {
        'title': 'Test Task from API'
    }, content_type='application/json')
    if response.status_code == 201:
        task_data = response.json()
        print(f"✅ Task created successfully: {task_data.get('title', 'Unknown')}")
    else:
        print(f"❌ Task creation failed: {response.status_code}")
        return False
    
    # Test 6: Dashboard API
    print("\n🔍 Test 6: Dashboard API")
    response = client.get('/api/v1/todo/dashboard/')
    if response.status_code == 200:
        dashboard_data = response.json()
        stats = dashboard_data.get('stats', {})
        print(f"✅ Dashboard API works")
        print(f"   Total tasks: {stats.get('total_tasks', 0)}")
        print(f"   Completed tasks: {stats.get('completed_tasks', 0)}")
        print(f"   Today's tasks: {stats.get('today_tasks', 0)}")
    else:
        print(f"❌ Dashboard API failed: {response.status_code}")
        return False
    
    # Test 7: Settings API
    print("\n🔍 Test 7: Settings API")
    response = client.get('/api/v1/todo/settings/')
    if response.status_code == 200:
        settings_data = response.json()
        print(f"✅ Settings API works")
        print(f"   Default view: {settings_data.get('default_project_view', 'unknown')}")
    else:
        print(f"❌ Settings API failed: {response.status_code}")
        return False
    
    print("\n🎉 All tests passed! Todo app is fully functional!")
    return True

if __name__ == '__main__':
    test_todo_functionality()