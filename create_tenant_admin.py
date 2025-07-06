#!/usr/bin/env python
"""
Script pour créer des interfaces admin spécifiques aux tenants
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms.settings')
django.setup()

from django.conf import settings
from lms.apps.tenants.models import Organization

def create_tenant_admin_urls():
    """Créer des URLs admin pour chaque tenant"""
    organizations = Organization.objects.all()
    
    print("=== URLs Admin par Organisation ===")
    print("\nPour accéder aux données étudiantes de chaque organisation :")
    
    for org in organizations:
        print(f"\n🏫 {org.name}")
        print(f"   Dashboard Admin: /org/{org.slug}/admin/")
        print(f"   Students: /org/{org.slug}/admin/students/")
        print(f"   Database: {org.database_name}")
        
    print("\n=== Connexion ===")
    print("Utilisez votre compte admin avec les mêmes identifiants")
    print("L'interface s'adaptera automatiquement à l'organisation")

if __name__ == '__main__':
    create_tenant_admin_urls()