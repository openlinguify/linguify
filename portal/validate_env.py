#!/usr/bin/env python3
"""
Environment validation script for Portal deployment
"""
import os
import sys

def validate_environment():
    """Validate required environment variables for production deployment"""
    print("==> Starting environment validation...")
    
    # Required environment variables
    required_vars = [
        'SECRET_KEY',
        'DATABASE_URL',
        'DJANGO_ENV',
        'ALLOWED_HOSTS'
    ]
    
    # Optional but recommended variables
    optional_vars = [
        'DEBUG',
        'BACKEND_API_URL',
        'PYTHON_VERSION'
    ]
    
    # Check required variables
    missing_vars = []
    for var in required_vars:
        value = os.environ.get(var)
        if not value:
            missing_vars.append(var)
        else:
            # Don't log secret values
            if 'SECRET' in var or 'PASSWORD' in var:
                print(f"✅ {var}: [HIDDEN]")
            elif len(value) > 100:
                print(f"✅ {var}: {value[:50]}... [TRUNCATED]")
            else:
                print(f"✅ {var}: {value}")
    
    # Check optional variables
    for var in optional_vars:
        value = os.environ.get(var)
        if value:
            print(f"ℹ️  {var}: {value}")
        else:
            print(f"⚠️  {var}: Not set (optional)")
    
    if missing_vars:
        print(f"\n❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please ensure these environment variables are configured in your Render service settings.")
        return False
    
    # Validate specific values
    django_env = os.environ.get('DJANGO_ENV')
    if django_env not in ['production', 'development', 'staging']:
        print(f"❌ DJANGO_ENV should be 'production', 'development', or 'staging', got: {django_env}")
        return False
    
    debug = os.environ.get('DEBUG', 'True').lower()
    if django_env == 'production' and debug == 'true':
        print("⚠️  Warning: DEBUG=True in production environment")
        print("   Consider setting DEBUG=False for production deployments")
    
    # Validate ALLOWED_HOSTS format
    allowed_hosts = os.environ.get('ALLOWED_HOSTS', '')
    if ',' in allowed_hosts:
        hosts = [h.strip() for h in allowed_hosts.split(',')]
        print(f"ℹ️  Parsed ALLOWED_HOSTS: {hosts}")
    
    # Check DATABASE_URL format
    database_url = os.environ.get('DATABASE_URL', '')
    if database_url and not database_url.startswith(('postgres://', 'postgresql://')):
        print("⚠️  DATABASE_URL doesn't appear to be a PostgreSQL URL")
        print("   Make sure it starts with 'postgres://' or 'postgresql://'")
    
    print("\n✅ Environment validation passed")
    return True

def check_python_environment():
    """Check Python environment and dependencies"""
    print("==> Checking Python environment...")
    
    # Check Python version
    python_version = sys.version_info
    print(f"ℹ️  Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 11):
        print("⚠️  Warning: Python version is below 3.11. Some features may not work correctly.")
    
    # Check if we can import Django
    try:
        import django
        print(f"✅ Django version: {django.get_version()}")
    except ImportError:
        print("❌ Django is not installed")
        return False
    
    return True

if __name__ == '__main__':
    print("🔍 Portal Environment Validation")
    print("=" * 50)
    
    env_success = validate_environment()
    python_success = check_python_environment()
    
    overall_success = env_success and python_success
    
    if overall_success:
        print("\n🎉 All validations passed!")
    else:
        print("\n💥 Some validations failed. Please check the errors above.")
    
    sys.exit(0 if overall_success else 1)