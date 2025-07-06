"""
Django management command to set up organizations and memberships
"""
from django.core.management.base import BaseCommand
from lms.apps.tenants.models import Organization, OrganizationUser, OrganizationMembership
from lms.apps.tenants.utils import create_tenant_database


class Command(BaseCommand):
    help = 'Set up default organizations and memberships for testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--email', 
            type=str, 
            default='louisphilippelalou@outlook.com',
            help='Email of the user to make owner of organizations'
        )
    
    def handle(self, *args, **options):
        email = options['email']
        
        # Get the user
        try:
            user = OrganizationUser.objects.get(email=email)
            self.stdout.write(f"Found user: {user.username}")
        except OrganizationUser.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"User with email {email} not found. Please create superuser first.")
            )
            return

        organizations = [
            {'name': 'MIT', 'slug': 'mit', 'email': 'admin@mit.edu'},
            {'name': 'Harvard University', 'slug': 'harvard', 'email': 'admin@harvard.edu'},
            {'name': 'Stanford University', 'slug': 'stanford', 'email': 'admin@stanford.edu'},
        ]

        for org_data in organizations:
            self.stdout.write(f"\n--- Setting up {org_data['name']} ---")
            
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
                self.stdout.write(
                    self.style.SUCCESS(f"Created organization: {organization.name}")
                )
                
                # Create database for organization
                try:
                    self.stdout.write(f"Creating database: {organization.database_name}")
                    create_tenant_database(organization)
                    self.stdout.write(
                        self.style.SUCCESS("Database created successfully")
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f"Database creation error: {e}")
                    )
            else:
                self.stdout.write(f"Organization already exists: {organization.name}")

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
                self.stdout.write(
                    self.style.SUCCESS(f"Added {user.username} as owner of {organization.name}")
                )
            else:
                self.stdout.write(f"{user.username} already member of {organization.name}")

        self.stdout.write(
            self.style.SUCCESS("\n--- Setup complete! ---")
        )
        self.stdout.write("\nYou can now access:")
        for org_data in organizations:
            self.stdout.write(f"- http://127.0.0.1:8000/org/{org_data['slug']}/")
        
        self.stdout.write(
            self.style.SUCCESS(f"\nUser {user.username} is now owner of all organizations!")
        )