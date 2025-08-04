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
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        
        # Generate plain text version
        body = loader.render_to_string(email_template_name, context)
        
        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        
        # Add HTML version if template is provided
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')
        
        email_message.send()
    
    def form_valid(self, form):
        """
        Override to use HTML email template
        """
        opts = {
            'use_https': self.request.is_secure(),
            'token_generator': self.token_generator,
            'from_email': self.from_email,
            'email_template_name': 'authentication/password_reset/password_reset_email.txt',  # Plain text
            'subject_template_name': self.subject_template_name,
            'request': self.request,
            'html_email_template_name': 'authentication/password_reset/password_reset_email.html',  # HTML
            'extra_email_context': self.extra_email_context,
        }
        form.save(**opts)
        return super().form_valid(form)