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

        # Log uniquement si POST ou paramètres GET présents
        if request.method == 'POST' and request.POST:
            post_data = dict(request.POST)
            sensitive_fields = ['password', 'password1', 'password2', 'csrfmiddlewaretoken']
            for field in sensitive_fields:
                if field in post_data:
                    post_data[field] = ['***HIDDEN***']
            logger.info(f"📝 POST {request.path}: {post_data}")

        if request.GET:
            logger.info(f"📋 GET {request.path}: {dict(request.GET)}")

        return None

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Log quelle vue va être appelée
        """
        return None

    def process_response(self, request, response):
        """
        Log la réponse et calcule le temps de traitement
        """
        # Ignore Chrome DevTools 404
        if response.status_code == 404 and '.well-known/appspecific/com.chrome.devtools.json' in request.path:
            return response

        # Log uniquement les erreurs et redirections
        if response.status_code >= 400:
            logger.error(f"❌ {response.status_code} {request.method} {request.path}")

            if response.status_code == 404:
                logger.error(f"🚯 404: {request.build_absolute_uri()}")

            if hasattr(response, 'content') and len(response.content) < 2000:
                try:
                    content_preview = response.content.decode('utf-8', errors='ignore')[:300]
                    logger.error(f"📄 Content: {content_preview}")
                except:
                    pass
        elif response.status_code in [301, 302, 303, 307, 308]:
            location = response.get('Location', 'N/A')
            logger.warning(f"🔄 REDIRECT {response.status_code}: {request.path} → {location}")

        return response

    def process_exception(self, request, exception):
        """
        Log toutes les exceptions non gérées
        """
        if not isinstance(exception, Http404):
            logger.error(f"💥 UNHANDLED EXCEPTION: {type(exception).__name__} in {request.method} {request.path}", exc_info=True)
        return None