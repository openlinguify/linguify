# Middleware to check terms acceptance on each request
import logging
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
from apps.notification.services import send_terms_acceptance_email_and_notification
from apps.notification.models import Notification

logger = logging.getLogger(__name__)
User = get_user_model()

class TermsAcceptanceMiddleware:
    """
    Middleware to check if user has accepted terms and conditions.
    Sends notification if terms are not accepted (maximum once per day).
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Process the request
        response = self.get_response(request)
        
        # Check terms only for authenticated users
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Skip for certain paths to avoid loops
            skip_paths = [
                '/admin',
                '/api/auth/terms',
                '/api/notifications',
                '/static',
                '/media',
                '/auth/logout',
                '/robots.txt',
                '/sitemap.xml',
                '/manifest.json',
            ]
            
            if any(request.path.startswith(path) for path in skip_paths):
                return response
            
            # Only check on main dashboard requests to avoid spam
            if request.path not in ['/dashboard/', '/']:
                return response
            
            try:
                # Check if user has accepted terms
                if not request.user.terms_accepted:
                    # Check if we already sent a notification today
                    today = timezone.now().date()
                    daily_cache_key = f"terms_notification_sent_{request.user.id}_{today}"
                    
                    if cache.get(daily_cache_key):
                        # Already sent today, skip
                        response['X-Terms-Required'] = 'true'
                        return response
                    
                    # Check if there's already an unread terms notification
                    existing_notification = Notification.objects.filter(
                        user=request.user,
                        type='terms',
                        is_read=False,
                        created_at__gte=timezone.now() - timedelta(days=1)  # Within last 24h
                    ).exists()
                    
                    if existing_notification:
                        # Already have an unread notification, don't send another
                        logger.info(f"User {request.user.email} already has an unread terms notification")
                        response['X-Terms-Required'] = 'true'
                        return response
                    
                    logger.info(f"User {request.user.email} has not accepted terms, sending daily notification")
                    
                    # Send notification and email (max once per day)
                    try:
                        success = send_terms_acceptance_email_and_notification(request.user)
                        if success:
                            # Cache for 24 hours to prevent multiple sends per day
                            cache.set(daily_cache_key, True, 86400)  # 24 hours
                            logger.info(f"Terms notification sent successfully to {request.user.email}")
                        else:
                            logger.warning(f"Failed to send terms notification to {request.user.email}")
                    except Exception as e:
                        logger.error(f"Error sending terms notification to {request.user.email}: {e}")
                    
                    # Add header to response to indicate terms required
                    response['X-Terms-Required'] = 'true'
                
            except Exception as e:
                logger.error(f"Error checking terms acceptance for user {request.user.id}: {e}")
        
        return response