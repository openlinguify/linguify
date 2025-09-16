# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

from django.utils import translation
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
import logging

LANGUAGE_SESSION_KEY = settings.LANGUAGE_COOKIE_NAME

logger = logging.getLogger(__name__)


class UserLanguageMiddleware(MiddlewareMixin):
    """
    Middleware to set the language based on user's interface_language preference
    """

    def process_request(self, request):
        """
        Set the language for the request based on user preferences
        """
        # First check if user is authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            try:
                # Get user's interface language preference directly from User model
                user = request.user

                if hasattr(user, 'interface_language') and user.interface_language:
                    # Activate the user's preferred language
                    language = user.interface_language
                    translation.activate(language)
                    request.session[LANGUAGE_SESSION_KEY] = language
                    request.LANGUAGE_CODE = language
                    logger.info(f"Language activated: {language} for user {user.username}")
                else:
                    # Default to session or English if no preference is set
                    language = request.session.get(LANGUAGE_SESSION_KEY, 'en')
                    translation.activate(language)
                    request.LANGUAGE_CODE = language
                    logger.info(f"Using default language: {language}")
            except Exception as e:
                logger.error(f"Error setting user language: {e}", exc_info=True)
                # Fall back to default language
                translation.activate('en')
                request.LANGUAGE_CODE = 'en'
        else:
            # For anonymous users, detect language from multiple sources
            language = None

            # 1. Check URL parameter (from portal links)
            if 'lang' in request.GET:
                lang_param = request.GET.get('lang')
                if lang_param in ['en', 'fr', 'es', 'nl']:
                    language = lang_param
                    logger.info(f"Language from URL parameter: {language}")

            # 2. Check session
            if not language:
                language = request.session.get(LANGUAGE_SESSION_KEY)
                if language:
                    logger.info(f"Language from session: {language}")

            # 3. Check Accept-Language header
            if not language:
                accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
                if 'fr' in accept_language:
                    language = 'fr'
                elif 'es' in accept_language:
                    language = 'es'
                elif 'nl' in accept_language:
                    language = 'nl'
                else:
                    language = 'en'
                logger.info(f"Language from Accept-Language header: {language}")

            # 4. Default fallback
            if not language:
                language = 'en'
                logger.info(f"Using default language: {language}")

            # Apply the detected language
            translation.activate(language)
            request.session[LANGUAGE_SESSION_KEY] = language
            request.LANGUAGE_CODE = language
            logger.info(f"Anonymous user - final language: {language}")

        return None