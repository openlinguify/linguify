# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

"""
Email verification service for user registration
"""
import logging
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.translation import gettext as _
from django.urls import reverse
from ..models.models import EmailVerificationToken

logger = logging.getLogger(__name__)


class EmailVerificationService:
    """Service for handling email verification"""
    
    @staticmethod
    def create_verification_token(user):
        """Create a new verification token for a user"""
        from django.utils import timezone
        
        # Security: Limit total tokens per user to prevent abuse
        MAX_TOKENS_PER_USER = 10
        user_tokens = EmailVerificationToken.objects.filter(user=user)
        
        if user_tokens.count() >= MAX_TOKENS_PER_USER:
            # Delete oldest tokens to stay under limit
            oldest_tokens = user_tokens.order_by('created_at')[:-MAX_TOKENS_PER_USER+1]
            for token in oldest_tokens:
                token.delete()
            logger.warning(f"Token limit reached for user {user.email}, cleaned up old tokens")
        
        # Invalidate any existing unused tokens for this user
        EmailVerificationToken.objects.filter(user=user, is_used=False).update(is_used=True)
        
        # Create new token
        token = EmailVerificationToken.objects.create(user=user)
        logger.info(f"New verification token created for user {user.email}")
        return token
    
    @staticmethod
    def send_verification_email(user, token, request=None):
        """Send verification email to user"""
        try:
            # Build verification URL
            verification_url = EmailVerificationService._build_verification_url(token.token, request)
            
            # Prepare email context
            context = {
                'user': user,
                'verification_url': verification_url,
                'token': token.token,
                'site_name': 'Linguify',
                'expires_hours': 24,
            }
            
            # Render email templates
            subject = _('Confirm your email address - Linguify')
            html_message = render_to_string('authentication/emails/email_verification.html', context)
            plain_message = render_to_string('authentication/emails/email_verification.txt', context)
            
            # Send email
            success = send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False
            )
            
            if success:
                logger.info(f"Verification email sent successfully to {user.email}")
                return True
            else:
                logger.error(f"Failed to send verification email to {user.email}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending verification email to {user.email}: {str(e)}")
            return False
    
    @staticmethod
    def _build_verification_url(token, request=None):
        """Build the verification URL"""
        verification_path = reverse('auth:verify_email', kwargs={'token': token})
        
        if request:
            # Use request to build absolute URL
            return request.build_absolute_uri(verification_path)
        else:
            # Fallback to settings-based URL
            base_url = getattr(settings, 'BASE_URL', 'http://localhost:8081')
            return f"{base_url}{verification_path}"
    
    @staticmethod
    def verify_token(token_string):
        """Verify a token and activate user if valid"""
        try:
            token = EmailVerificationToken.objects.get(token=token_string)
            
            if not token.is_valid():
                if token.is_expired():
                    return {'success': False, 'error': 'token_expired'}
                else:
                    return {'success': False, 'error': 'token_used'}
            
            # Activate user
            user = token.user
            user.is_active = True
            user.save()
            
            # Mark token as used
            token.use_token()
            
            logger.info(f"User {user.email} successfully verified their email")
            return {'success': True, 'user': user}
            
        except EmailVerificationToken.DoesNotExist:
            return {'success': False, 'error': 'invalid_token'}
        except Exception as e:
            logger.error(f"Error verifying token {token_string}: {str(e)}")
            return {'success': False, 'error': 'verification_error'}
    
    @staticmethod
    def resend_verification_email(user, request=None):
        """Resend verification email for a user"""
        if user.is_active:
            return {'success': False, 'error': 'already_verified'}
        
        # Create new token and send email
        token = EmailVerificationService.create_verification_token(user)
        success = EmailVerificationService.send_verification_email(user, token, request)
        
        if success:
            return {'success': True, 'message': 'email_sent'}
        else:
            return {'success': False, 'error': 'send_failed'}