#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import argparse

def main():
    """Run administrative tasks."""
    parser = argparse.ArgumentParser(description='Django management utility')
    parser.add_argument('--project', choices=['backend', 'lms'], default='backend', 
                       help='Specify which project to manage (default: backend)')
    parser.add_argument('command', nargs='?', default='help')
    parser.add_argument('args', nargs='*')
    
    # Parse known args to get the project
    known_args, remaining_args = parser.parse_known_args()
    
    # Set the appropriate settings module
    if known_args.project == 'lms':
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms.settings')
        print(f"Managing LMS project...")
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
        print(f"Managing Backend project...")
    
    # Reconstruct sys.argv for Django
    sys.argv = [sys.argv[0]] + [known_args.command] + known_args.args + remaining_args
    
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