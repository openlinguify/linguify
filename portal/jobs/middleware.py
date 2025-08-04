from django.http import Http404, JsonResponse
from django.utils.translation import gettext as _
import logging

logger = logging.getLogger(__name__)

class JobsErrorHandlingMiddleware:
    """Middleware pour gérer les erreurs spécifiques aux jobs"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """Gérer les exceptions dans les vues jobs"""
        
        # Ne traiter que les URLs liées aux jobs
        if not request.path.startswith('/careers/') and not '/careers/' in request.path:
            return None
            
        if isinstance(exception, Http404):
            # Pour les requêtes AJAX, retourner JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': _('Ressource non trouvée'),
                    'code': 'NOT_FOUND'
                }, status=404)
        
        # Log l'erreur pour le debugging
        logger.error(f"Jobs error in {request.path}: {exception}", exc_info=True)
        
        return None