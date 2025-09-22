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
        # Log incoming request details
        logger.info(f"REQUEST START: {request.method} {request.path}")
        logger.info(f"Headers: User-Agent={request.META.get('HTTP_USER_AGENT', 'N/A')[:100]}")
        logger.info(f"Headers: Accept-Language={request.META.get('HTTP_ACCEPT_LANGUAGE', 'N/A')}")
        logger.info(f"Headers: Referer={request.META.get('HTTP_REFERER', 'N/A')}")
        logger.info(f"Query params: {dict(request.GET)}")

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
                    logger.info(f"AUTHENTICATED USER: {user.username} → Language: {language}")
                    logger.info(f"FINAL LANGUAGE: {language} (from user preference)")
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
            # For anonymous users, check if LocaleMiddleware already set the language from URL
            logger.info(f"ANONYMOUS USER - analyzing language detection")
            current_language = getattr(request, 'LANGUAGE_CODE', None) or translation.get_language()
            logger.info(f"Current language from request/translation: {current_language}")

            # If URL contains a language prefix (handled by LocaleMiddleware), respect it
            url_has_language_prefix = any(request.path.startswith(f'/{lang}/') for lang, _ in settings.LANGUAGES)
            logger.info(f"URL has language prefix: {url_has_language_prefix}")

            if url_has_language_prefix:
                detected_lang = None
                for lang_code, _ in settings.LANGUAGES:
                    if request.path.startswith(f'/{lang_code}/'):
                        detected_lang = lang_code
                        break
                logger.info(f"URL Language detected: {detected_lang}")

            if url_has_language_prefix and current_language in [lang for lang, _ in settings.LANGUAGES]:
                # URL language takes precedence - don't override it
                logger.info(f"RESPECTING URL LANGUAGE: {current_language}")
                logger.info(f"FINAL LANGUAGE: {current_language} (from URL prefix)")
                request.session[LANGUAGE_SESSION_KEY] = current_language
                return None

            # For cases without URL language prefix, detect language from other sources
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
            logger.info(f"FINAL LANGUAGE: {language} (anonymous user fallback)")

        logger.info(f"MIDDLEWARE END: Language set to {getattr(request, 'LANGUAGE_CODE', 'N/A')}")
        return None

    def process_response(self, request, response):
        """
        Log response details for debugging
        """
        status_emoji = {
            200: "✅", 201: "✅", 202: "✅", 204: "✅",
            301: "🔄", 302: "🔄", 303: "🔄", 307: "🔄", 308: "🔄",
            400: "❌", 401: "🔒", 403: "🚫", 404: "🚯", 405: "🚫",
            500: "💥", 502: "💥", 503: "💥"
        }.get(response.status_code, "❓")

        logger.info(f"RESPONSE: {status_emoji} {response.status_code} for {request.method} {request.path}")

        # Log redirects with destination
        if response.status_code in [301, 302, 303, 307, 308]:
            location = response.get('Location', 'N/A')
            logger.warning(f"REDIRECT: {response.status_code} → {location}")

        # Log errors
        if response.status_code >= 400:
            logger.error(f"ERROR RESPONSE: {response.status_code} for {request.method} {request.path}")
            if hasattr(response, 'content') and len(response.content) < 1000:
                logger.error(f"Error content preview: {response.content.decode('utf-8', errors='ignore')[:200]}")

        return response

    def process_exception(self, request, exception):
        """
        Log all exceptions for debugging
        """
        logger.error(f"EXCEPTION in {request.method} {request.path}: {type(exception).__name__}: {exception}", exc_info=True)
        return None