# backend/apps/revision/middleware.py
import logging
import time
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse

logger = logging.getLogger('revision.security')

class RevisionSecurityMiddleware(MiddlewareMixin):
    """
    Middleware de sécurité pour l'application revision
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """
        Traite les requêtes entrantes pour l'app revision
        """
        # Ne traiter que les requêtes pour l'API revision
        if not request.path.startswith('/api/v1/revision/'):
            return None
        
        # Enregistrer le début de la requête
        request.revision_start_time = time.time()
        
        # Logging des requêtes sensibles
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            logger.info(f"Security log - {request.method} {request.path} - User: {getattr(request.user, 'id', 'anonymous')} - IP: {self.get_client_ip(request)}")
        
        return None
    
    def process_response(self, request, response):
        """
        Traite les réponses pour l'app revision
        """
        # Ne traiter que les requêtes pour l'API revision
        if not request.path.startswith('/api/v1/revision/'):
            return response
        
        # Calculer le temps de réponse
        if hasattr(request, 'revision_start_time'):
            duration = time.time() - request.revision_start_time
            
            # Logger les requêtes lentes (> 2 secondes)
            if duration > 2.0:
                logger.warning(f"Slow request - {request.method} {request.path} - Duration: {duration:.2f}s - User: {getattr(request.user, 'id', 'anonymous')}")
        
        # Logger les erreurs de sécurité
        if response.status_code in [401, 403, 429]:
            logger.warning(f"Security alert - {response.status_code} {request.method} {request.path} - User: {getattr(request.user, 'id', 'anonymous')} - IP: {self.get_client_ip(request)}")
        
        return response
    
    def get_client_ip(self, request):
        """
        Obtient l'IP réelle du client
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RevisionRateLimitMiddleware(MiddlewareMixin):
    """
    Middleware de rate limiting simple pour l'app revision
    """
    
    # Cache simple en mémoire (pour production, utiliser Redis)
    _request_counts = {}
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """
        Vérifie les limites de taux pour les actions sensibles
        """
        # Ne traiter que les requêtes pour l'API revision
        if not request.path.startswith('/api/v1/revision/'):
            return None
        
        # Limites globales par IP
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            ip = self.get_client_ip(request)
            
            # Limite globale : 100 requêtes modifiantes par heure par IP
            if self.is_rate_limited(ip, 'global', 100, 3600):
                logger.warning(f"Rate limit exceeded - IP: {ip} - Path: {request.path}")
                return JsonResponse(
                    {"detail": "Trop de requêtes. Veuillez patienter avant de réessayer."},
                    status=429
                )
        
        return None
    
    def is_rate_limited(self, identifier, key_suffix, max_requests, window_seconds):
        """
        Vérifie si l'identifiant a dépassé la limite de taux
        """
        import time
        
        cache_key = f"{identifier}:{key_suffix}"
        current_time = time.time()
        
        # Nettoyer les anciennes entrées
        if cache_key in self._request_counts:
            self._request_counts[cache_key] = [
                timestamp for timestamp in self._request_counts[cache_key]
                if current_time - timestamp < window_seconds
            ]
        else:
            self._request_counts[cache_key] = []
        
        # Vérifier la limite
        if len(self._request_counts[cache_key]) >= max_requests:
            return True
        
        # Enregistrer cette requête
        self._request_counts[cache_key].append(current_time)
        return False
    
    def get_client_ip(self, request):
        """
        Obtient l'IP réelle du client
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RevisionCacheMiddleware(MiddlewareMixin):
    """
    Middleware de cache simple pour les données publiques
    """
    
    def process_response(self, request, response):
        """
        Ajoute des headers de cache pour les ressources publiques
        """
        # Ne traiter que les requêtes GET pour l'API revision
        if (not request.path.startswith('/api/v1/revision/') or 
            request.method != 'GET'):
            return response
        
        # Cache pour les decks publics
        if 'public' in request.path or 'popular' in request.path:
            response['Cache-Control'] = 'public, max-age=300'  # 5 minutes
        
        # Cache pour les stats publiques
        elif 'stats' in request.path and not request.user.is_authenticated:
            response['Cache-Control'] = 'public, max-age=600'  # 10 minutes
        
        # Pas de cache pour les données privées
        elif request.user.is_authenticated:
            response['Cache-Control'] = 'private, no-cache'
        
        return response