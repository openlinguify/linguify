#!/usr/bin/env python3
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

try:
    print("=== Testing Jobs Models ===")
    from core.jobs.models import JobPosition, Department, JobApplication
    print("✓ Jobs models imported successfully")
    
    # Test basic queries
    departments = Department.objects.all()
    print(f"Departments: {list(departments)}")
    
    positions = JobPosition.objects.all()
    print(f"Positions: {[(p.id, p.title, p.is_active) for p in positions]}")
    
    active_positions = JobPosition.objects.filter(is_active=True)
    print(f"Active positions: {[(p.id, p.title) for p in active_positions]}")
    
    # Test position 6 specifically
    position_6 = JobPosition.objects.filter(id=6).first()
    print(f"Position 6: {position_6}")
    if position_6:
        print(f"Position 6 details: ID={position_6.id}, Title={position_6.title}, Active={position_6.is_active}")
    
    print("\n=== Testing Forms ===")
    from core.jobs.forms import JobApplicationForm
    print("✓ Forms imported successfully")
    
    # Test form creation
    if position_6:
        form = JobApplicationForm(position=position_6)
        print(f"✓ Form created for position {position_6.title}")
    else:
        print("✗ Cannot test form - position 6 not found")
        
    print("\n=== Testing Views ===")
    from core.jobs.views_web import JobApplicationView
    print("✓ Views imported successfully")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()