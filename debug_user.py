#!/usr/bin/env python
"""
Script pour débugger les permissions utilisateur
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms.settings')
django.setup()

from lms.apps.tenants.models import Organization, OrganizationUser, OrganizationMembership

def debug_user_permissions():
    print("=== DEBUG PERMISSIONS UTILISATEUR ===")
    
    # Get current admin user
    try:
        admin_user = OrganizationUser.objects.get(username='admin')
        print(f"Utilisateur trouvé: {admin_user.username}")
        print(f"- is_superuser: {admin_user.is_superuser}")
        print(f"- is_staff: {admin_user.is_staff}")
        print(f"- is_active: {admin_user.is_active}")
        
        # Check memberships
        memberships = OrganizationMembership.objects.filter(user=admin_user)
        print(f"\nAppartenances ({memberships.count()}):")
        for membership in memberships:
            print(f"- {membership.organization.name}: {membership.role}")
            
        # Get MIT org
        try:
            mit_org = Organization.objects.get(slug='mit')
            print(f"\nOrganisation MIT trouvée: {mit_org.name}")
            print(f"- Database: {mit_org.database_name}")
            
            # Check MIT membership
            try:
                mit_membership = OrganizationMembership.objects.get(user=admin_user, organization=mit_org)
                print(f"- Rôle dans MIT: {mit_membership.role}")
            except OrganizationMembership.DoesNotExist:
                print("- PAS D'APPARTENANCE À MIT!")
                
                # Create membership for admin
                membership = OrganizationMembership.objects.create(
                    user=admin_user,
                    organization=mit_org,
                    role='owner'
                )
                print(f"- APPARTENANCE CRÉÉE: {membership.role}")
                
        except Organization.DoesNotExist:
            print("Organisation MIT non trouvée!")
            
    except OrganizationUser.DoesNotExist:
        print("Utilisateur admin non trouvé!")
        
        # List all users
        users = OrganizationUser.objects.all()
        print(f"Utilisateurs disponibles ({users.count()}):")
        for user in users:
            print(f"- {user.username} (superuser: {user.is_superuser})")

if __name__ == '__main__':
    debug_user_permissions()