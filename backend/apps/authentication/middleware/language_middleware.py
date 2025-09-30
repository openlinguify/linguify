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
                else:
                    # Default to session or English if no preference is set
                    language = request.session.get(LANGUAGE_SESSION_KEY, 'en')
                    translation.activate(language)
                    request.LANGUAGE_CODE = language
            except Exception as e:
                logger.error(f"Error setting user language: {e}", exc_info=True)
                # Fall back to default language
                translation.activate('en')
                request.LANGUAGE_CODE = 'en'
        else:
            # For anonymous users, check if LocaleMiddleware already set the language from URL
            current_language = getattr(request, 'LANGUAGE_CODE', None) or translation.get_language()

            # If URL contains a language prefix (handled by LocaleMiddleware), respect it
            url_has_language_prefix = any(request.path.startswith(f'/{lang}/') for lang, _ in settings.LANGUAGES)

            if url_has_language_prefix and current_language in [lang for lang, _ in settings.LANGUAGES]:
                # URL language takes precedence - don't override it
                request.session[LANGUAGE_SESSION_KEY] = current_language
                return None

            # For cases without URL language prefix, detect language from other sources
            language = None

            # 1. Check URL parameter (from portal links)
            if 'lang' in request.GET:
                lang_param = request.GET.get('lang')
                if lang_param in ['en', 'fr', 'es', 'nl']:
                    language = lang_param

            # 2. Check session
            if not language:
                language = request.session.get(LANGUAGE_SESSION_KEY)

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

            # 4. Default fallback
            if not language:
                language = 'en'

            # Apply the detected language
            translation.activate(language)
            request.session[LANGUAGE_SESSION_KEY] = language
            request.LANGUAGE_CODE = language

        return None

    def process_response(self, request, response):
        """
        Log response details for debugging
        """
        # Ignore Chrome DevTools 404
        if response.status_code == 404 and '.well-known/appspecific/com.chrome.devtools.json' in request.path:
            return response

        # Log uniquement les erreurs et redirections
        if response.status_code in [301, 302, 303, 307, 308]:
            location = response.get('Location', 'N/A')
            logger.warning(f"LANGUAGE REDIRECT: {response.status_code} {request.path} → {location}")

        if response.status_code >= 400:
            logger.error(f"LANGUAGE ERROR: {response.status_code} for {request.method} {request.path}")

        return response

    def process_exception(self, request, exception):
        """
        Log all exceptions for debugging
        """
        logger.error(f"EXCEPTION in {request.method} {request.path}: {type(exception).__name__}: {exception}", exc_info=True)
        return None