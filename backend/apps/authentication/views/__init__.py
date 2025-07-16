# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

from . import auth_views
from . import profile_views  
from . import settings_views
from . import password_views

# Export des fonctions nécessaires pour les URLs
from .profile_views import get_me, user_settings, user_profile, update_profile_picture, debug_profile_endpoint, delete_account, cancel_account_deletion
from .profile_views import create_cookie_consent, get_cookie_consent, revoke_cookie_consent, get_cookie_consent_stats, get_cookie_consent_logs, check_consent_validity, debug_cookie_consent
from .settings_views import export_user_data, logout_all_devices, update_user_profile, update_learning_settings, change_user_password, manage_profile_picture, settings_stats