# authentication/urls.py
from django.urls import path
from .views import Auth0Login, auth0_callback, auth0_logout, user_profile, get_me_view, token_refresh
from .debug_views import cors_debug  # Importer de debug_views.py au lieu de views.py
from django.conf import settings

urlpatterns = [
    path('login/', Auth0Login.as_view(), name='auth0_login'),
    path('callback/', auth0_callback, name='auth0_callback'),
    path('logout/', auth0_logout, name='auth0_logout'),
    path('user/', user_profile, name='auth0_user'),
    path('me/', get_me_view, name='get_me'),
    path('token/refresh/', token_refresh, name='token_refresh'),

]

if settings.DEBUG:
    urlpatterns += [
        path('cors-debug/', cors_debug, name='cors_debug'),
    ]