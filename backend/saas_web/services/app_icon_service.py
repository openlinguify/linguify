"""
Service for handling application icons and static assets.
"""
import os
import logging
from django.apps import apps as django_apps
from django.conf import settings

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
        Generate static icon URL for an app if the icon file exists.
        
        Args:
            app_code (str): The application code
            
        Returns:
            str or None: URL to static icon or None if not found
        """
        try:
            # Find the corresponding Django app
            for app_config in django_apps.get_app_configs():
                if app_config.name.endswith(app_code) or app_config.label == app_code:
                    # Check if icon.png exists in static/description/
                    icon_path = os.path.join(
                        app_config.path, 
                        'static', 
                        'description', 
                        'icon.png'
                    )
                    
                    if os.path.exists(icon_path):
                        # Return URL to the app-icons system
                        return f"/app-icons/{app_code}/icon.png"
                    break
                    
        except Exception as e:
            logger.warning(f"Error getting static icon for app {app_code}: {e}")
            
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