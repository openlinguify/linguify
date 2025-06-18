# backend/apps/notification/views.py
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q

from .models import Notification, NotificationSetting, NotificationDevice
from .serializers import (
    NotificationSerializer, 
    NotificationCreateSerializer,
    NotificationSettingSerializer, 
    NotificationDeviceSerializer
)

class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notifications
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'priority']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Return only notifications for the current user
        and filter out expired notifications
        """
        user = self.request.user
        return Notification.objects.filter(
            user=user
        ).filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
        ).order_by('-created_at')
    
    def get_serializer_class(self):
        """
        Use different serializers for different actions
        """
        if self.action == 'create':
            return NotificationCreateSerializer
        return NotificationSerializer
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """
        Return only unread notifications
        """
        unread = self.get_queryset().filter(is_read=False)
        serializer = self.get_serializer(unread, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """
        Mark all notifications as read
        """
        self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({"status": "All notifications marked as read"})
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """
        Mark a specific notification as read
        """
        notification = self.get_object()
        notification.mark_as_read()
        return Response({"status": "Notification marked as read"})
    
    @action(detail=False, methods=['get'])
    def count_unread(self, request):
        """
        Return the count of unread notifications
        """
        count = self.get_queryset().filter(is_read=False).count()
        return Response({"count": count})
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """
        Return notifications filtered by type
        """
        notification_type = request.query_params.get('type', None)
        if not notification_type:
            return Response(
                {"error": "Type parameter is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        notifications = self.get_queryset().filter(type=notification_type)
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['delete'])
    def clear_all(self, request):
        """
        Delete all notifications for the current user
        """
        self.get_queryset().delete()
        return Response(
            {"status": "All notifications deleted"}, 
            status=status.HTTP_204_NO_CONTENT
        )

class NotificationSettingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notification settings
    """
    serializer_class = NotificationSettingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Return only notification settings for the current user
        """
        user = self.request.user
        return NotificationSetting.objects.filter(user=user)
    
    def list(self, request):
        """
        Return the notification settings for the current user
        Create default settings if none exist
        """
        user = request.user
        settings, created = NotificationSetting.objects.get_or_create(user=user)
        serializer = self.get_serializer(settings)
        return Response(serializer.data)
    
    def create(self, request):
        """
        Override create to ensure we update existing settings
        """
        user = request.user
        settings, created = NotificationSetting.objects.get_or_create(user=user)
        serializer = self.get_serializer(settings, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @action(detail=False, methods=['patch'])
    def update_settings(self, request):
        """
        Update notification settings
        """
        user = request.user
        settings, created = NotificationSetting.objects.get_or_create(user=user)
        serializer = self.get_serializer(settings, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class NotificationDeviceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notification devices
    """
    serializer_class = NotificationDeviceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Return only notification devices for the current user
        """
        user = self.request.user
        return NotificationDevice.objects.filter(user=user)
    
    def perform_create(self, serializer):
        """
        Set the user when creating a new device
        """
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """
        Deactivate a specific device
        """
        device = self.get_object()
        device.is_active = False
        device.save(update_fields=['is_active'])
        return Response({"status": "Device deactivated"})
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        Activate a specific device
        """
        device = self.get_object()
        device.is_active = True
        device.save(update_fields=['is_active'])
        return Response({"status": "Device activated"})
    
    @action(detail=False, methods=['delete'])
    def remove_inactive(self, request):
        """
        Remove all inactive devices for the current user
        """
        user = request.user
        deleted_count = NotificationDevice.objects.filter(
            user=user, is_active=False
        ).delete()[0]
        
        return Response({
            "status": "Inactive devices removed",
            "count": deleted_count
        })