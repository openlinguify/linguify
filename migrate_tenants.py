#!/usr/bin/env python
"""
Script to run migrations on all tenant databases
"""
import os
import django
from django.core.management import call_command

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms.settings')
django.setup()

from django.conf import settings
from lms.apps.tenants.models import Organization

def migrate_all_tenants():
    """Run migrations on all tenant databases"""
    print("=== Migration des bases de donnees tenant ===")
    
    # Get all organizations
    organizations = Organization.objects.all()
    print(f"Organisations trouvees: {[org.name for org in organizations]}")
    
    for org in organizations:
        try:
            db_name = org.database_name
            print(f"\nMigration de {org.name} (database: {db_name})")
            
            # Add database to settings if not already there
            if db_name not in settings.DATABASES:
                default_db = settings.DATABASES['default']
                settings.DATABASES[db_name] = {
                    'ENGINE': default_db['ENGINE'],
                    'NAME': db_name,
                    'USER': default_db['USER'],
                    'PASSWORD': default_db['PASSWORD'],
                    'HOST': default_db['HOST'],
                    'PORT': default_db['PORT'],
                }
                # Copy additional options if they exist
                if 'OPTIONS' in default_db:
                    settings.DATABASES[db_name]['OPTIONS'] = default_db['OPTIONS']
                print(f"  - Database configured: {db_name}")
            
            # Run migrations for students app
            print(f"  - Migration de l'app students...")
            call_command('migrate', 'students', database=db_name, verbosity=1)
            print(f"  - Migration terminee pour {org.name}")
            
        except Exception as e:
            print(f"  ERREUR lors de la migration de {org.name}: {e}")
    
    print("\n=== Migrations terminees ===")

if __name__ == '__main__':
    migrate_all_tenants()