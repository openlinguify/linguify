"""
Views package for saas_web app.
Modular views separated by responsibility.
"""

# Import all views to maintain backward compatibility
from .dashboard import DashboardView
from .api import UserStatsAPI, NotificationAPI
from .admin import AdminFixAppsView
from .utils import check_username_availability, save_draft_settings, load_draft_settings

# Maintain backward compatibility for existing imports
__all__ = [
    'DashboardView',
    'UserStatsAPI',
    'NotificationAPI', 
    'AdminFixAppsView',
    'check_username_availability',
    'save_draft_settings',
    'load_draft_settings',
]