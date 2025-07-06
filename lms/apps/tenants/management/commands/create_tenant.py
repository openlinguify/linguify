"""
Management command to create a new tenant (organization) with its database
"""

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from lms.apps.tenants.models import Organization, OrganizationUser, OrganizationMembership
from lms.apps.tenants.utils import create_tenant_database


class Command(BaseCommand):
    help = 'Create a new tenant organization with its own database'
    
    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='Organization name')
        parser.add_argument('--email', type=str, required=True, help='Organization email')
        parser.add_argument('--slug', type=str, help='URL slug (auto-generated if not provided)')
        parser.add_argument('--owner-email', type=str, help='Email of the owner user')
        parser.add_argument('--plan', type=str, default='trial', help='Subscription plan')
        
    def handle(self, *args, **options):
        name = options['name']
        email = options['email']
        slug = options.get('slug') or slugify(name)
        owner_email = options.get('owner_email')
        plan = options['plan']
        
        # Check if organization already exists
        if Organization.objects.filter(slug=slug).exists():
            self.stdout.write(
                self.style.ERROR(f'Organization with slug "{slug}" already exists')
            )
            return
        
        # Create organization
        self.stdout.write(f'Creating organization "{name}"...')
        
        organization = Organization.objects.create(
            name=name,
            slug=slug,
            email=email,
            plan=plan
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Created organization: {organization.name}')
        )
        
        # Create database
        self.stdout.write(f'Creating database for {organization.name}...')
        
        try:
            create_tenant_database(organization)
            self.stdout.write(
                self.style.SUCCESS(f'Created database: {organization.database_name}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to create database: {str(e)}')
            )
            # Clean up organization
            organization.delete()
            return
        
        # Link owner user if provided
        if owner_email:
            try:
                user = OrganizationUser.objects.get(email=owner_email)
                OrganizationMembership.objects.create(
                    user=user,
                    organization=organization,
                    role='owner',
                    is_default=True
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Linked owner: {owner_email}')
                )
            except OrganizationUser.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Owner user not found: {owner_email}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nOrganization "{name}" created successfully!\n'
                f'Database: {organization.database_name}\n'
                f'Access URL: https://{slug}.lms.linguify.com'
            )
        )