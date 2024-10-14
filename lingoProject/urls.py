# lingoProject/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views import defaults as default_views
from linguify import views as linguify_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('base/', linguify_views.base),
    path('', linguify_views.index, name='index'),  # URL racine pour l'index
    path('platforme/', include('platforme.urls')),
    path('revision/', include('revision.urls')),
    path('linguify/', include('linguify.urls')),
    path('teaching/', include('teaching.urls')),
    path('authentication/', include('authentication.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += [
        path('400/', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
        path('403/', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        path('404/', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
        path('500/', default_views.server_error),
    ]
