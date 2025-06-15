# backend/core/urls.py
from django.shortcuts import redirect
from django.contrib import admin
from django.urls import path, include
from . import utils
from . import views
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView, 
    SpectacularSwaggerView, 
    SpectacularRedocView
    )
from apps.authentication.views_terms import accept_terms, terms_status
from test_settings import test_settings
from django.contrib.sitemaps.views import sitemap, index as sitemap_index
try:
    from .advanced_sitemaps import sitemaps
except ImportError:
    from .sitemaps import sitemaps


def redirect_to_admin(request):
    return redirect('admin/')

urlpatterns = [
    # Frontend web (remplace la redirection vers admin)
    path('', include('frontend_web.urls')),
    path('admin/', admin.site.urls),
    # Add admin dashboard
    path('admin/stats/users/', include('apps.authentication.enhanced_admin.urls')),
    path('csrf/', utils.get_csrf_token, name='get_csrf_token'),
    path('api/', include('rest_framework.urls')),
    path('api/auth/', include('apps.authentication.urls')),
    # Test settings interface
    path('test-settings/', test_settings, name='test_settings'),
    # Terms and conditions endpoints
    path('api/auth/terms/accept', accept_terms, name='accept_terms'),
    path('api/auth/terms/status', terms_status, name='terms_status'),
    path('api/v1/course/', include('apps.course.urls', namespace='course')),
    path('api/v1/revision/', include('apps.revision.urls', namespace='revision')),
    path('api/v1/notebook/', include('apps.notebook.urls', namespace='notebook')),
    path('notebook/', include('apps.notebook.urls_web', namespace='notebook_web')),
    path('revision/', include('apps.revision.urls_web', namespace='revision_web')),
    path('course/', include('apps.course.urls_web', namespace='learning')),
    path('api/contact/', views.contact_view, name='contact'),
    path('api/v1/notifications/', include('apps.notification.urls', namespace='notification')),
    path('api/v1/language_ai/', include('apps.language_ai.urls', namespace='language_ai')),
    path('api/v1/jobs/', include('apps.jobs.urls', namespace='jobs')),
    path('api/v1/app-manager/', include('app_manager.urls', namespace='app_manager')),
    # path('api/v1/flashcard/', include('flashcard.urls', namespace='flashcard')),
    # path('api/v1/task/', include('task.urls', namespace='task')),
    # path('api/v1/chat/', include('chat.urls', namespace='chat')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/v1/quizz/', include('apps.quizz.urls', namespace='quizz')),
    
    # Sitemap URLs
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('sitemap-<section>.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('sitemap-index.xml', sitemap_index, {'sitemaps': sitemaps}, name='sitemap_index'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)