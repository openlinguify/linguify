"""
Tests for status change email notifications
"""

import tempfile
from unittest.mock import patch, MagicMock

from django.test import TestCase, override_settings
from django.utils import timezone
from django.core import mail
from django.contrib.admin.sites import site
from django.contrib.auth import get_user_model
from django.test import RequestFactory

from core.jobs.models import Department, JobPosition, JobApplication
from core.jobs.admin import JobApplicationAdmin

User = get_user_model()


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    MEDIA_ROOT=tempfile.mkdtemp()
)
class StatusNotificationTests(TestCase):
    """Tests for status change email notifications"""
    
    def setUp(self):
        self.department = Department.objects.create(
            name="Engineering",
            description="Software development team"
        )
        
        self.position = JobPosition.objects.create(
            title="Senior Python Developer",
            department=self.department,
            location="Paris, France",
            employment_type="full_time",
            experience_level="senior",
            description="We are looking for a senior Python developer",
            requirements="5+ years of Python experience",
            responsibilities="Develop and maintain applications",
            application_email="test@linguify.com"
        )
        
        self.application = JobApplication.objects.create(
            position=self.position,
            first_name="Test",
            last_name="User",
            email="test@example.com",
            phone="0123456789",
            cover_letter="I am interested in this position",
            status='submitted'
        )
        
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass'
        )
        
        # Clear mail outbox
        mail.outbox = []
    
    def test_status_change_to_reviewed_sends_emails(self):
        """Test that changing status to 'reviewed' sends both HR and candidate emails"""
        self.application.status = 'reviewed'
        self.application.save()
        
        # Should send only candidate email (reviewed is not in hr_notification_statuses)
        self.assertEqual(len(mail.outbox), 1)
        
        # Check candidate email
        candidate_email = mail.outbox[0]
        self.assertEqual(candidate_email.to, ["test@example.com"])
        self.assertIn("under review", candidate_email.subject)
        self.assertIn("Test", candidate_email.body)
        self.assertIn("being reviewed", candidate_email.body)
    
    def test_status_change_to_interview_sends_emails(self):
        """Test that changing status to 'interview' sends both HR and candidate emails"""
        self.application.status = 'interview'
        self.application.save()
        
        # Should send both HR and candidate emails
        self.assertEqual(len(mail.outbox), 2)
        
        # Find HR and candidate emails
        hr_email = next((e for e in mail.outbox if e.to == ['linguify.info@gmail.com']), None)
        candidate_email = next((e for e in mail.outbox if e.to == ['test@example.com']), None)
        
        self.assertIsNotNone(hr_email)
        self.assertIsNotNone(candidate_email)
        
        # Check HR email
        self.assertIn("Status Update", hr_email.subject)
        self.assertIn("Test User", hr_email.subject)
        self.assertIn("interview", hr_email.body.lower())
        self.assertIn("Schedule an interview", hr_email.body)
        
        # Check candidate email
        self.assertIn("Interview invitation", candidate_email.subject)
        self.assertIn("Test", candidate_email.body)
        self.assertIn("selected for an interview", candidate_email.body)
    
    def test_status_change_to_offer_sends_emails(self):
        """Test that changing status to 'offer' sends appropriate emails"""
        self.application.status = 'offer'
        self.application.save()
        
        # Should send both HR and candidate emails
        self.assertEqual(len(mail.outbox), 2)
        
        # Find emails
        hr_email = next((e for e in mail.outbox if e.to == ['linguify.info@gmail.com']), None)
        candidate_email = next((e for e in mail.outbox if e.to == ['test@example.com']), None)
        
        # Check HR email
        self.assertIn("🎉", hr_email.subject)
        self.assertIn("offer", hr_email.body.lower())
        self.assertIn("Prepare the offer letter", hr_email.body)
        
        # Check candidate email
        self.assertIn("Job offer", candidate_email.subject)
        self.assertIn("offer you the", candidate_email.body)
    
    def test_status_change_to_hired_sends_emails(self):
        """Test that changing status to 'hired' sends appropriate emails"""
        self.application.status = 'hired'
        self.application.save()
        
        # Should send both emails
        self.assertEqual(len(mail.outbox), 2)
        
        # Check for welcome message in candidate email
        candidate_email = next((e for e in mail.outbox if e.to == ['test@example.com']), None)
        self.assertIn("Welcome to", candidate_email.subject)
        self.assertIn("onboarding", candidate_email.body.lower())
    
    def test_status_change_to_rejected_sends_emails(self):
        """Test that changing status to 'rejected' sends appropriate emails"""
        self.application.status = 'rejected'
        self.application.save()
        
        # Should send both emails
        self.assertEqual(len(mail.outbox), 2)
        
        # Check rejection email is polite and encouraging
        candidate_email = next((e for e in mail.outbox if e.to == ['test@example.com']), None)
        self.assertIn("Thank you for your interest", candidate_email.body)
        self.assertIn("encourage you to apply", candidate_email.body)
    
    def test_no_email_on_same_status_save(self):
        """Test that no email is sent if status doesn't change"""
        self.application.status = 'reviewed'
        self.application.save()
        mail.outbox = []  # Clear
        
        # Save again without changing status
        self.application.save()
        
        # No new emails should be sent
        self.assertEqual(len(mail.outbox), 0)
    
    def test_admin_bulk_action_sends_emails(self):
        """Test that admin bulk actions trigger email notifications"""
        # Create another application
        app2 = JobApplication.objects.create(
            position=self.position,
            first_name="Another",
            last_name="Candidate",
            email="another@example.com",
            status='submitted'
        )
        
        # Create request with messages support
        from django.contrib.messages.storage.fallback import FallbackStorage
        request = RequestFactory().get('/')
        request.user = self.admin_user
        # Add message storage to request
        setattr(request, 'session', {})
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        
        # Get admin instance
        admin = JobApplicationAdmin(JobApplication, site)
        
        # Test bulk interview action
        queryset = JobApplication.objects.filter(id__in=[self.application.id, app2.id])
        admin.mark_interview(request, queryset)
        
        # Should send 4 emails (2 HR + 2 candidate)
        self.assertEqual(len(mail.outbox), 4)
        
        # Verify emails were sent to both candidates
        candidate_emails = [e.to[0] for e in mail.outbox if e.to[0] != 'linguify.info@gmail.com']
        self.assertIn('test@example.com', candidate_emails)
        self.assertIn('another@example.com', candidate_emails)
    
    def test_email_contains_correct_template_variables(self):
        """Test that email templates have all variables properly filled"""
        self.application.status = 'interview'
        self.application.save()
        
        candidate_email = next((e for e in mail.outbox if e.to == ['test@example.com']), None)
        
        # Check no template variables remain
        self.assertNotIn('{{', candidate_email.body)
        self.assertNotIn('}}', candidate_email.body)
        self.assertNotIn('{%', candidate_email.body)
        self.assertNotIn('%}', candidate_email.body)
        
        # Check personalization
        self.assertIn('Test', candidate_email.body)  # First name
        self.assertIn('Senior Python Developer', candidate_email.body)  # Position
    
    def test_html_email_structure(self):
        """Test that HTML emails have proper structure"""
        self.application.status = 'offer'
        self.application.save()
        
        # Get candidate email
        candidate_email = next((e for e in mail.outbox if e.to == ['test@example.com']), None)
        
        # Check HTML structure
        self.assertIn('<!DOCTYPE html>', candidate_email.body)
        self.assertIn('<html', candidate_email.body)
        self.assertIn('</html>', candidate_email.body)
        self.assertIn('status-offer', candidate_email.body)  # CSS class
    
    def test_rejected_email_no_status_badge(self):
        """Test that rejected emails don't show the status badge"""
        self.application.status = 'rejected'
        self.application.save()
        
        # Get candidate email
        candidate_email = next((e for e in mail.outbox if e.to == ['test@example.com']), None)
        
        # Check that the status badge HTML element is NOT shown for rejected status
        self.assertNotIn('<span class="status-badge status-rejected">', candidate_email.body)
        self.assertNotIn('Your application status:', candidate_email.body)
        
        # But the thank you message should be there
        self.assertIn('Thank you for your interest', candidate_email.body)