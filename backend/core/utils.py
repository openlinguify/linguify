"""
Utility functions for Django configuration.
"""
import os
from pathlib import Path
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie


def discover_project_apps(apps_directory=None, exclude_apps=None):
    """
    Automatically discover Django apps in the apps directory.
    
    Args:
        apps_directory (str): Path to the apps directory. If None, uses PROJECT_DIR/apps
        exclude_apps (list): List of app names to exclude from discovery
        
    Returns:
        list: List of app module paths ready for INSTALLED_APPS
    """
    if apps_directory is None:
        # Get the directory where settings.py is located
        settings_dir = Path(__file__).resolve().parent
        # Go up one level to get the project root (backend/)
        project_dir = settings_dir.parent
        apps_directory = project_dir / 'apps'
    else:
        apps_directory = Path(apps_directory)
    
    if exclude_apps is None:
        exclude_apps = []
    
    discovered_apps = []
    
    # Check if apps directory exists
    if not apps_directory.exists():
        return discovered_apps
    
    # Iterate through all directories in the apps folder
    for item in apps_directory.iterdir():
        if item.is_dir() and item.name != '__pycache__':
            app_name = item.name
            
            # Skip excluded apps
            if app_name in exclude_apps:
                continue
            
            # Check if the directory has an apps.py file (indicates it's a Django app)
            apps_py_file = item / 'apps.py'
            if apps_py_file.exists():
                discovered_apps.append(f'apps.{app_name}')
    
    # Sort for consistent ordering
    discovered_apps.sort()
    return discovered_apps


def get_installed_apps():
    """
    Get the complete list of INSTALLED_APPS including automatically discovered ones.
    
    Returns:
        list: Complete list of apps for INSTALLED_APPS
    """
    # Base Django and third-party apps
    base_apps = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.humanize',
        'django_extensions',
        'django_filters',
        'channels',
        'drf_spectacular',
    ]
    
    # Apps to exclude from automatic discovery (commented out or problematic ones)
    exclude_from_discovery = [
        'coaching',          # Commented out in original INSTALLED_APPS
        'payments',          # Commented out in original INSTALLED_APPS
        'task',              # Commented out in original INSTALLED_APPS
        'screen',            # Not a complete app - no apps.py
        'subscription',      # Commented out in original INSTALLED_APPS
        'language_learning', # Now ready for use
        'teaching',          # Temporarily hidden - work in progress
    ]
    
    # Automatically discover project apps
    project_apps = discover_project_apps(exclude_apps=exclude_from_discovery)
    
    # Non-app modules and special cases
    other_apps = [
        'app_manager',      # Located at root level, not in apps/
        'saas_web',         # Web interface
        'core.apps.CoreConfig',
        'rest_framework',
        'rest_framework.authtoken',
        'corsheaders',
    ]
    
    # Combine all apps
    all_apps = base_apps + project_apps + other_apps
    
    return all_apps


@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({'csrfToken': get_token(request)})


if __name__ == '__main__':
    # For testing/debugging
    print("Discovered apps:")
    apps = discover_project_apps()
    for app in apps:
        print(f"  - {app}")
    
    print("\nComplete INSTALLED_APPS list:")
    all_apps = get_installed_apps()
    for app in all_apps:
        print(f"  - {app}")