"""
Script to set up organizations and memberships for the LMS
"""
import os
import sys
import django

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms.settings')
django.setup()

from apps.tenants.models import Organization, OrganizationUser, OrganizationMembership
from apps.tenants.utils import create_tenant_database

def setup_organizations():
    """Create organizations and add user as owner"""
    
    # Get the superuser
    try:
        # TODO: Update with admin email from environment variable
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
        user = OrganizationUser.objects.get(email=admin_email)
        print(f"Found user: {user.username}")
    except OrganizationUser.DoesNotExist:
        print("User not found. Please create superuser first.")
        return

    organizations = [
        {'name': 'MIT', 'slug': 'mit', 'email': 'admin@mit.edu'},
        {'name': 'Harvard University', 'slug': 'harvard', 'email': 'admin@harvard.edu'},
        {'name': 'Stanford University', 'slug': 'stanford', 'email': 'admin@stanford.edu'},
    ]

    for org_data in organizations:
        print(f"\n--- Setting up {org_data['name']} ---")
        
        # Create or get organization
        organization, created = Organization.objects.get_or_create(
            slug=org_data['slug'],
            defaults={
                'name': org_data['name'],
                'email': org_data['email'],
                'plan': 'trial',
                'is_active': True
            }
        )
        
        if created:
            print(f"Created organization: {organization.name}")
            
            # Create database for organization
            try:
                print(f"Creating database: {organization.database_name}")
                create_tenant_database(organization)
                print(f"Database created successfully")
            except Exception as e:
                print(f"Database creation error: {e}")
        else:
            print(f"Organization already exists: {organization.name}")

        # Add user as owner
        membership, created = OrganizationMembership.objects.get_or_create(
            user=user,
            organization=organization,
            defaults={
                'role': 'owner',
                'is_default': org_data['slug'] == 'mit'  # MIT as default
            }
        )
        
        if created:
            print(f"Added {user.username} as owner of {organization.name}")
        else:
            print(f"{user.username} already member of {organization.name}")

    print("\n--- Setup complete! ---")
    print("\nYou can now access:")
    for org_data in organizations:
        print(f"- http://127.0.0.1:8000/org/{org_data['slug']}/")

if __name__ == "__main__":
    setup_organizations()