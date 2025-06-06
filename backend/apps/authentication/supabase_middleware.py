# Supabase authentication middleware
import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger(__name__)
User = get_user_model()

class SupabaseAuthMiddleware:
    """Middleware to handle Supabase authentication for all requests"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip if already authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            return self.get_response(request)
        
        # In development with bypass enabled, create a dev user
        if settings.DEBUG and getattr(settings, 'BYPASS_AUTH_FOR_DEVELOPMENT', False):
            try:
                # Get or create a development user
                dev_user, created = User.objects.get_or_create(
                    email='dev@example.com',
                    defaults={
                        'username': 'dev_user',
                        'first_name': 'Dev',
                        'last_name': 'User',
                    }
                )
                request.user = dev_user
                logger.debug(f"Using development user: {dev_user.email}")
            except Exception as e:
                logger.error(f"Failed to create dev user: {e}")
                request.user = AnonymousUser()
        else:
            # Let DRF authentication handle it
            request.user = AnonymousUser()
        
        return self.get_response(request)