#!/usr/bin/env python
"""
Script pour créer des profils étudiants de test
"""
import os
import django
from datetime import date, datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms.settings')
django.setup()

from lms.apps.tenants.models import Organization, OrganizationUser, OrganizationMembership
from lms.apps.students.models import StudentProfile, CourseEnrollment

def create_student_profiles():
    """Créer des profils étudiants pour les organisations existantes"""
    
    # Obtenir les organisations
    organizations = Organization.objects.all()
    print(f"Organisations trouvées: {[org.name for org in organizations]}")
    
    # Données d'étudiants de test
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
        },
        {
            'username': 'maria.garcia',
            'first_name': 'Maria',
            'last_name': 'Garcia',
            'email': 'maria.garcia@mit.edu',
            'org_slug': 'mit',
            'student_id': 'MIT2024004',
            'program': 'Electrical Engineering',
            'academic_year': '4',
            'specialization': 'Signal Processing',
            'gpa': 3.85,
            'credits_earned': 110,
            'study_mode': 'full_time'
        }
    ]
    
    for student_data in students_data:
        try:
            # Trouver l'organisation
            org = Organization.objects.get(slug=student_data['org_slug'])
            print(f"\nTraitement de {student_data['username']} pour {org.name}")
            
            # Vérifier si l'utilisateur existe déjà
            user, user_created = OrganizationUser.objects.get_or_create(
                username=student_data['username'],
                defaults={
                    'email': student_data['email'],
                    'first_name': student_data['first_name'],
                    'last_name': student_data['last_name'],
                }
            )
            
            if user_created:
                user.set_password('password123')  # Mot de passe de test
                user.save()
                print(f"  - Utilisateur créé: {user.username}")
            else:
                print(f"  - Utilisateur existant: {user.username}")
            
            # Créer/obtenir l'appartenance à l'organisation
            membership, membership_created = OrganizationMembership.objects.get_or_create(
                user=user,
                organization=org,
                defaults={'role': 'student'}
            )
            
            if membership_created:
                print(f"  - Appartenance créée avec le rôle: {membership.role}")
            else:
                print(f"  - Appartenance existante avec le rôle: {membership.role}")
            
            # Créer le profil étudiant
            profile, profile_created = StudentProfile.objects.get_or_create(
                user=user,
                defaults={
                    'student_id': student_data['student_id'],
                    'organization_id': org.slug,
                    'program': student_data['program'],
                    'academic_year': student_data['academic_year'],
                    'specialization': student_data['specialization'],
                    'enrollment_date': date(2024, 9, 1),
                    'expected_graduation': date(2028, 6, 1),
                    'status': 'active',
                    'study_mode': student_data['study_mode'],
                    'gpa': student_data['gpa'],
                    'credits_earned': student_data['credits_earned'],
                    'credits_required': 120,
                    'emergency_contact_name': f"Parent de {student_data['first_name']}",
                    'emergency_contact_phone': '+1-555-0123',
                    'emergency_contact_relation': 'Parent'
                }
            )
            
            if profile_created:
                print(f"  - Profil étudiant créé: {profile.student_id}")
                
                # Ajouter quelques inscriptions de cours fictives
                courses_data = [
                    {'course_id': 'CS101', 'course_name': 'Introduction to Programming', 'credits': 3},
                    {'course_id': 'MATH201', 'course_name': 'Linear Algebra', 'credits': 4},
                    {'course_id': 'ENG100', 'course_name': 'Academic Writing', 'credits': 3},
                ]
                
                for course_data in courses_data:
                    enrollment, enroll_created = CourseEnrollment.objects.get_or_create(
                        student=profile,
                        course_id=course_data['course_id'],
                        defaults={
                            'course_name': course_data['course_name'],
                            'credits': course_data['credits'],
                            'status': 'enrolled'
                        }
                    )
                    if enroll_created:
                        print(f"    - Inscription créée: {course_data['course_name']}")
                        
            else:
                print(f"  - Profil étudiant existant: {profile.student_id}")
                
        except Organization.DoesNotExist:
            print(f"ERREUR: Organisation '{student_data['org_slug']}' non trouvée")
        except Exception as e:
            print(f"ERREUR lors de la création de {student_data['username']}: {e}")

if __name__ == '__main__':
    print("=== Création des profils étudiants de test ===")
    create_student_profiles()
    print("\n=== Terminé ===")