#!/usr/bin/env python3
"""
Deployment debugging script for Render
"""
import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(cmd, description=""):
    """Run a command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'stdout': '',
            'stderr': 'Command timed out',
            'returncode': -1
        }
    except Exception as e:
        return {
            'success': False,
            'stdout': '',
            'stderr': str(e),
            'returncode': -1
        }

def check_system_info():
    """Check system information"""
    print("==> System Information")
    print("-" * 40)
    
    # Python version
    print(f"Python version: {sys.version}")
    
    # Environment variables
    important_vars = [
        'PYTHON_VERSION', 'DJANGO_ENV', 'DEBUG', 'SECRET_KEY', 
        'DATABASE_URL', 'ALLOWED_HOSTS', 'PORT', 'RENDER'
    ]
    
    print("\nEnvironment Variables:")
    for var in important_vars:
        value = os.environ.get(var, 'NOT SET')
        if 'SECRET' in var or 'PASSWORD' in var:
            value = '[HIDDEN]' if value != 'NOT SET' else 'NOT SET'
        print(f"  {var}: {value}")
    
    # Working directory
    print(f"\nWorking directory: {os.getcwd()}")
    
    # Check if key files exist
    key_files = ['manage.py', 'build.sh', 'start.sh', 'requirements.txt', 'pyproject.toml']
    print("\nKey files:")
    for file in key_files:
        exists = Path(file).exists()
        print(f"  {file}: {'✅' if exists else '❌'}")

def check_python_packages():
    """Check Python package installation"""
    print("\n==> Python Packages")
    print("-" * 40)
    
    # Check pip
    pip_result = run_command("python3 -m pip --version")
    if pip_result['success']:
        print(f"pip: {pip_result['stdout'].strip()}")
    else:
        print(f"pip: ❌ {pip_result['stderr']}")
    
    # Check Poetry
    poetry_result = run_command("poetry --version")
    if poetry_result['success']:
        print(f"Poetry: {poetry_result['stdout'].strip()}")
    else:
        print("Poetry: Not available")
    
    # Try to import key packages
    key_packages = ['django', 'gunicorn', 'psycopg2', 'environ', 'whitenoise']
    print("\nKey package imports:")
    for package in key_packages:
        try:
            __import__(package)
            print(f"  {package}: ✅")
        except ImportError as e:
            print(f"  {package}: ❌ {e}")

def check_django_setup():
    """Check Django configuration"""
    print("\n==> Django Configuration")
    print("-" * 40)
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
    
    try:
        import django
        django.setup()
        from django.conf import settings
        
        print(f"Django version: {django.get_version()}")
        print(f"DEBUG: {settings.DEBUG}")
        print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        print(f"SECRET_KEY: {'✅ Set' if settings.SECRET_KEY else '❌ Not set'}")
        print(f"DATABASES: {'✅ Configured' if settings.DATABASES else '❌ Not configured'}")
        
        # Test database connection
        try:
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            print("Database connection: ✅")
        except Exception as e:
            print(f"Database connection: ❌ {e}")
            
    except Exception as e:
        print(f"Django setup failed: ❌ {e}")

def check_static_files():
    """Check static files configuration"""
    print("\n==> Static Files")
    print("-" * 40)
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
        import django
        django.setup()
        from django.conf import settings
        
        print(f"STATIC_URL: {settings.STATIC_URL}")
        print(f"STATIC_ROOT: {settings.STATIC_ROOT}")
        
        static_root = Path(settings.STATIC_ROOT)
        if static_root.exists():
            file_count = len(list(static_root.rglob('*')))
            print(f"Static files collected: ✅ ({file_count} files)")
        else:
            print("Static files collected: ❌ (directory doesn't exist)")
            
    except Exception as e:
        print(f"Static files check failed: ❌ {e}")

def check_health_endpoint():
    """Check if health endpoint works"""
    print("\n==> Health Endpoint")
    print("-" * 40)
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
        import django
        django.setup()
        
        from django.test import Client
        client = Client()
        response = client.get('/health/')
        
        print(f"Health endpoint status: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Health response: {json.dumps(data, indent=2)}")
            except:
                print(f"Health response: {response.content.decode()}")
        else:
            print(f"Health endpoint failed: {response.content}")
            
    except Exception as e:
        print(f"Health endpoint check failed: ❌ {e}")

def main():
    """Main debugging function"""
    print("🔍 Portal Deployment Debug Information")
    print("=" * 60)
    
    check_system_info()
    check_python_packages()
    check_django_setup()
    check_static_files()
    check_health_endpoint()
    
    print("\n" + "=" * 60)
    print("Debug information complete. Use this output to troubleshoot deployment issues.")

if __name__ == '__main__':
    main()