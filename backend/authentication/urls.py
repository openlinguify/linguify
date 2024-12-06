from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import UserViewSet, UpdateCommissionOverride, CoachProfileViewSet, ReviewViewSet, UserFeedbackViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'coaches', CoachProfileViewSet, basename='coach')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'user-feedback', UserFeedbackViewSet, basename='user-feedback')

urlpatterns = [
    path('', include(router.urls)),  # Inclure les URLs générées par le UserViewSet
    path('token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('commission-override/<int:coach_id>/', UpdateCommissionOverride.as_view(), name='commission-override'),
]
