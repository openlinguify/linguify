from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import UserViewSet, UpdateCommissionOverride, CoachProfileViewSet, ReviewViewSet, UserFeedbackViewSet, get_user_profile, update_user_profile
from .views import auth0_login, auth0_callback, auth0_logout, get_auth0_user


router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'coaches', CoachProfileViewSet, basename='coach')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'user-feedback', UserFeedbackViewSet, basename='user-feedback')


# Auth0 specific URLs
auth0_patterns = [
    path('login/', auth0_login, name='auth0_login'),
    path('callback/', auth0_callback, name='auth0_callback'),
    path('logout/', auth0_logout, name='auth0_logout'),
    path('user/', get_auth0_user, name='auth0_user'),
]

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include(auth0_patterns)),
    path('commission-override/<int:coach_id>/', UpdateCommissionOverride.as_view(), name='commission-override'),
    path('profile/', get_user_profile, name='get_user_profile'),
    path('profile/update/', update_user_profile, name='update_user_profile'),
]