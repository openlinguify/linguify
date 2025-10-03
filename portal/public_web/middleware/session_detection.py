"""
Middleware pour détecter automatiquement si un utilisateur est connecté sur le backend
en lisant le cookie de session partagé et en vérifiant via l'API backend
"""
import requests
from django.conf import settings
from django.utils.functional import SimpleLazyObject
import logging

logger = logging.getLogger(__name__)


def get_backend_user(session_key):
    """
    Récupère les informations utilisateur depuis le backend via l'API
    """
    if not session_key:
        return None

    try:
        # Déterminer l'URL du backend
        django_env = getattr(settings, 'DJANGO_ENV', 'development')
        is_production = django_env == 'production' or not getattr(settings, 'DEBUG', True)

        if is_production:
            backend_url = "https://app.openlinguify.com"
        else:
            backend_url = "http://127.0.0.1:8081"

        # Appeler l'API de vérification de session
        response = requests.get(
            f"{backend_url}/api/auth/check-session/",
            params={'session_key': session_key},
            timeout=3  # 3 secondes max
        )

        if response.status_code == 200:
            data = response.json()
            if data.get('authenticated'):
                return data.get('user')

        return None

    except requests.RequestException as e:
        logger.warning(f"Failed to check backend session: {e}")
        return None
    except Exception as e:
        logger.error(f"Error checking backend session: {e}", exc_info=True)
        return None


class BackendSessionMiddleware:
    """
    Middleware qui détecte si un utilisateur est connecté sur le backend
    en vérifiant le cookie de session partagé
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Récupérer le cookie de session
        session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME)

        # Créer un lazy object pour éviter de faire l'appel API à chaque requête
        # L'API ne sera appelée que si on accède à request.backend_user
        request.backend_user = SimpleLazyObject(
            lambda: get_backend_user(session_key)
        )

        response = self.get_response(request)
        return response
