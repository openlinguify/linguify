"""
Middleware d'optimisation pour gérer 100+ applications
"""
import logging
import time
from django.core.cache import cache
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from ..app_registry import get_app_registry
from ..app_synergies import get_synergy_manager

logger = logging.getLogger(__name__)

class AppOptimizationMiddleware(MiddlewareMixin):
    """
    Middleware pour optimiser les performances avec de nombreuses apps
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.registry = get_app_registry()
        self.synergy_manager = get_synergy_manager()
        self.cache_timeout = getattr(settings, 'APP_OPTIMIZATION_CACHE_TIMEOUT', 3600)
        
    def process_request(self, request):
        """Optimisations au niveau de la requête"""
        # Marquer le début de la requête
        request._app_optimization_start = time.time()
        
        # Mettre en cache les informations utilisateur fréquemment utilisées
        if hasattr(request, 'user') and request.user.is_authenticated:
            self._cache_user_app_data(request.user)
    
    def process_response(self, request, response):
        """Optimisations au niveau de la réponse"""
        # Calculer le temps de traitement
        if hasattr(request, '_app_optimization_start'):
            processing_time = time.time() - request._app_optimization_start
            response['X-App-Processing-Time'] = f"{processing_time:.3f}s"
            
            # Logger les requêtes lentes
            if processing_time > 1.0:
                logger.warning(f"Slow request: {request.path} took {processing_time:.3f}s")
        
        return response
    
    def _cache_user_app_data(self, user):
        """Met en cache les données d'apps fréquemment utilisées par l'utilisateur"""
        cache_key = f"user_app_data_{user.id}"
        
        if not cache.get(cache_key):
            try:
                # Récupérer les apps de l'utilisateur
                from app_manager.models import UserAppSettings
                user_settings = UserAppSettings.objects.filter(user=user).first()
                
                if user_settings:
                    enabled_apps = list(user_settings.enabled_apps.values_list('code', flat=True))
                    
                    # Calculer les recommandations
                    recommendations = self.synergy_manager.get_recommended_apps(enabled_apps)
                    
                    user_data = {
                        'enabled_apps': enabled_apps,
                        'recommendations': recommendations,
                        'last_updated': time.time()
                    }
                    
                    cache.set(cache_key, user_data, self.cache_timeout)
                    
            except Exception as e:
                logger.warning(f"Error caching user app data: {e}")


class LazyAppLoadingMiddleware(MiddlewareMixin):
    """
    Middleware pour le chargement paresseux des apps
    """
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """Charge uniquement les apps nécessaires pour cette vue"""
        # Identifier l'app concernée par cette requête
        resolver_match = getattr(request, 'resolver_match', None)
        if resolver_match:
            app_name = resolver_match.app_name
            if app_name:
                # Précharger les données de cette app uniquement
                self._preload_app_data(app_name, request)
    
    def _preload_app_data(self, app_name, request):
        """Précharge les données spécifiques à une app"""
        cache_key = f"app_data_{app_name}"
        
        if not cache.get(cache_key):
            try:
                registry = get_app_registry()
                app_info = registry.discover_all_apps().get(app_name)
                
                if app_info:
                    cache.set(cache_key, app_info, 1800)  # 30 minutes
                    
            except Exception as e:
                logger.warning(f"Error preloading app data for {app_name}: {e}")


class AppResourceMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware pour surveiller l'utilisation des ressources par app
    """
    
    def process_request(self, request):
        """Initialise le monitoring des ressources"""
        request._resource_start = {
            'time': time.time(),
            'cache_hits': self._get_cache_stats(),
        }
    
    def process_response(self, request, response):
        """Collecte les métriques de ressources"""
        if hasattr(request, '_resource_start'):
            # Calculer les métriques
            end_time = time.time()
            duration = end_time - request._resource_start['time']
            
            # Identifier l'app
            app_name = getattr(request.resolver_match, 'app_name', 'unknown') if hasattr(request, 'resolver_match') else 'unknown'
            
            # Stocker les métriques
            self._store_app_metrics(app_name, {
                'duration': duration,
                'status_code': response.status_code,
                'timestamp': end_time
            })
        
        return response
    
    def _get_cache_stats(self):
        """Récupère les statistiques de cache basiques"""
        try:
            return cache._cache.get_stats() if hasattr(cache._cache, 'get_stats') else {}
        except:
            return {}
    
    def _store_app_metrics(self, app_name, metrics):
        """Stocke les métriques d'une app"""
        cache_key = f"app_metrics_{app_name}"
        
        # Récupérer les métriques existantes
        existing_metrics = cache.get(cache_key, [])
        existing_metrics.append(metrics)
        
        # Garder seulement les 100 dernières métriques
        if len(existing_metrics) > 100:
            existing_metrics = existing_metrics[-100:]
        
        cache.set(cache_key, existing_metrics, 3600)  # 1 heure