"""
Cookie consent validation middleware for Linguify
"""
import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.conf import settings
from .models import CookieConsent

logger = logging.getLogger(__name__)


class CookieConsentMiddleware(MiddlewareMixin):
    """
    Middleware to validate cookie consent for protected endpoints
    """
    
    # API endpoints that require specific consent
    CONSENT_REQUIRED_ENDPOINTS = {
        'analytics': [
            '/api/analytics/',
            '/api/stats/',
        ],
        'functionality': [
            '/api/preferences/',
            '/api/settings/',
        ],
        'performance': [
            '/api/cache/',
            '/api/performance/',
        ]
    }
    
    # Endpoints that are always allowed (essential functionality)
    EXEMPT_ENDPOINTS = [
        '/api/auth/',
        '/api/auth/cookie-consent/',
        '/admin/',
        '/api/docs/',
        '/api/schema/',
        '/static/',
        '/media/',
    ]
    
    def __init__(self, get_response):
        super().__init__(get_response)
        self.get_response = get_response
    
    def process_request(self, request):
        """Process incoming request to check consent"""
        
        # Skip consent check in debug mode if configured
        if getattr(settings, 'COOKIE_CONSENT_DEBUG_SKIP', False) and settings.DEBUG:
            return None
        
        # Skip for exempt endpoints
        if self._is_exempt_endpoint(request.path):
            return None
        
        # Check if endpoint requires specific consent
        required_consent = self._get_required_consent(request.path)
        if not required_consent:
            return None
        
        # Get user consent
        consent = self._get_user_consent(request)
        
        # Check if user has required consent
        if not self._has_required_consent(consent, required_consent):
            return self._consent_required_response(required_consent)
        
        return None
    
    def _is_exempt_endpoint(self, path):
        """Check if endpoint is exempt from consent checks"""
        for exempt_path in self.EXEMPT_ENDPOINTS:
            if path.startswith(exempt_path):
                return True
        return False
    
    def _get_required_consent(self, path):
        """Get required consent type for endpoint"""
        for consent_type, endpoints in self.CONSENT_REQUIRED_ENDPOINTS.items():
            for endpoint in endpoints:
                if path.startswith(endpoint):
                    return consent_type
        return None
    
    def _get_user_consent(self, request):
        """Get user's latest consent record"""
        try:
            user = request.user if request.user.is_authenticated else None
            session_id = request.session.session_key
            
            # Get IP address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')
            
            consent = CookieConsent.objects.get_latest_consent(
                user=user,
                session_id=session_id,
                ip_address=ip_address
            )
            
            return consent
            
        except Exception as e:
            logger.warning(f"Error getting user consent: {e}")
            return None
    
    def _has_required_consent(self, consent, required_type):
        """Check if consent includes required type"""
        if not consent or consent.is_revoked or consent.is_expired():
            return False
        
        return getattr(consent, required_type, False)
    
    def _consent_required_response(self, consent_type):
        """Return consent required response"""
        return JsonResponse({
            'error': 'CONSENT_REQUIRED',
            'message': f'This endpoint requires {consent_type} cookie consent',
            'consent_type': consent_type,
            'action_required': 'Please update your cookie preferences to access this feature'
        }, status=403)


class CookieConsentHeaderMiddleware(MiddlewareMixin):
    """
    Middleware to add consent status headers to responses
    """
    
    def __init__(self, get_response):
        super().__init__(get_response)
        self.get_response = get_response
    
    def process_response(self, request, response):
        """Add consent headers to response"""
        try:
            # Skip for non-API requests
            if not request.path.startswith('/api/'):
                return response
            
            # Get user consent
            user = request.user if request.user.is_authenticated else None
            session_id = request.session.session_key
            
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')
            
            consent = CookieConsent.objects.get_latest_consent(
                user=user,
                session_id=session_id,
                ip_address=ip_address
            )
            
            if consent and not consent.is_revoked and not consent.is_expired():
                # Add consent status headers
                response['X-Cookie-Consent-Status'] = 'granted'
                response['X-Cookie-Consent-Version'] = consent.version
                response['X-Cookie-Consent-Analytics'] = 'true' if consent.analytics else 'false'
                response['X-Cookie-Consent-Functionality'] = 'true' if consent.functionality else 'false'
                response['X-Cookie-Consent-Performance'] = 'true' if consent.performance else 'false'
                response['X-Cookie-Consent-Date'] = consent.created_at.isoformat()
            else:
                response['X-Cookie-Consent-Status'] = 'required'
            
        except Exception as e:
            logger.warning(f"Error adding consent headers: {e}")
            response['X-Cookie-Consent-Status'] = 'unknown'
        
        return response


class CookieConsentLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log cookie-related requests for audit purposes
    """
    
    def __init__(self, get_response):
        super().__init__(get_response)
        self.get_response = get_response
    
    def process_request(self, request):
        """Log cookie-related requests"""
        
        # Only log specific cookie-related endpoints
        cookie_endpoints = [
            '/api/auth/cookie-consent/',
            '/api/analytics/',
            '/api/tracking/',
        ]
        
        should_log = any(request.path.startswith(endpoint) for endpoint in cookie_endpoints)
        
        if should_log:
            user_id = request.user.id if request.user.is_authenticated else None
            session_id = request.session.session_key
            
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')
            
            logger.info(
                f"Cookie endpoint access: {request.method} {request.path} "
                f"User: {user_id} Session: {session_id} IP: {ip_address}"
            )
        
        return None


# Utility functions for use in views

def require_cookie_consent(consent_types):
    """
    Decorator to require specific cookie consent types for a view
    
    Usage:
    @require_cookie_consent(['analytics', 'performance'])
    def my_analytics_view(request):
        ...
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            # Get user consent
            user = request.user if request.user.is_authenticated else None
            session_id = request.session.session_key
            
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')
            
            consent = CookieConsent.objects.get_latest_consent(
                user=user,
                session_id=session_id,
                ip_address=ip_address
            )
            
            # Check consent
            if not consent or consent.is_revoked or consent.is_expired():
                return JsonResponse({
                    'error': 'CONSENT_REQUIRED',
                    'message': 'Cookie consent required',
                    'required_types': consent_types
                }, status=403)
            
            # Check specific consent types
            missing_consents = []
            for consent_type in consent_types:
                if not getattr(consent, consent_type, False):
                    missing_consents.append(consent_type)
            
            if missing_consents:
                return JsonResponse({
                    'error': 'CONSENT_REQUIRED',
                    'message': f'Missing consent for: {", ".join(missing_consents)}',
                    'required_types': missing_consents
                }, status=403)
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def get_user_consent_status(request):
    """
    Utility function to get current user consent status
    Returns dict with consent information
    """
    try:
        user = request.user if request.user.is_authenticated else None
        session_id = request.session.session_key
        
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        
        consent = CookieConsent.objects.get_latest_consent(
            user=user,
            session_id=session_id,
            ip_address=ip_address
        )
        
        if consent and not consent.is_revoked and not consent.is_expired():
            return {
                'has_consent': True,
                'consent_id': str(consent.id),
                'version': consent.version,
                'essential': consent.essential,
                'analytics': consent.analytics,
                'functionality': consent.functionality,
                'performance': consent.performance,
                'created_at': consent.created_at.isoformat(),
                'expires_at': consent.expires_at.isoformat() if consent.expires_at else None
            }
        else:
            return {
                'has_consent': False,
                'consent_id': None,
                'version': None,
                'essential': False,
                'analytics': False,
                'functionality': False,
                'performance': False,
                'created_at': None,
                'expires_at': None
            }
            
    except Exception as e:
        logger.error(f"Error getting consent status: {e}")
        return {
            'has_consent': False,
            'error': str(e)
        }