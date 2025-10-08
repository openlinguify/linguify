"""
URL configuration for Linguify Teacher CMS project.
Ultra-modular architecture with HTMX support.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Authentication
    path('accounts/', include('django.contrib.auth.urls')),

    # Redirect root to dashboard
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),

    # Core CMS (Dashboard)
    path('dashboard/', include('apps.core.urls')),

    # Teacher management
    path('teachers/', include('apps.teachers.urls')),

    # Course management (NEW - Ultra-modular like Udemy/Superprof)
    path('cours/', include('apps.cours.urls')),

    # Content store (Legacy course content)
    path('courses/', include('apps.contentstore.urls')),

    # Scheduling & Appointments (Enhanced with HTMX)
    path('scheduling/', include('apps.scheduling.urls')),

    # Monetization
    path('monetization/', include('apps.monetization.urls')),

    # Sync API
    path('api/sync/', include('apps.sync.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)