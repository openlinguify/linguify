# backend/core/urls.py
from django.shortcuts import redirect
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
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
from tests.test_settings import test_settings
from django.contrib.sitemaps.views import sitemap, index as sitemap_index
from .seo.views import serve_sitemap, serve_robots_txt, sitemap_status


def redirect_to_admin(request):
    return redirect('admin/')

# URLs without language prefix (for compatibility)
urlpatterns = [
    # Language switching
    path('i18n/', include('django.conf.urls.i18n')),
    
    # SaaS application (protected routes) - no language prefix
    path('', include('saas_web.urls')),
    
    # Legacy frontend web (à supprimer après migration complète)
    # path('legacy/', include('frontend_web.urls')),
    
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
    path('learning/', include('apps.course.urls_web', namespace='learning_alias')),
    path('quizz/', include('apps.quizz.urls_web', namespace='quizz_web')),
    path('language_ai/', include('apps.language_ai.urls_web', namespace='language_ai_web')),
    path('api/contact/', views.contact_view, name='contact'),
    path('api/v1/notifications/', include('apps.notification.urls', namespace='notification')),
    path('api/v1/language_ai/', include('apps.language_ai.urls', namespace='language_ai')),
    path('api/v1/jobs/', include('core.jobs.urls', namespace='jobs')),
    path('api/v1/app-manager/', include('app_manager.urls', namespace='app_manager')),
    # path('api/v1/flashcard/', include('flashcard.urls', namespace='flashcard')),
    # path('api/v1/task/', include('task.urls', namespace='task')),
    # path('api/v1/chat/', include('chat.urls', namespace='chat')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/v1/quizz/', include('apps.quizz.urls', namespace='quizz')),
    
    # SEO URLs - Organized sitemap serving
    path('robots.txt', serve_robots_txt, name='robots_txt'),
    path('sitemap.xml', serve_sitemap, {'sitemap_name': 'sitemap'}, name='sitemap_main'),
    path('sitemap-index.xml', serve_sitemap, {'sitemap_name': 'sitemap-index'}, name='sitemap_index'),
    path('sitemap-static.xml', serve_sitemap, {'sitemap_name': 'sitemap-static'}, name='sitemap_static'),
    path('sitemap-courses.xml', serve_sitemap, {'sitemap_name': 'sitemap-courses'}, name='sitemap_courses'),
    path('sitemap-learning.xml', serve_sitemap, {'sitemap_name': 'sitemap-learning'}, name='sitemap_learning'),
    path('sitemap-ugc.xml', serve_sitemap, {'sitemap_name': 'sitemap-ugc'}, name='sitemap_ugc'),
    path('sitemap-images.xml', serve_sitemap, {'sitemap_name': 'sitemap-images'}, name='sitemap_images'),
    path('sitemap-videos.xml', serve_sitemap, {'sitemap_name': 'sitemap-videos'}, name='sitemap_videos'),
    path('sitemap-en.xml', serve_sitemap, {'sitemap_name': 'sitemap-en'}, name='sitemap_en'),
    path('sitemap-fr.xml', serve_sitemap, {'sitemap_name': 'sitemap-fr'}, name='sitemap_fr'),
    path('sitemap-es.xml', serve_sitemap, {'sitemap_name': 'sitemap-es'}, name='sitemap_es'),
    path('sitemap-nl.xml', serve_sitemap, {'sitemap_name': 'sitemap-nl'}, name='sitemap_nl'),
    
    # SEO Status and Management
    path('seo/status/', sitemap_status, name='seo_status'),
]

# URLs with language prefix (for public website and authentication)
urlpatterns += i18n_patterns(
    # Authentication (login/register pages) - with language prefix
    path('auth/', include('apps.authentication.urls_auth')),
    
    # Careers/Jobs pages - with language prefix (public-facing)
    path('careers/', include('core.jobs.urls_web', namespace='jobs_web')),
    
    # Public website (landing, marketing) - with language prefix
    path('', include('public_web.urls')),
    prefix_default_language=True,  # Add language prefix even for default language
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)