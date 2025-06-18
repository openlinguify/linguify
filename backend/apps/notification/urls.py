# backend/apps/notification/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, NotificationSettingViewSet, NotificationDeviceViewSet
from . import views_push

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'settings', NotificationSettingViewSet, basename='notification-settings')
router.register(r'devices', NotificationDeviceViewSet, basename='notification-devices')

app_name = 'notification'

urlpatterns = [
    path('', include(router.urls)),

    # Push notification subscriptions
    path('subscriptions/', views_push.register_push_subscription, name='register_subscription'),
    path('subscriptions/unregister/', views_push.unregister_push_subscription, name='unregister_subscription'),
    path('subscriptions/list/', views_push.get_push_subscriptions, name='list_subscriptions'),
    path('test/', views_push.send_test_notification, name='send_test'),
]