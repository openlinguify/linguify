from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings


class RequireAuthenticationMiddleware:
    """
    Middleware pour protéger automatiquement toutes les vues SaaS.
    Redirige vers la page de connexion si l'utilisateur n'est pas authentifié.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Patterns d'URL qui nécessitent une authentification
        self.protected_patterns = [
            '/dashboard/',
            '/app-store/',
            '/profile/',
            '/settings/',
            '/api/user/',
            '/api/notifications/',
            '/admin-tools/',
        ]
        
        # Patterns d'URL qui sont toujours publics (même si dans un path protégé)
        self.public_patterns = [
            '/api/health/',
            '/api/status/',
        ]

    def __call__(self, request):
        # Vérifier si l'URL nécessite une authentification
        requires_auth = any(
            request.path.startswith(pattern) 
            for pattern in self.protected_patterns
        )
        
        # Vérifier si l'URL est explicitement publique
        is_public = any(
            request.path.startswith(pattern) 
            for pattern in self.public_patterns
        )
        
        # Si l'URL est protégée et l'utilisateur n'est pas connecté
        if requires_auth and not is_public and not request.user.is_authenticated:
            # Conserver l'URL de destination après connexion
            login_url = reverse('authentication:login')
            return redirect(f'{login_url}?next={request.path}')
        
        response = self.get_response(request)
        return response


class SaaSSecurityHeadersMiddleware:
    """
    Middleware pour ajouter des headers de sécurité spécifiques à la partie SaaS.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Appliquer uniquement aux routes SaaS
        if any(request.path.startswith(pattern) for pattern in ['/dashboard/', '/app-store/', '/profile/', '/settings/']):
            # Empêcher l'inclusion dans des iframes (protection clickjacking)
            response['X-Frame-Options'] = 'DENY'
            
            # Protection XSS
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-XSS-Protection'] = '1; mode=block'
            
            # Forcer HTTPS en production
            if not settings.DEBUG:
                response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response