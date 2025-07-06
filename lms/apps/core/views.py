from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from lms.apps.tenants.models import Organization

def dashboard(request, org_slug=None):
    """LMS Dashboard - main landing page"""
    if request.user.is_authenticated:
        # Check if we're in an organization context
        if hasattr(request, 'organization') and request.organization:
            # Get user's role in this organization
            from lms.apps.tenants.models import OrganizationMembership
            try:
                membership = OrganizationMembership.objects.get(
                    user=request.user,
                    organization=request.organization
                )
                user_role = membership.role
            except OrganizationMembership.DoesNotExist:
                user_role = 'guest'
            
            # Build context based on role
            context = {
                'organization': request.organization,
                'user_role': user_role,
            }
            
            # Add role-specific data
            if user_role == 'student':
                # Get student profile and enrollments from tenant database
                try:
                    from lms.apps.students.models import StudentProfile
                    db_name = request.organization.database_name
                    student_profile = StudentProfile.objects.using(db_name).get(
                        user=request.user
                    )
                    context['student_profile'] = student_profile
                    context['enrollments'] = student_profile.enrollments.using(db_name).all()[:5]  # Recent 5
                except StudentProfile.DoesNotExist:
                    # Auto-create student profile if it doesn't exist
                    from datetime import date
                    student_profile = StudentProfile.objects.using(db_name).create(
                        user=request.user,
                        student_id=f"{request.organization.slug.upper()}{str(request.user.id).zfill(6)}",
                        organization_id=request.organization.slug,
                        program="Non defini",
                        academic_year="1",
                        enrollment_date=date.today(),
                        status='active',
                        study_mode='full_time',
                        credits_required=120
                    )
                    context['student_profile'] = student_profile
                    context['enrollments'] = []
                    context['profile_just_created'] = True
                except Exception as e:
                    print(f"Error accessing student profile: {e}")
                    context['needs_profile_setup'] = True
            
            elif user_role in ['owner', 'administrator']:
                # Add admin statistics from tenant database
                try:
                    from lms.apps.students.models import StudentProfile
                    db_name = request.organization.database_name
                    context['total_students'] = StudentProfile.objects.using(db_name).filter(
                        organization_id=request.organization.slug
                    ).count()
                    context['active_students'] = StudentProfile.objects.using(db_name).filter(
                        organization_id=request.organization.slug,
                        status='active'
                    ).count()
                except Exception as e:
                    print(f"Error getting admin stats: {e}")
                    context['total_students'] = 0
                    context['active_students'] = 0
            
            return render(request, 'core/dashboard.html', context)
        else:
            # Show organization selection
            return organization_select(request)
    # Pass organization context even for non-authenticated users
    context = {}
    if hasattr(request, 'organization') and request.organization:
        context['organization'] = request.organization
    return render(request, 'core/landing.html', context)

@login_required
def organization_select(request):
    """Let user select which organization to access"""
    context = {
        'user': request.user,
    }
    
    if request.user.is_superuser:
        context['all_organizations'] = Organization.objects.all().order_by('name')
    
    return render(request, 'core/organization_select.html', context)

def login_view(request, org_slug=None):
    """LMS Login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Debug: Print authentication attempt
        print(f"Authentication attempt: username={username}, org_slug={org_slug}")
        
        # Force authentication to use default database (where users are stored)
        from lms.apps.tenants.db_router import clear_current_database, get_current_database, set_current_database
        from lms.apps.tenants.models import OrganizationUser
        current_db = get_current_database()
        print(f"Current DB before auth: {current_db}")
        
        clear_current_database()  # This ensures auth uses the default database
        print(f"Current DB after clear: {get_current_database()}")
        
        # Debug: Check if user exists - force using default database
        try:
            db_user = OrganizationUser.objects.using('default').get(username=username)
            print(f"User found in DB: {db_user.username}, active: {db_user.is_active}")
            print(f"User has usable password: {db_user.has_usable_password()}")
        except OrganizationUser.DoesNotExist:
            print(f"User {username} not found in database")
        
        user = authenticate(request, username=username, password=password)
        print(f"Authentication result: {user}")
        
        # Restore the previous database context after authentication
        if current_db != 'default':
            set_current_database(current_db)
        
        if user is not None:
            login(request, user)
            print(f"Login successful for: {user.username}")
            # Redirect to organization dashboard if in org context
            if org_slug:
                return redirect('org-core:dashboard', org_slug=org_slug)
            return redirect('core:dashboard')
        else:
            print("Authentication failed")
            messages.error(request, 'Invalid username or password')
    
    # Pass organization context to template
    context = {}
    if hasattr(request, 'organization') and request.organization:
        context['organization'] = request.organization
    return render(request, 'core/login.html', context)

@login_required
def logout_view(request, org_slug=None):
    """LMS Logout view"""
    logout(request)
    # Redirect to organization context if available
    if org_slug:
        return redirect('org-core:dashboard', org_slug=org_slug)
    return redirect('core:dashboard')