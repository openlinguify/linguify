# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

from . import auth_views
from . import settings_views

# Export des fonctions nécessaires pour les URLs
from .views import get_me, user_profile, update_profile_picture, debug_profile_endpoint, delete_account, cancel_account_deletion
from .views import create_cookie_consent, get_cookie_consent, revoke_cookie_consent, get_cookie_consent_stats, get_cookie_consent_logs, check_consent_validity, debug_cookie_consent
from .views import export_user_data, logout_all_devices, change_user_password, settings_stats