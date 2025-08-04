from django.core.management.base import BaseCommand
from jobs.models import Department, JobPosition


class Command(BaseCommand):
    help = 'Test if the jobs module is working correctly'

    def handle(self, *args, **options):
        self.stdout.write('Testing jobs module...')
        
        try:
            # Test if we can query the models
            dept_count = Department.objects.count()
            pos_count = JobPosition.objects.count()
            
            self.stdout.write(f'✅ Database queries work:')
            self.stdout.write(f'   - Departments: {dept_count}')
            self.stdout.write(f'   - Job Positions: {pos_count}')
            
            # Test creating a simple department
            dept, created = Department.objects.get_or_create(
                name='Test Department',
                defaults={'description': 'Test department for module verification'}
            )
            
            if created:
                self.stdout.write('✅ Created test department')
            else:
                self.stdout.write('✅ Test department already exists')
                
            self.stdout.write(
                self.style.SUCCESS('Jobs module is working correctly!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error: {str(e)}')
            )
            self.stdout.write(
                self.style.ERROR('Make sure to run: python manage.py migrate jobs')
            )