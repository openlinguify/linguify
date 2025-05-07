# backend/apps/notification/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, NotificationSettingViewSet, NotificationDeviceViewSet

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'settings', NotificationSettingViewSet, basename='notification-settings')
router.register(r'devices', NotificationDeviceViewSet, basename='notification-devices')

app_name = 'notification'

urlpatterns = [
    path('', include(router.urls)),
]