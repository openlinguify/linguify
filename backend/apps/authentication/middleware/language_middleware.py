# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

from django.utils import translation
from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)


class UserLanguageMiddleware(MiddlewareMixin):
    """
    Middleware to set the language based on user's interface_language preference
    """

    def process_request(self, request):
        """
        Set the language for the request based on user preferences
        """
        if request.user.is_authenticated:
            try:
                # Get user's interface language preference
                from ..models.models import UserProfile
                profile = UserProfile.objects.filter(user=request.user).first()

                if profile and profile.interface_language:
                    # Activate the user's preferred language
                    translation.activate(profile.interface_language)
                    request.session[translation.LANGUAGE_SESSION_KEY] = profile.interface_language
                    logger.debug(f"Language set to {profile.interface_language} for user {request.user.username}")
                else:
                    # Default to English if no preference is set
                    translation.activate('en')
                    request.session[translation.LANGUAGE_SESSION_KEY] = 'en'
            except Exception as e:
                logger.error(f"Error setting user language: {e}")
                # Fall back to default language
                translation.activate('en')
        else:
            # For anonymous users, check session or use default
            language = request.session.get(translation.LANGUAGE_SESSION_KEY, 'en')
            translation.activate(language)

        return None