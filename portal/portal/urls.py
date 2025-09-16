"""
URL configuration for portal project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import RedirectView
from django.http import JsonResponse
from public_web.views import LanguageRedirectView

def health_check(request):
    """Health check endpoint for monitoring"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'linguify-portal',
        'version': '1.0.0'
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    # Health check endpoint
    path('health/', health_check, name='health_check'),
    # API endpoints (no language prefix)
    path('api/v1/jobs/', include('jobs.urls')),
    # Redirection intelligente basée sur la langue du navigateur
    path('', LanguageRedirectView.as_view(), name='root_redirect'),
]

# URLs avec préfixe de langue
urlpatterns += i18n_patterns(
    # Pages publiques seulement - pas d'auth dans le portal
    path('', include('public_web.urls')),
    # Apps déplacées du backend
    path('blog/', include('blog.urls')),
    path('jobs/', include('jobs.urls_web', namespace='jobs_web')),  # Web interface for jobs
    path('careers/', include('jobs.urls_web', namespace='careers_web')),  # Alternative URL for careers
    prefix_default_language=True,
)

# Servir les fichiers statiques et media en développement
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# TEMPORARY: Force static files serving in production for debugging
if not settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)