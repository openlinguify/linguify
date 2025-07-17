"""
Notification settings serializers
"""
from rest_framework import serializers
from apps.authentication.models import User


class NotificationSettingsSerializer(serializers.ModelSerializer):
    """Serializer for notification preferences"""
    
    class Meta:
        model = User
        fields = [
            'email_notifications',
            'push_notifications', 
            'achievement_notifications',
            'lesson_notifications',
            'flashcard_notifications',
            'system_notifications',
        ]