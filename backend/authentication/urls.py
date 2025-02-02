from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import auth0_login, auth0_callback, auth0_logout, user_profile, get_me_view
from .debug_views import cors_debug
from django.conf import settings

router = DefaultRouter()

# Auth0 specific URLs
auth0_patterns = [
    path('login/', auth0_login, name='auth0_login'),
    path('callback/', auth0_callback, name='auth0_callback'),
    path('logout/', auth0_logout, name='auth0_logout'),
    path('user/', user_profile, name='get_auth0_user'),
    path('me/', get_me_view, name='get_me'),
]

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include(auth0_patterns)),
]

if settings.DEBUG:
    urlpatterns += [
        path('cors-debug/', cors_debug, name='cors_debug'),
    ]