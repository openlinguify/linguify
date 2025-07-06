"""
Management command to test job application status change notifications
"""

from django.core.management.base import BaseCommand
from django.core import mail
from django.utils import timezone
from jobs.models import Department, JobPosition, JobApplication


class Command(BaseCommand):
    help = 'Test job application status change email notifications'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default='test@example.com',
            help='Email address to use for test application'
        )
        parser.add_argument(
            '--status',
            type=str,
            choices=['reviewed', 'interview', 'offer', 'hired', 'rejected', 'withdrawn'],
            help='Status to change to (if not provided, will cycle through all)'
        )

    def handle(self, *args, **options):
        self.stdout.write("Testing job application status notifications...")
        
        # Create test data
        department, _ = Department.objects.get_or_create(
            name="Test Department",
            defaults={'description': 'Department for testing'}
        )
        
        position, _ = JobPosition.objects.get_or_create(
            title="Test Position",
            department=department,
            defaults={
                'location': 'Test Location',
                'employment_type': 'full_time',
                'experience_level': 'mid',
                'description': 'Test description',
                'requirements': 'Test requirements',
                'responsibilities': 'Test responsibilities',
                'application_email': 'hr@test.com'
            }
        )
        
        # Create or get test application
        application, created = JobApplication.objects.get_or_create(
            position=position,
            email=options['email'],
            defaults={
                'first_name': 'Test',
                'last_name': 'User',
                'phone': '0123456789',
                'cover_letter': 'This is a test application',
                'status': 'submitted'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created new test application for {options['email']}"))
        else:
            self.stdout.write(f"Using existing application for {options['email']}")
            # Reset to submitted status
            application.status = 'submitted'
            application.save()
        
        # Clear mail outbox
        mail.outbox = []
        
        if options['status']:
            # Test specific status
            statuses = [options['status']]
        else:
            # Test all statuses
            statuses = ['reviewed', 'interview', 'offer', 'hired', 'rejected']
        
        for status in statuses:
            self.stdout.write(f"\nTesting status change to '{status}'...")
            
            # Clear mail outbox
            mail.outbox = []
            
            # Change status
            old_status = application.status
            application.status = status
            application.save()
            
            # Check emails sent
            self.stdout.write(f"  Old status: {old_status}")
            self.stdout.write(f"  New status: {status}")
            self.stdout.write(f"  Emails sent: {len(mail.outbox)}")
            
            for i, email in enumerate(mail.outbox):
                self.stdout.write(f"\n  Email {i+1}:")
                self.stdout.write(f"    To: {', '.join(email.to)}")
                self.stdout.write(f"    Subject: {email.subject}")
                self.stdout.write(f"    Has HTML: {'Yes' if email.alternatives else 'No'}")
                
                # Show preview of email body
                preview = email.body[:200].replace('\n', ' ')
                if len(email.body) > 200:
                    preview += '...'
                self.stdout.write(f"    Preview: {preview}")
        
        self.stdout.write(self.style.SUCCESS("\nTest completed successfully!"))
        self.stdout.write(f"Total emails sent: {len(mail.outbox)}")
        
        # Cleanup - reset to submitted
        application.status = 'submitted'
        application.save()