#!/usr/bin/env python3
"""
Environment validation script for Portal deployment
"""
import os
import sys

def validate_environment():
    """Validate required environment variables for production deployment"""
    required_vars = [
        'SECRET_KEY',
        'DATABASE_URL',
        'DJANGO_ENV',
        'ALLOWED_HOSTS'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    # Validate specific values
    django_env = os.environ.get('DJANGO_ENV')
    if django_env not in ['production', 'development']:
        print(f"❌ DJANGO_ENV should be 'production' or 'development', got: {django_env}")
        return False
    
    debug = os.environ.get('DEBUG', 'True').lower()
    if django_env == 'production' and debug == 'true':
        print("⚠️  Warning: DEBUG=True in production environment")
    
    print("✅ Environment validation passed")
    return True

if __name__ == '__main__':
    success = validate_environment()
    sys.exit(0 if success else 1)