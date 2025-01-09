from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import UserViewSet, UpdateCommissionOverride, CoachProfileViewSet, ReviewViewSet, UserFeedbackViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'coaches', CoachProfileViewSet, basename='coach')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'user-feedback', UserFeedbackViewSet, basename='user-feedback')

urlpatterns = [
    path('', include(router.urls)),  # Inclure les URLs générées par le UserViewSet
    path('login')
    path('commission-override/<int:coach_id>/', UpdateCommissionOverride.as_view(), name='commission-override'),
]
