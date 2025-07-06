#!/usr/bin/env python
"""
Script to create student profiles directly using Django shell
"""
import os
import django
from datetime import date

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms.settings')
django.setup()

from django.conf import settings
from lms.apps.tenants.models import Organization, OrganizationUser, OrganizationMembership

def create_students():
    print("=== Creation des profils etudiants de test ===")
    
    # Get organizations
    organizations = Organization.objects.all()
    print(f"Organisations trouvees: {[org.name for org in organizations]}")
    
    # Student test data
    students_data = [
        {
            'username': 'john.doe',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@mit.edu',
            'org_slug': 'mit',
            'student_id': 'MIT2024001',
            'program': 'Computer Science',
            'academic_year': '3',
            'specialization': 'Machine Learning',
            'gpa': 3.75,
            'credits_earned': 90,
            'study_mode': 'full_time'
        },
        {
            'username': 'alice.smith',
            'first_name': 'Alice',
            'last_name': 'Smith',
            'email': 'alice.smith@harvard.edu',
            'org_slug': 'harvard',
            'student_id': 'HRV2024002',
            'program': 'Law',
            'academic_year': '2',
            'specialization': 'International Law',
            'gpa': 3.90,
            'credits_earned': 60,
            'study_mode': 'full_time'
        },
        {
            'username': 'bob.johnson',
            'first_name': 'Bob',
            'last_name': 'Johnson',
            'email': 'bob.johnson@stanford.edu',
            'org_slug': 'stanford',
            'student_id': 'STF2024003',
            'program': 'Business Administration',
            'academic_year': '1',
            'specialization': '',
            'gpa': 3.50,
            'credits_earned': 30,
            'study_mode': 'full_time'
        }
    ]
    
    for student_data in students_data:
        try:
            # Find organization
            org = Organization.objects.get(slug=student_data['org_slug'])
            print(f"\nTraitement de {student_data['username']} pour {org.name}")
            
            # Setup tenant database connection
            db_name = org.database_name
            if db_name not in settings.DATABASES:
                settings.DATABASES[db_name] = {
                    'ENGINE': 'django.db.backends.postgresql',
                    'NAME': db_name,
                    'USER': settings.DATABASES['default']['USER'],
                    'PASSWORD': settings.DATABASES['default']['PASSWORD'],
                    'HOST': settings.DATABASES['default']['HOST'],
                    'PORT': settings.DATABASES['default']['PORT'],
                }
                print(f"  - Database configured: {db_name}")
            
            # Create/get user in main database
            user, user_created = OrganizationUser.objects.using('default').get_or_create(
                username=student_data['username'],
                defaults={
                    'email': student_data['email'],
                    'first_name': student_data['first_name'],
                    'last_name': student_data['last_name'],
                }
            )
            
            if user_created:
                user.set_password('password123')
                user.save(using='default')
                print(f"  - Utilisateur cree: {user.username}")
            else:
                print(f"  - Utilisateur existant: {user.username}")
            
            # Create/get organization membership
            membership, membership_created = OrganizationMembership.objects.using('default').get_or_create(
                user=user,
                organization=org,
                defaults={'role': 'student'}
            )
            
            if membership_created:
                print(f"  - Appartenance creee avec le role: {membership.role}")
            else:
                print(f"  - Appartenance existante avec le role: {membership.role}")
                if membership.role != 'student':
                    membership.role = 'student'
                    membership.save(using='default')
                    print(f"  - Role mis a jour vers: student")
                    
            print(f"  - Etudiant configure avec succes!")
            
        except Organization.DoesNotExist:
            print(f"ERREUR: Organisation '{student_data['org_slug']}' non trouvee")
        except Exception as e:
            print(f"ERREUR lors de la creation de {student_data['username']}: {e}")
    
    print("\n=== Configuration terminee ===")
    print("\nNOTE: Les profils academiques detailles seront crees automatiquement")
    print("lors de la premiere connexion de chaque etudiant.")

if __name__ == '__main__':
    create_students()