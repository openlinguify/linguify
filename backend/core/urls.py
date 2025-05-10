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


def redirect_to_admin(request):
    return redirect('admin/')

urlpatterns = [
    path('', redirect_to_admin),
    path('admin/', admin.site.urls),
    # Add admin dashboard
    path('admin/stats/users/', include('apps.authentication.enhanced_admin.urls')),
    path('csrf/', utils.get_csrf_token, name='get_csrf_token'),
    path('api/', include('rest_framework.urls')),
    path('api/auth/', include('apps.authentication.urls')),
    path('api/v1/course/', include('apps.course.urls', namespace='course')),
    path('api/v1/revision/', include('apps.revision.urls', namespace='revision')),
    path('api/v1/notebook/', include('apps.notebook.urls', namespace='notebook')),
    path('api/contact/', views.contact_view, name='contact'),
    path('api/v1/progress/', include('apps.progress.urls', namespace='progress')),
    path('api/v1/notifications/', include('apps.notification.urls', namespace='notification')),
    path('api/v1/language_ai/', include('apps.language_ai.urls', namespace='language_ai')),
    # path('api/v1/flashcard/', include('flashcard.urls', namespace='flashcard')),
    # path('api/v1/task/', include('task.urls', namespace='task')),
    # path('api/v1/chat/', include('chat.urls', namespace='chat')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)