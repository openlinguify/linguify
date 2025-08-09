# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

"""
Security audit logging for authentication events
"""
import logging
from django.utils import timezone
from django.contrib.auth.signals import user_login_failed, user_logged_in, user_logged_out
from django.dispatch import receiver
from django.db.models.signals import post_save
from ..models.models import User, EmailVerificationToken

# Configure security logger
security_logger = logging.getLogger('security.authentication')


class SecurityAuditLogger:
    """Centralized security event logging"""
    
    @staticmethod
    def log_event(event_type, user_identifier, details=None, ip_address=None, user_agent=None, severity='INFO'):
        """Log a security event"""
        log_data = {
            'event_type': event_type,
            'user_identifier': user_identifier,
            'timestamp': timezone.now().isoformat(),
            'ip_address': ip_address,
            'user_agent': user_agent,
            'details': details or {},
            'severity': severity
        }
        
        log_message = f"[{severity}] {event_type} - User: {user_identifier}"
        if ip_address:
            log_message += f" - IP: {ip_address}"
        if details:
            log_message += f" - Details: {details}"
        
        if severity == 'WARNING':
            security_logger.warning(log_message)
        elif severity == 'ERROR':
            security_logger.error(log_message)
        elif severity == 'CRITICAL':
            security_logger.critical(log_message)
        else:
            security_logger.info(log_message)
    
    @classmethod
    def log_registration(cls, user, ip_address=None, user_agent=None):
        """Log user registration"""
        cls.log_event(
            'USER_REGISTRATION',
            user.email,
            {'username': user.username, 'native_language': user.native_language},
            ip_address,
            user_agent
        )
    
    @classmethod
    def log_email_verification_sent(cls, user, token_id, ip_address=None):
        """Log verification email sent"""
        cls.log_event(
            'VERIFICATION_EMAIL_SENT',
            user.email,
            {'token_id': str(token_id)},
            ip_address
        )
    
    @classmethod
    def log_email_verification_attempt(cls, email, token, success, ip_address=None, error_reason=None):
        """Log email verification attempt"""
        severity = 'INFO' if success else 'WARNING'
        details = {'token': token[:10] + '...', 'success': success}
        if error_reason:
            details['error'] = error_reason
        
        cls.log_event(
            'EMAIL_VERIFICATION_ATTEMPT',
            email,
            details,
            ip_address,
            severity=severity
        )
    
    @classmethod
    def log_verification_success(cls, user, ip_address=None):
        """Log successful email verification"""
        cls.log_event(
            'EMAIL_VERIFICATION_SUCCESS',
            user.email,
            {'username': user.username, 'account_activated': True},
            ip_address
        )
    
    @classmethod
    def log_rate_limit_exceeded(cls, identifier, action, ip_address=None):
        """Log rate limit exceeded"""
        cls.log_event(
            'RATE_LIMIT_EXCEEDED',
            identifier,
            {'action': action, 'blocked': True},
            ip_address,
            severity='WARNING'
        )
    
    @classmethod
    def log_account_lockout(cls, identifier, reason, ip_address=None):
        """Log account lockout"""
        cls.log_event(
            'ACCOUNT_LOCKOUT',
            identifier,
            {'reason': reason, 'lockout_applied': True},
            ip_address,
            severity='WARNING'
        )
    
    @classmethod
    def log_suspicious_activity(cls, identifier, activity, ip_address=None, severity='WARNING'):
        """Log suspicious activity"""
        cls.log_event(
            'SUSPICIOUS_ACTIVITY',
            identifier,
            {'activity': activity},
            ip_address,
            severity=severity
        )
    
    @classmethod
    def log_token_cleanup(cls, deleted_count, user_email=None):
        """Log token cleanup operation"""
        cls.log_event(
            'TOKEN_CLEANUP',
            user_email or 'system',
            {'deleted_tokens': deleted_count},
            severity='INFO'
        )


# Django signal receivers for automatic logging
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log successful login"""
    from ..security.rate_limiter import EmailVerificationRateLimiter
    ip_address = EmailVerificationRateLimiter.get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    SecurityAuditLogger.log_event(
        'USER_LOGIN_SUCCESS',
        user.email,
        {'username': user.username},
        ip_address,
        user_agent
    )


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    """Log failed login attempt"""
    from ..security.rate_limiter import EmailVerificationRateLimiter
    ip_address = EmailVerificationRateLimiter.get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    # Don't log the actual credentials for security
    username = credentials.get('username', 'unknown')
    
    SecurityAuditLogger.log_event(
        'USER_LOGIN_FAILED',
        username,
        {'attempt_blocked': False},
        ip_address,
        user_agent,
        severity='WARNING'
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log user logout"""
    if user:
        from ..security.rate_limiter import EmailVerificationRateLimiter
        ip_address = EmailVerificationRateLimiter.get_client_ip(request)
        
        SecurityAuditLogger.log_event(
            'USER_LOGOUT',
            user.email,
            {'username': user.username},
            ip_address
        )


@receiver(post_save, sender=EmailVerificationToken)
def log_token_creation(sender, instance, created, **kwargs):
    """Log token creation"""
    if created:
        SecurityAuditLogger.log_event(
            'VERIFICATION_TOKEN_CREATED',
            instance.user.email,
            {
                'token_id': str(instance.id),
                'expires_at': instance.expires_at.isoformat()
            }
        )