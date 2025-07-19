# Import views for backward compatibility
from .app_manager_views import (
    AppListView, AppStoreView, AppToggleAPI,
    toggle_app, user_enabled_apps, debug_apps
)
from .app_manager_settings_views import UserAppSettingsView

__all__ = [
    'AppListView', 'AppStoreView', 'AppToggleAPI',
    'toggle_app', 'user_enabled_apps', 'debug_apps',
    'UserAppSettingsView'
]