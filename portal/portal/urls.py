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
from core.seo import views as seo_views

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
    # SEO files - using core.seo system
    path('robots.txt', seo_views.serve_robots_txt, name='robots_txt'),
    path('sitemap.xml', seo_views.serve_sitemap, {'sitemap_name': 'sitemap'}, name='sitemap_main'),
    path('sitemap-index.xml', seo_views.serve_sitemap, {'sitemap_name': 'sitemap-index'}, name='sitemap_index'),
    path('sitemap-static.xml', seo_views.serve_sitemap, {'sitemap_name': 'sitemap-static'}, name='sitemap_static'),
    path('sitemap-courses.xml', seo_views.serve_sitemap, {'sitemap_name': 'sitemap-courses'}, name='sitemap_courses'),
    path('sitemap-images.xml', seo_views.serve_sitemap, {'sitemap_name': 'sitemap-images'}, name='sitemap_images'),
    path('sitemap-videos.xml', seo_views.serve_sitemap, {'sitemap_name': 'sitemap-videos'}, name='sitemap_videos'),
    path('sitemap-en.xml', seo_views.serve_sitemap, {'sitemap_name': 'sitemap-en'}, name='sitemap_en'),
    path('sitemap-fr.xml', seo_views.serve_sitemap, {'sitemap_name': 'sitemap-fr'}, name='sitemap_fr'),
    path('sitemap-es.xml', seo_views.serve_sitemap, {'sitemap_name': 'sitemap-es'}, name='sitemap_es'),
    path('sitemap-nl.xml', seo_views.serve_sitemap, {'sitemap_name': 'sitemap-nl'}, name='sitemap_nl'),
    path('seo/status/', seo_views.sitemap_status, name='seo_status'),
    # Health check endpoint
    path('health/', health_check, name='health_check'),
    # API endpoints (no language prefix)
    path('api/v1/jobs/', include('core.jobs.urls')),
    # Redirection intelligente basée sur la langue du navigateur
    path('', LanguageRedirectView.as_view(), name='root_redirect'),
]

# URLs avec préfixe de langue
urlpatterns += i18n_patterns(
    # Pages publiques seulement - pas d'auth dans le portal
    path('', include('public_web.urls')),
    # Apps déplacées du backend
    path('blog/', include('core.blog.urls')),
    path('jobs/', include('core.jobs.urls_web', namespace='jobs_web')),  # Web interface for jobs
    path('careers/', include('core.jobs.urls_web', namespace='careers_web')),  # Alternative URL for careers
    prefix_default_language=True,
)

# Servir les fichiers statiques et media en développement
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# TEMPORARY: Force static files serving in production for debugging
if not settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)