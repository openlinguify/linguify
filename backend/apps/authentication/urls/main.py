# authentication/urls.py
from django.urls import path
from ..views import (
    get_me,
    user_settings,
    user_profile,
    update_profile_picture,
    debug_profile_endpoint,
    delete_account,
    cancel_account_deletion,
    # Cookie consent views
    create_cookie_consent,
    get_cookie_consent,
    revoke_cookie_consent,
    get_cookie_consent_stats,
    get_cookie_consent_logs,
    check_consent_validity,
    debug_cookie_consent,
    # Additional settings endpoints
    export_user_data,
    logout_all_devices,
    # Simple Django views for settings
    update_user_profile,
    update_learning_settings,
    change_user_password,
    # Profile picture management
    manage_profile_picture
)

# Settings views
from ..views import (
    settings_stats
)
from django.conf import settings
from .debug_views import cors_debug, test_token_verification, debug_auth_headers, debug_apps_system, test_token
from ..views_terms import accept_terms, terms_status

urlpatterns = [
    # Django authentication endpoints
    # (Using standard Django auth via frontend_web app)
    
    # Common user endpoints
    path('me/', get_me, name='get_me'),
    path('me/settings/', user_settings, name='user_settings'),
    path('profile/', user_profile, name='user_profile'),
    path('profile-picture/', manage_profile_picture, name='user_profile_picture'),
    path('debug-profile/', debug_profile_endpoint, name='debug_profile'),
    path('delete-account/', delete_account, name='delete_account'),
    path('restore-account/', cancel_account_deletion, name='restore_account'),

    # Terms and conditions endpoints
    path('terms/accept/', accept_terms, name='accept_terms'),
    path('terms/status/', terms_status, name='terms_status'),
    
    # Cookie consent endpoints
    path('cookie-consent/', create_cookie_consent, name='create_cookie_consent'),
    path('cookie-consent/get/', get_cookie_consent, name='get_cookie_consent'),
    path('cookie-consent/revoke/', revoke_cookie_consent, name='revoke_cookie_consent'),
    path('cookie-consent/check/', check_consent_validity, name='check_consent_validity'),
    
    # Admin cookie consent endpoints
    path('cookie-consent/stats/', get_cookie_consent_stats, name='cookie_consent_stats'),
    path('cookie-consent/logs/', get_cookie_consent_logs, name='cookie_consent_logs'),
    path('cookie-consent/debug/', debug_cookie_consent, name='debug_cookie_consent'),
    
    # Settings endpoints (unified Django views)
    path('settings/', update_user_profile, name='update_user_profile'),
    path('settings/learning/', update_learning_settings, name='update_learning_settings'),
    path('settings/password/', change_user_password, name='change_user_password'),
    path('settings/stats/', settings_stats, name='settings_stats'),
    
    # User management endpoints
    path('export-data/', export_user_data, name='export_user_data'),
    path('logout-all/', logout_all_devices, name='logout_all_devices'),
]

if settings.DEBUG:
    urlpatterns += [
        path('test-token/', test_token, name='test_token'),
        path('cors-debug/', cors_debug, name='cors_debug'),
        path('debug/test-token/', test_token_verification, name='test_token_verification'),
        path('debug/auth-headers/', debug_auth_headers, name='debug_auth_headers'),
        path('debug/apps-system/', debug_apps_system, name='debug_apps_system'),
    ]