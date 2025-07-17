# backend/apps/notification/serializers/notification_serializers.py
from rest_framework import serializers
from ..models import Notification, NotificationSetting, NotificationDevice

class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for Notification model
    """
    class Meta:
        model = Notification
        fields = [
            'id', 'type', 'title', 'message', 'priority', 
            'data', 'is_read', 'created_at', 'expires_at'
        ]
        read_only_fields = ['id', 'created_at']

class NotificationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating notifications with validation
    """
    class Meta:
        model = Notification
        fields = [
            'user', 'type', 'title', 'message', 'priority', 
            'data', 'expires_at'
        ]
    
    def validate_expires_at(self, value):
        """
        Check that expires_at is in the future
        """
        from django.utils import timezone
        if value and value < timezone.now():
            raise serializers.ValidationError("Expiration date must be in the future")
        return value

class NotificationSettingSerializer(serializers.ModelSerializer):
    """
    Serializer for NotificationSetting model
    """
    class Meta:
        model = NotificationSetting
        fields = [
            'email_enabled', 'email_frequency',
            'push_enabled', 'web_enabled',
            'lesson_reminders', 'flashcard_reminders',
            'achievement_notifications', 'streak_notifications',
            'system_notifications',
            'quiet_hours_enabled', 'quiet_hours_start', 'quiet_hours_end'
        ]

class NotificationDeviceSerializer(serializers.ModelSerializer):
    """
    Serializer for NotificationDevice model
    """
    class Meta:
        model = NotificationDevice
        fields = [
            'id', 'device_token', 'device_type', 
            'device_name', 'is_active', 'created_at', 'last_used'
        ]
        read_only_fields = ['id', 'created_at', 'last_used']

    def validate_device_token(self, value):
        """
        Check that device token is not already registered to another user
        """
        user = self.context['request'].user
        existing = NotificationDevice.objects.filter(
            device_token=value
        ).exclude(user=user).first()
        
        if existing:
            # If token exists for another user, deactivate old device and allow new registration
            existing.is_active = False
            existing.save(update_fields=['is_active'])
        
        return value