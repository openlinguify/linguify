#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import argparse

def print_help():
    """Print help message for Linguify projects"""
    print("\n" + "="*60)
    print("🌐 LINGUIFY PROJECT MANAGER")
    print("="*60 + "\n")
    
    print("Available projects:")
    print("  • backend (default) - Linguify Particulier")
    print("  • lms              - Linguify LMS for institutions")
    print("  • portal           - Linguify Portal (main entry point)")
    
    print("\nUsage examples:")
    print("  python manage.py backend runserver        # Run backend on port 8000")
    print("  python manage.py lms runserver 8001       # Run LMS on port 8001")
    print("  python manage.py portal runserver 8080    # Run portal on port 8080")
    
    print("\nOther commands:")
    print("  python manage.py backend migrate          # Run backend migrations")
    print("  python manage.py lms createsuperuser      # Create LMS admin user")
    print("  python manage.py portal collectstatic     # Collect portal static files")
    
    print("\nRecommended ports:")
    print("  • Backend: 8000")
    print("  • LMS:     8001")
    print("  • Portal:  8080")
    print("\n" + "="*60 + "\n")

def main():
    """Run administrative tasks."""
    # Check if first argument is a project name (for simpler syntax)
    if len(sys.argv) > 1 and sys.argv[1] in ['backend', 'lms', 'portal']:
        project = sys.argv[1]
        # Remove project from argv so Django doesn't see it
        sys.argv.pop(1)
    else:
        # Use argparse for --project syntax (backward compatibility)
        parser = argparse.ArgumentParser(description='Django management utility', add_help=False)
        parser.add_argument('--project', choices=['backend', 'lms', 'portal'], default='backend')
        parser.add_argument('--help', '-h', action='store_true', help='Show this help message')
        
        # Parse only --project and --help
        known_args, remaining = parser.parse_known_args()
        
        if known_args.help or (len(sys.argv) == 1):
            print_help()
            sys.exit(0)
            
        project = known_args.project
        
        # Remove --project from sys.argv if it was used
        if '--project' in sys.argv:
            idx = sys.argv.index('--project')
            sys.argv.pop(idx)  # Remove --project
            if idx < len(sys.argv) and sys.argv[idx] in ['backend', 'lms', 'portal']:
                sys.argv.pop(idx)  # Remove the value
    
    # Configure the appropriate project
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    if project == 'lms':
        sys.path.insert(0, os.path.join(base_dir, 'lms'))
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms.settings')
        print(f"🎓 Managing Linguify LMS...")
    elif project == 'portal':
        sys.path.insert(0, os.path.join(base_dir, 'portal'))
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
        print(f"🌐 Managing Linguify Portal...")
    else:
        sys.path.insert(0, os.path.join(base_dir, 'backend'))
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
        print(f"📚 Managing Linguify Particulier (Backend)...")
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()