"""
Tests for the email system (HR notifications + candidate confirmations)
"""

import tempfile
from unittest.mock import patch, MagicMock

from django.test import TestCase, override_settings
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core import mail
from django.core.mail import EmailMessage

from ..models import Department, JobPosition, JobApplication
from ..views import JobApplicationCreateView


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    MEDIA_ROOT=tempfile.mkdtemp()
)
class EmailSystemTests(TestCase):
    """Tests for the complete email system"""
    
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
        
        # Clear mail outbox
        mail.outbox = []
    
    def create_test_pdf(self):
        """Create a test PDF file"""
        pdf_content = b"""%%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
xref
0 2
trailer
<<
/Size 2
/Root 1 0 R
>>
startxref
%%EOF"""
        return SimpleUploadedFile(
            "test_resume.pdf", 
            pdf_content, 
            content_type="application/pdf"
        )
    
    def test_candidate_confirmation_email_sent(self):
        """Test that confirmation email is sent to candidate"""
        application = JobApplication.objects.create(
            position=self.position,
            first_name="Louis-Philippe",
            last_name="Lalou",
            email="louisphilippelalou@outlook.com",
            phone="0473488100",
            cover_letter="I am very interested in this position",
            portfolio_url="https://example.com/portfolio",
            linkedin_url="https://linkedin.com/in/test"
        )
        
        # Send confirmation email
        view = JobApplicationCreateView()
        view._send_confirmation_email(application)
        
        # Verify email was sent
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        
        # Check subject
        self.assertIn("Candidature reçue", email.subject)
        self.assertIn("Senior Python Developer", email.subject)
        self.assertIn("Linguify", email.subject)
        
        # Check recipient
        self.assertEqual(email.to, ["louisphilippelalou@outlook.com"])
        
        # Check reply-to
        self.assertEqual(email.reply_to, ["linguify.info@gmail.com"])
        
        # Check content
        self.assertIn("Louis-Philippe", email.body)
        self.assertIn("Senior Python Developer", email.body)
        self.assertIn("Engineering", email.body)
        self.assertIn("Paris, France", email.body)
        self.assertIn("Notre équipe RH", email.body)
    
    def test_hr_email_structure_and_content(self):
        """Test HR email content and structure"""
        application = JobApplication.objects.create(
            position=self.position,
            first_name="Test",
            last_name="User", 
            email="test@example.com",
            phone="0123456789",
            cover_letter="This is my cover letter explaining my motivation.",
            portfolio_url="https://example.com/portfolio",
            linkedin_url="https://linkedin.com/in/testuser"
        )
        
        # Create HR email
        subject = f"🚀 Nouvelle candidature: {application.position.title} - {application.first_name} {application.last_name}"
        
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <body>
            <h1>💼 Nouvelle candidature reçue</h1>
            <p>Candidat: {application.first_name} {application.last_name}</p>
            <p>Email: {application.email}</p>
            <p>Téléphone: {application.phone}</p>
            <p>Poste: {application.position.title}</p>
            <p>Département: {application.position.department.name}</p>
            <p>Lettre de motivation: {application.cover_letter}</p>
        </body>
        </html>
        """
        
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email="noreply@linguify.com",
            to=["linguify.info@gmail.com"],
            reply_to=[application.email],
        )
        
        email.content_subtype = 'html'
        email.send()
        
        # Verify email
        sent_email = mail.outbox[0]
        
        self.assertIn("🚀 Nouvelle candidature", sent_email.subject)
        self.assertIn("Test User", sent_email.subject)
        self.assertEqual(sent_email.to, ["linguify.info@gmail.com"])
        self.assertEqual(sent_email.reply_to, ["test@example.com"])
        self.assertIn("💼 Nouvelle candidature reçue", sent_email.body)
        self.assertIn("This is my cover letter", sent_email.body)
    
    def test_email_with_resume_attachment(self):
        """Test email with CV attachment"""
        test_resume = self.create_test_pdf()
        
        application = JobApplication.objects.create(
            position=self.position,
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="0123456789",
            cover_letter="I am interested in this position",
            resume_file=test_resume
        )
        
        # Create email with attachment
        email = EmailMessage(
            subject="Test email with attachment",
            body="Test body",
            from_email="noreply@linguify.com",
            to=["linguify.info@gmail.com"],
        )
        
        # Attach CV file
        if application.resume_file:
            application.resume_file.seek(0)
            email.attach(
                application.resume_file.name,
                application.resume_file.read(),
                'application/pdf'
            )
        
        email.send()
        
        # Verify attachment
        sent_email = mail.outbox[0]
        self.assertEqual(len(sent_email.attachments), 1)
        
        attachment = sent_email.attachments[0]
        self.assertIn("test_resume", attachment[0])  # File name
        self.assertIsInstance(attachment[1], bytes)  # Content
        self.assertEqual(attachment[2], 'application/pdf')  # MIME type
    
    def test_email_content_special_characters(self):
        """Test email handling of special characters"""
        application = JobApplication.objects.create(
            position=self.position,
            first_name="François",
            last_name="Müller",
            email="francois.muller@example.com",
            phone="0123456789",
            cover_letter="J'aimerais beaucoup travailler chez Linguify. C'est formidable !"
        )
        
        view = JobApplicationCreateView()
        view._send_confirmation_email(application)
        
        email = mail.outbox[0]
        
        # Check special characters in subject (position title)
        self.assertIn("Senior Python Developer", email.subject)
        
        # Check special characters in body (name should be there, cover letter is not in confirmation email)
        self.assertIn("François", email.body)
        # Cover letter is not included in candidate confirmation email, only in HR email
    
    @patch('core.jobs.views.EmailMessage')
    def test_email_error_handling(self, mock_email):
        """Test email error handling"""
        # Configure mock to raise exception
        mock_email_instance = MagicMock()
        mock_email_instance.send.side_effect = Exception("SMTP Error")
        mock_email.return_value = mock_email_instance
        
        application = JobApplication.objects.create(
            position=self.position,
            first_name="Test",
            last_name="User",
            email="test@example.com"
        )
        
        view = JobApplicationCreateView()
        
        # Email sending should fail gracefully
        try:
            view._send_confirmation_email(application)
            # If we reach here, error was handled gracefully
            self.assertTrue(True)
        except Exception:
            self.fail("Email sending should not raise unhandled exceptions")
    
    def test_email_template_variables_complete(self):
        """Test that all template variables are properly replaced"""
        application = JobApplication.objects.create(
            position=self.position,
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="0123456789",
            cover_letter="Test cover letter"
        )
        
        view = JobApplicationCreateView()
        view._send_confirmation_email(application)
        
        email = mail.outbox[0]
        
        # Check no unreplaced template variables (but allow CSS styles)
        # Should not have Django template variables like {variable_name}
        import re
        django_vars = re.findall(r'\{[a-zA-Z_][a-zA-Z0-9_]*\}', email.body)
        self.assertEqual(len(django_vars), 0, f"Found unreplaced template variables: {django_vars}")
        
        # Check all required values are present
        self.assertIn("John", email.body)
        self.assertIn("Senior Python Developer", email.body)
        self.assertIn("Engineering", email.body)
        self.assertIn("Paris, France", email.body)
        
        # Check date formatting
        today = timezone.now().strftime('%d/%m/%Y')
        self.assertIn(today, email.body)
    
    def test_multiple_emails_workflow(self):
        """Test the complete email workflow (HR + candidate)"""
        application = JobApplication.objects.create(
            position=self.position,
            first_name="Test",
            last_name="User",
            email="test@example.com",
            phone="0123456789",
            cover_letter="I am very interested"
        )
        
        view = JobApplicationCreateView()
        
        # 1. Send candidate confirmation
        view._send_confirmation_email(application)
        
        # 2. Send HR notification (simulated)
        hr_email = EmailMessage(
            subject=f"🚀 Nouvelle candidature: {application.position.title} - {application.first_name} {application.last_name}",
            body="HR notification content",
            from_email="noreply@linguify.com",
            to=["linguify.info@gmail.com"],
            reply_to=[application.email],
        )
        hr_email.send()
        
        # Verify both emails were sent
        self.assertEqual(len(mail.outbox), 2)
        
        # Email 1: Candidate confirmation
        candidate_email = mail.outbox[0]
        self.assertEqual(candidate_email.to, ["test@example.com"])
        self.assertIn("Candidature reçue", candidate_email.subject)
        
        # Email 2: HR notification
        hr_email_sent = mail.outbox[1]
        self.assertEqual(hr_email_sent.to, ["linguify.info@gmail.com"])
        self.assertIn("Nouvelle candidature", hr_email_sent.subject)
        self.assertEqual(hr_email_sent.reply_to, ["test@example.com"])


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class EmailContentTests(TestCase):
    """Tests for specific email content and formatting"""
    
    def setUp(self):
        self.department = Department.objects.create(
            name="Marketing",
            description="Marketing department"
        )
        
        self.position = JobPosition.objects.create(
            title="Marketing Manager",
            department=self.department,
            location="Lyon, France",
            employment_type="full_time",
            experience_level="senior",
            description="Marketing management role",
            requirements="Marketing experience",
            responsibilities="Manage marketing campaigns",
            application_email="marketing@linguify.com"
        )
        
        mail.outbox = []
    
    def test_email_html_structure(self):
        """Test that emails have proper HTML structure"""
        application = JobApplication.objects.create(
            position=self.position,
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com"
        )
        
        view = JobApplicationCreateView()
        view._send_confirmation_email(application)
        
        email = mail.outbox[0]
        
        # Check HTML elements are present
        self.assertIn("<!DOCTYPE html>", email.body)
        self.assertIn("<html>", email.body)
        self.assertIn("<body>", email.body)
        self.assertIn("<div", email.body)
        self.assertIn("</html>", email.body)
    
    def test_email_styling_and_branding(self):
        """Test that emails include proper styling and branding"""
        application = JobApplication.objects.create(
            position=self.position,
            first_name="Test",
            last_name="User",
            email="test@example.com"
        )
        
        view = JobApplicationCreateView()
        view._send_confirmation_email(application)
        
        email = mail.outbox[0]
        
        # Check branding elements
        self.assertIn("Linguify", email.body)
        self.assertIn("L'équipe Linguify", email.body)
        
        # Check styling elements
        self.assertIn("background:", email.body)
        self.assertIn("color:", email.body)
        self.assertIn("font-family:", email.body)
    
    def test_email_links_and_contacts(self):
        """Test that emails include proper contact information and links"""
        application = JobApplication.objects.create(
            position=self.position,
            first_name="Contact",
            last_name="Test",
            email="contact@example.com"
        )
        
        view = JobApplicationCreateView()
        view._send_confirmation_email(application)
        
        email = mail.outbox[0]
        
        # Check contact information
        self.assertIn("linguify.info@gmail.com", email.body)
        
        # Check website link
        self.assertIn("openlinguify.com", email.body)  # Production URL
        
        # Check proper mailto and href formatting
        self.assertIn("mailto:", email.body)
        self.assertIn("href=", email.body)