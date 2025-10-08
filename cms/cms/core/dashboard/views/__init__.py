"""
Views package for saas_web app (CMS version).
Simplified for CMS - only core views.
"""

# Import core views for CMS
from .dashboard import DashboardView
from .api import UserStatsAPI, NotificationAPI
# from .admin import AdminFixAppsView  # Not needed for CMS
# from .utils import check_username_availability, save_draft_settings, load_draft_settings  # Not needed for CMS

# Maintain backward compatibility for existing imports
__all__ = [
    'DashboardView',
    'UserStatsAPI',
    'NotificationAPI',
]