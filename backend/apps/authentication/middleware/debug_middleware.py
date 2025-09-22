# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

"""
Middleware de debug complet pour tracker toutes les requêtes, erreurs et exceptions
"""

import logging
import time
from django.utils.deprecation import MiddlewareMixin
from django.http import Http404
from django.conf import settings

logger = logging.getLogger(__name__)


class DebugMiddleware(MiddlewareMixin):
    """
    Middleware de debug pour capturer toutes les informations de requête/réponse
    """

    def process_request(self, request):
        """
        Capture toutes les informations de la requête entrante
        """
        request._start_time = time.time()

        logger.info(f"🚀 ===== NEW REQUEST START =====")
        logger.info(f"🎯 METHOD: {request.method}")
        logger.info(f"🌐 PATH: {request.path}")
        logger.info(f"🔗 FULL URL: {request.build_absolute_uri()}")
        logger.info(f"📱 USER AGENT: {request.META.get('HTTP_USER_AGENT', 'N/A')[:150]}")
        logger.info(f"🌍 ACCEPT LANGUAGE: {request.META.get('HTTP_ACCEPT_LANGUAGE', 'N/A')}")
        logger.info(f"🔗 REFERER: {request.META.get('HTTP_REFERER', 'N/A')}")
        logger.info(f"🏠 REMOTE ADDR: {request.META.get('REMOTE_ADDR', 'N/A')}")
        logger.info(f"🔄 QUERY STRING: {request.META.get('QUERY_STRING', 'N/A')}")

        if request.GET:
            logger.info(f"📋 GET PARAMS: {dict(request.GET)}")

        if request.method == 'POST' and request.POST:
            # Log POST data but filter sensitive info
            post_data = dict(request.POST)
            sensitive_fields = ['password', 'password1', 'password2', 'csrfmiddlewaretoken']
            for field in sensitive_fields:
                if field in post_data:
                    post_data[field] = ['***HIDDEN***']
            logger.info(f"📝 POST PARAMS: {post_data}")

        # Log session info if available
        if hasattr(request, 'session'):
            session_data = dict(request.session)
            if 'django_language' in session_data:
                logger.info(f"🌐 SESSION LANGUAGE: {session_data['django_language']}")
            logger.info(f"🔑 SESSION KEYS: {list(session_data.keys())}")

        return None

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Log quelle vue va être appelée
        """
        view_name = getattr(view_func, '__name__', str(view_func))
        module_name = getattr(view_func, '__module__', 'Unknown')

        logger.info(f"🎯 VIEW RESOLVED: {module_name}.{view_name}")
        logger.info(f"📊 VIEW ARGS: {view_args}")
        logger.info(f"📊 VIEW KWARGS: {view_kwargs}")

        return None

    def process_response(self, request, response):
        """
        Log la réponse et calcule le temps de traitement
        """
        duration = 0
        if hasattr(request, '_start_time'):
            duration = (time.time() - request._start_time) * 1000  # ms

        status_emoji = {
            200: "✅", 201: "✅", 202: "✅", 204: "✅",
            301: "🔄", 302: "🔄", 303: "🔄", 307: "🔄", 308: "🔄",
            400: "❌", 401: "🔒", 403: "🚫", 404: "🚯", 405: "🚫",
            500: "💥", 502: "💥", 503: "💥", 504: "💥"
        }.get(response.status_code, "❓")

        logger.info(f"🏁 RESPONSE: {status_emoji} {response.status_code} | ⏱️ {duration:.2f}ms")

        # Log redirects avec la destination
        if response.status_code in [301, 302, 303, 307, 308]:
            location = response.get('Location', 'N/A')
            logger.warning(f"🔄 REDIRECT: {response.status_code} → {location}")

        # Log des détails sur les erreurs
        if response.status_code >= 400:
            logger.error(f"❌ ERROR RESPONSE: {response.status_code} for {request.method} {request.path}")

            # Log le contenu pour les petites erreurs
            if hasattr(response, 'content') and len(response.content) < 2000:
                try:
                    content_preview = response.content.decode('utf-8', errors='ignore')[:300]
                    logger.error(f"📄 ERROR CONTENT: {content_preview}")
                except:
                    logger.error(f"📄 ERROR CONTENT: [Unable to decode]")

        # Log spécial pour les 404
        if response.status_code == 404:
            logger.error(f"🚯 404 NOT FOUND: {request.method} {request.path}")
            logger.error(f"🚯 404 FULL URL: {request.build_absolute_uri()}")
            logger.error(f"🚯 404 REFERER: {request.META.get('HTTP_REFERER', 'N/A')}")

        logger.info(f"🏁 ===== REQUEST END ({duration:.2f}ms) =====")
        return response

    def process_exception(self, request, exception):
        """
        Log toutes les exceptions non gérées
        """
        duration = 0
        if hasattr(request, '_start_time'):
            duration = (time.time() - request._start_time) * 1000

        exception_type = type(exception).__name__

        if isinstance(exception, Http404):
            logger.error(f"🚯 HTTP 404 EXCEPTION: {request.method} {request.path}")
            logger.error(f"🚯 404 MESSAGE: {str(exception)}")
        else:
            logger.error(f"💥 UNHANDLED EXCEPTION: {exception_type} in {request.method} {request.path}")
            logger.error(f"💥 EXCEPTION MESSAGE: {str(exception)}")
            logger.error(f"💥 EXCEPTION DETAILS:", exc_info=True)

        logger.error(f"💥 EXCEPTION AFTER {duration:.2f}ms")
        return None