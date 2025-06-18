# Enhanced authentication middleware for better error handling
import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.http import JsonResponse
import json

logger = logging.getLogger(__name__)
User = get_user_model()

class EnhancedSupabaseAuthMiddleware:
    """Enhanced middleware to handle Supabase authentication with better error reporting"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip authentication for certain paths
        skip_paths = [
            '/admin',
            '/static',
            '/media',
            '/favicon.ico',
            '/robots.txt',
            '/api/docs',
            '/api/schema',
        ]
        
        if any(request.path.startswith(path) for path in skip_paths):
            return self.get_response(request)
        
        # Skip if already authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            return self.get_response(request)
        
        # Development bypass
        if settings.DEBUG and getattr(settings, 'BYPASS_AUTH_FOR_DEVELOPMENT', False):
            try:
                dev_user, created = User.objects.get_or_create(
                    email='dev@example.com',
                    defaults={
                        'username': 'dev_user',
                        'first_name': 'Dev',
                        'last_name': 'User',
                    }
                )
                request.user = dev_user
                if created:
                    logger.info("Created development user")
                logger.debug(f"Using development user: {dev_user.email}")
            except Exception as e:
                logger.error(f"Failed to create dev user: {e}")
                request.user = AnonymousUser()
        else:
            request.user = AnonymousUser()
        
        response = self.get_response(request)
        return response

class AuthenticationErrorMiddleware:
    """Middleware to handle authentication errors gracefully"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_exception(self, request, exception):
        """Handle authentication-related exceptions"""
        from rest_framework.exceptions import AuthenticationFailed
        
        if isinstance(exception, AuthenticationFailed):
            error_detail = str(exception.detail) if hasattr(exception, 'detail') else str(exception)
            
            # Enhanced error messages based on the error type
            if 'expired' in error_detail.lower():
                message = "Votre session a expiré. Veuillez vous reconnecter."
                code = "TOKEN_EXPIRED"
            elif 'signature' in error_detail.lower():
                message = "Token invalide. Veuillez vous reconnecter."
                code = "INVALID_SIGNATURE"
            elif 'audience' in error_detail.lower():
                message = "Configuration d'authentification incorrecte."
                code = "INVALID_AUDIENCE"
            elif 'anon key' in error_detail.lower():
                message = "Clé d'authentification incorrecte utilisée."
                code = "ANON_KEY_USED"
            else:
                message = "Authentification requise. Veuillez vous connecter."
                code = "AUTHENTICATION_REQUIRED"
            
            logger.warning(f"Authentication failed for {request.path}: {error_detail}")
            
            return JsonResponse({
                'detail': message,
                'code': code,
                'debug_info': error_detail if settings.DEBUG else None
            }, status=401)
        
        return None