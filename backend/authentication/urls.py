# authentication/urls.py
from django.urls import path
from .views import auth0_login, auth0_callback, auth0_logout, get_me, token_refresh
from .debug_views import cors_debug
from django.conf import settings

urlpatterns = [
    path('login/', auth0_login, name='auth0_login'),
    path('callback/', auth0_callback, name='auth0_callback'),
    path('logout/', auth0_logout, name='auth0_logout'),
    path('me/', get_me, name='get_me'),
    path('token/refresh/', token_refresh, name='token_refresh'),
]

if settings.DEBUG:
    urlpatterns += [
        path('cors-debug/', cors_debug, name='cors_debug'),
    ]