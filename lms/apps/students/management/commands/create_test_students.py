from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings
from datetime import date
from lms.apps.tenants.models import Organization, OrganizationUser, OrganizationMembership
from lms.apps.students.models import StudentProfile, CourseEnrollment


class Command(BaseCommand):
    help = 'Create test student profiles for existing organizations'

    def handle(self, *args, **options):
        self.stdout.write("=== Creation des profils etudiants de test ===")
        
        # Obtenir les organisations
        organizations = Organization.objects.all()
        self.stdout.write(f"Organisations trouvees: {[org.name for org in organizations]}")
        
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
                self.stdout.write(f"\nTraitement de {student_data['username']} pour {org.name}")
                
                # S'assurer que la base de données tenant est configurée
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
                
                # Créer/obtenir l'utilisateur dans la base principale
                user, user_created = OrganizationUser.objects.using('default').get_or_create(
                    username=student_data['username'],
                    defaults={
                        'email': student_data['email'],
                        'first_name': student_data['first_name'],
                        'last_name': student_data['last_name'],
                    }
                )
                
                if user_created:
                    user.set_password('password123')  # Mot de passe de test
                    user.save(using='default')
                    self.stdout.write(f"  - Utilisateur cree: {user.username}")
                else:
                    self.stdout.write(f"  - Utilisateur existant: {user.username}")
                
                # Créer/obtenir l'appartenance à l'organisation
                membership, membership_created = OrganizationMembership.objects.using('default').get_or_create(
                    user=user,
                    organization=org,
                    defaults={'role': 'student'}
                )
                
                if membership_created:
                    self.stdout.write(f"  - Appartenance creee avec le role: {membership.role}")
                else:
                    self.stdout.write(f"  - Appartenance existante avec le role: {membership.role}")
                
                # Créer le profil étudiant dans la base tenant
                try:
                    # Tenter de créer la table si elle n'existe pas
                    from django.core.management import call_command
                    call_command('migrate', 'students', database=db_name, verbosity=0)
                    
                    profile, profile_created = StudentProfile.objects.using(db_name).get_or_create(
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
                        self.stdout.write(f"  - Profil etudiant cree: {profile.student_id}")
                        
                        # Ajouter quelques inscriptions de cours fictives
                        courses_data = [
                            {'course_id': 'CS101', 'course_name': 'Introduction to Programming', 'credits': 3},
                            {'course_id': 'MATH201', 'course_name': 'Linear Algebra', 'credits': 4},
                            {'course_id': 'ENG100', 'course_name': 'Academic Writing', 'credits': 3},
                        ]
                        
                        for course_data in courses_data:
                            enrollment, enroll_created = CourseEnrollment.objects.using(db_name).get_or_create(
                                student=profile,
                                course_id=course_data['course_id'],
                                defaults={
                                    'course_name': course_data['course_name'],
                                    'credits': course_data['credits'],
                                    'status': 'enrolled'
                                }
                            )
                            if enroll_created:
                                self.stdout.write(f"    - Inscription creee: {course_data['course_name']}")
                                
                    else:
                        self.stdout.write(f"  - Profil etudiant existant: {profile.student_id}")
                        
                except Exception as migrate_error:
                    self.stdout.write(f"    ERREUR migration/creation profil: {migrate_error}")
                    
            except Organization.DoesNotExist:
                self.stdout.write(f"ERREUR: Organisation '{student_data['org_slug']}' non trouvee")
            except Exception as e:
                self.stdout.write(f"ERREUR lors de la creation de {student_data['username']}: {e}")

        self.stdout.write("\n=== Termine ===")