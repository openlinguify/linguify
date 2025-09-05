"""
Custom password reset views to handle HTML emails properly
"""
from django.contrib.auth.views import PasswordResetView as BasePasswordResetView
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


class CustomPasswordResetView(BasePasswordResetView):
    """Custom password reset view that sends HTML emails"""
    
    def send_mail(self, subject_template_name, email_template_name, context,
                  from_email, to_email, html_email_template_name=None):
        """
        Send a django.core.mail.EmailMultiAlternatives to `to_email` with HTML as primary.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        
        # Generate HTML version first if template is provided
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            # Use HTML as the primary content with correct from email
            email_message = EmailMultiAlternatives(subject, '', 'noreply@openlinguify.com', [to_email])
            email_message.attach_alternative(html_email, 'text/html')
            
            # Set additional headers to force HTML rendering and correct sender
            email_message.mixed_subtype = 'related'
            email_message.extra_headers['X-Priority'] = '1'
            email_message.extra_headers['X-MSMail-Priority'] = 'High'
            email_message.extra_headers['Content-Type'] = 'text/html; charset=utf-8'
            email_message.extra_headers['Reply-To'] = 'noreply@openlinguify.com'
        else:
            # Fallback to plain text
            body = loader.render_to_string(email_template_name, context)
            email_message = EmailMultiAlternatives(subject, body, 'noreply@openlinguify.com', [to_email])
        
        email_message.send()
    
    def form_valid(self, form):
        """
        Override to use HTML email template with proper domain
        """
        # Create a mock request with the functional domain
        class MockRequest:
            def is_secure(self):
                return True
            def get_host(self):
                return 'linguify-h47a.onrender.com'
            META = {
                'SERVER_NAME': 'linguify-h47a.onrender.com',
                'SERVER_PORT': '443'
            }
        
        mock_request = MockRequest()
        
        opts = {
            'use_https': True,  # Always use HTTPS for production URLs
            'token_generator': self.token_generator,
            'from_email': self.from_email,
            'email_template_name': 'authentication/password_reset/password_reset_email.txt',  # Plain text
            'subject_template_name': self.subject_template_name,
            'request': mock_request,  # Use mock request with correct domain
            'html_email_template_name': 'authentication/password_reset/password_reset_email.html',  # HTML
            'extra_email_context': self.extra_email_context,
        }
        form.save(**opts)
        return super().form_valid(form)