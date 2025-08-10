# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

"""
Rate limiting utilities for email verification security
"""
import time
import logging
from django.core.cache import cache
from django.http import HttpResponse
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)


class EmailVerificationRateLimiter:
    """Rate limiter for email verification attempts"""
    
    # Rate limiting configuration (ajusté pour être plus convivial)
    MAX_VERIFICATION_ATTEMPTS = 10  # Max attempts per time window (plus généreux)
    VERIFICATION_WINDOW = 3600  # 1 hour in seconds (fenêtre plus longue)
    MAX_RESEND_ATTEMPTS = 5  # Max email resends per time window
    RESEND_WINDOW = 1800  # 30 minutes in seconds
    LOCKOUT_DURATION = 900  # 15 minutes lockout (réduit de 30 à 15 min)
    
    @staticmethod
    def get_cache_key(identifier, action):
        """Generate cache key for rate limiting"""
        return f"auth_rate_limit:{action}:{identifier}"
    
    @staticmethod
    def get_lockout_key(identifier):
        """Generate cache key for account lockouts"""
        return f"auth_lockout:{identifier}"
    
    @classmethod
    def is_locked_out(cls, email_or_ip):
        """Check if an email/IP is locked out"""
        lockout_key = cls.get_lockout_key(email_or_ip)
        return cache.get(lockout_key) is not None
    
    @classmethod
    def apply_lockout(cls, email_or_ip, reason="too_many_attempts"):
        """Apply lockout to an email/IP"""
        lockout_key = cls.get_lockout_key(email_or_ip)
        cache.set(lockout_key, {
            'reason': reason,
            'locked_at': time.time(),
            'expires_in': cls.LOCKOUT_DURATION
        }, cls.LOCKOUT_DURATION)
        
        logger.warning(f"Account lockout applied: {email_or_ip}, reason: {reason}")
    
    @classmethod
    def check_verification_attempts(cls, email, ip_address=None):
        """
        Check if verification attempts are within limits
        Returns: (allowed, remaining_attempts, time_until_reset)
        """
        if cls.is_locked_out(email):
            return False, 0, cls.LOCKOUT_DURATION
        
        if ip_address and cls.is_locked_out(ip_address):
            return False, 0, cls.LOCKOUT_DURATION
        
        email_key = cls.get_cache_key(email, "verification")
        
        # Get current attempt count
        attempts_data = cache.get(email_key, {'count': 0, 'first_attempt': time.time()})
        
        # Check if we're in a new time window
        current_time = time.time()
        if current_time - attempts_data['first_attempt'] > cls.VERIFICATION_WINDOW:
            # Reset counter for new window
            attempts_data = {'count': 0, 'first_attempt': current_time}
        
        # Check if limit exceeded
        if attempts_data['count'] >= cls.MAX_VERIFICATION_ATTEMPTS:
            # Apply lockout after too many attempts
            cls.apply_lockout(email, "verification_attempts_exceeded")
            if ip_address:
                cls.apply_lockout(ip_address, "verification_attempts_exceeded")
            return False, 0, cls.LOCKOUT_DURATION
        
        # Calculate remaining attempts and time
        remaining = cls.MAX_VERIFICATION_ATTEMPTS - attempts_data['count']
        time_until_reset = max(0, cls.VERIFICATION_WINDOW - (current_time - attempts_data['first_attempt']))
        
        return True, remaining, time_until_reset
    
    @classmethod
    def record_verification_attempt(cls, email, success=False):
        """Record a verification attempt"""
        email_key = cls.get_cache_key(email, "verification")
        
        # Get current data
        attempts_data = cache.get(email_key, {'count': 0, 'first_attempt': time.time()})
        
        if success:
            # Clear attempts on success
            cache.delete(email_key)
            logger.info(f"Successful email verification for {email}")
        else:
            # Increment failure counter
            current_time = time.time()
            if current_time - attempts_data['first_attempt'] > cls.VERIFICATION_WINDOW:
                # Start new window
                attempts_data = {'count': 1, 'first_attempt': current_time}
            else:
                # Increment in current window
                attempts_data['count'] += 1
            
            cache.set(email_key, attempts_data, cls.VERIFICATION_WINDOW)
            logger.warning(f"Failed email verification attempt for {email}, attempt {attempts_data['count']}")
    
    @classmethod
    def check_resend_attempts(cls, email, ip_address=None):
        """
        Check if email resend attempts are within limits
        Returns: (allowed, remaining_attempts, time_until_reset)
        """
        if cls.is_locked_out(email):
            return False, 0, cls.LOCKOUT_DURATION
        
        if ip_address and cls.is_locked_out(ip_address):
            return False, 0, cls.LOCKOUT_DURATION
        
        email_key = cls.get_cache_key(email, "resend")
        
        # Get current attempt count
        attempts_data = cache.get(email_key, {'count': 0, 'first_attempt': time.time()})
        
        # Check if we're in a new time window
        current_time = time.time()
        if current_time - attempts_data['first_attempt'] > cls.RESEND_WINDOW:
            # Reset counter for new window
            attempts_data = {'count': 0, 'first_attempt': current_time}
        
        # Check if limit exceeded
        if attempts_data['count'] >= cls.MAX_RESEND_ATTEMPTS:
            cls.apply_lockout(email, "resend_attempts_exceeded")
            if ip_address:
                cls.apply_lockout(ip_address, "resend_attempts_exceeded")
            return False, 0, cls.LOCKOUT_DURATION
        
        # Calculate remaining attempts and time
        remaining = cls.MAX_RESEND_ATTEMPTS - attempts_data['count']
        time_until_reset = max(0, cls.RESEND_WINDOW - (current_time - attempts_data['first_attempt']))
        
        return True, remaining, time_until_reset
    
    @classmethod
    def record_resend_attempt(cls, email):
        """Record an email resend attempt"""
        email_key = cls.get_cache_key(email, "resend")
        
        # Get current data
        attempts_data = cache.get(email_key, {'count': 0, 'first_attempt': time.time()})
        
        # Increment counter
        current_time = time.time()
        if current_time - attempts_data['first_attempt'] > cls.RESEND_WINDOW:
            # Start new window
            attempts_data = {'count': 1, 'first_attempt': current_time}
        else:
            # Increment in current window
            attempts_data['count'] += 1
        
        cache.set(email_key, attempts_data, cls.RESEND_WINDOW)
        logger.info(f"Email resend attempt recorded for {email}, attempt {attempts_data['count']}")
    
    @classmethod
    def get_client_ip(cls, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')


def rate_limit_response(message, status_code=429):
    """Return a user-friendly rate limit response"""
    friendly_html = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>Trop de tentatives - Linguify</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f7fafc; margin: 0; padding: 40px; }}
            .container {{ max-width: 500px; margin: 0 auto; background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 30px rgba(45, 91, 186, 0.1); text-align: center; }}
            .icon {{ font-size: 48px; margin-bottom: 20px; }}
            h1 {{ color: #2D5BBA; margin-bottom: 15px; font-size: 24px; }}
            p {{ color: #718096; line-height: 1.6; margin-bottom: 20px; }}
            .btn {{ display: inline-block; background: linear-gradient(135deg, #2D5BBA 0%, #00D4AA 100%); color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: 600; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="icon">⏰</div>
            <h1>Un petit moment s'il vous plaît</h1>
            <p>{message}</p>
            <a href="javascript:history.back()" class="btn">← Retour</a>
        </div>
    </body>
    </html>
    """
    return HttpResponse(friendly_html, status=status_code, content_type='text/html')