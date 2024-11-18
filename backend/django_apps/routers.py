# django_apps/routers.py

from rest_framework.routers import DefaultRouter
from django_apps.authentication.viewsets import UserViewSet

router = DefaultRouter()
router.register(r'user', UserViewSet, basename='user')
