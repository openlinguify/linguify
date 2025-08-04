"""
URL configuration for Linguify Teacher CMS project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # Add authentication URLs
    path('', include('apps.core.urls')),
    path('teachers/', include('apps.teachers.urls')),
    path('courses/', include('apps.contentstore.urls')),  # Main course management
    path('monetization/', include('apps.monetization.urls')),
    path('scheduling/', include('apps.scheduling.urls')),
    path('api/sync/', include('apps.sync.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)