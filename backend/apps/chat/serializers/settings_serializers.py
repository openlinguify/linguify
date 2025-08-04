"""
Chat settings serializers
"""
from rest_framework import serializers


class ChatSettingsSerializer(serializers.Serializer):
    """Serializer for chat settings validation"""
    
    # Notification settings
    chat_notifications = serializers.BooleanField(default=True)
    chat_sounds = serializers.BooleanField(default=True)
    typing_indicators = serializers.BooleanField(default=True)
    read_receipts = serializers.BooleanField(default=True)
    
    # Organization settings
    auto_archive = serializers.BooleanField(default=False)
    
    # Appearance settings
    text_size = serializers.ChoiceField(
        choices=['small', 'medium', 'large'],
        default='medium'
    )
    chat_theme = serializers.ChoiceField(
        choices=['default', 'dark', 'light', 'compact'],
        default='default'
    )
    
    # Privacy settings
    allow_anyone_to_message = serializers.BooleanField(default=False)
    show_online_status = serializers.BooleanField(default=True)
    show_last_seen = serializers.BooleanField(default=True)
    
    # Data retention
    message_retention = serializers.ChoiceField(
        choices=['forever', '30days', '90days', '1year'],
        default='forever',
        help_text="How long to keep messages"
    )
    
    def validate(self, data):
        """Cross-field validation"""
        # If show_online_status is False, show_last_seen should also be False
        if not data.get('show_online_status') and data.get('show_last_seen'):
            data['show_last_seen'] = False
            
        # If allow_anyone_to_message is False, certain features might be limited
        if not data.get('allow_anyone_to_message'):
            # Could add warnings or additional logic here
            pass
            
        return data
    
    def create(self, validated_data):
        """Create chat settings - typically stored in user profile"""
        return validated_data
    
    def update(self, instance, validated_data):
        """Update chat settings"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        return instance