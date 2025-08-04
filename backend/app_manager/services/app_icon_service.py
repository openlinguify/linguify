"""
Service for handling application icons and static assets.
"""
import os
import logging
from django.apps import apps as django_apps
from django.conf import settings
from django.core.cache import cache
from .manifest_loader import manifest_loader

logger = logging.getLogger(__name__)


class AppIconService:
    """Service for managing application icons and static assets."""
    
    # Icon mapping configuration - should eventually move to settings
    ICON_MAPPING = {
        'Book': 'bi-book',
        'Cards': 'bi-collection', 
        'MessageSquare': 'bi-chat-dots',
        'Brain': 'bi-lightbulb',
        'App': 'bi-app-indicator',
        'Zap': 'bi-lightning-fill',
        'RotateCcw': 'bi-arrow-clockwise',
        'Users': 'bi-people',
        'Settings': 'bi-gear',
        'FileText': 'bi-file-text',
        'Calendar': 'bi-calendar',
        'BarChart': 'bi-bar-chart',
    }
    
    @classmethod
    def get_icon_class(cls, icon_name):
        """
        Get Bootstrap icon class for given icon name.
        
        Args:
            icon_name (str): The icon name from the app
            
        Returns:
            str: Bootstrap icon class
        """
        return cls.ICON_MAPPING.get(icon_name, 'bi-app')
    
    @classmethod
    def get_static_icon_url(cls, app_code):
        """
        Generate static icon URL for an app using manifest data.
        Uses cache for performance.
        
        Args:
            app_code (str): The application code
            
        Returns:
            str or None: URL to static icon or None if not found
        """
        # Check cache first
        cache_key = f"app_icon_url_{app_code}"
        cached_url = cache.get(cache_key)
        if cached_url is not None:
            return cached_url if cached_url != "NOT_FOUND" else None
        
        try:
            # Check if app has static icon according to manifest
            app_info = manifest_loader.get_app_info(app_code)
            if app_info.get('has_static_icon', False):
                url = f"/app-icons/{app_code}/icon.png"
                cache.set(cache_key, url, 3600)  # Cache for 1 hour
                return url
                    
        except Exception as e:
            logger.warning(f"Error getting static icon for app {app_code}: {e}")
        
        # Cache "not found" to avoid repeated file system checks
        cache.set(cache_key, "NOT_FOUND", 3600)
        return None
    
    @classmethod
    def get_color_gradient(cls, color):
        """
        Generate CSS gradient from app color.
        
        Args:
            color (str): Base color for the gradient
            
        Returns:
            str: CSS gradient string
        """
        if not color:
            return 'linear-gradient(135deg, #6366f1 0%, #6366f180 100%)'  # Default
            
        return f'linear-gradient(135deg, {color} 0%, {color}80 100%)'