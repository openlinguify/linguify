"""
Community settings serializers
"""
from rest_framework import serializers


class CommunitySettingsSerializer(serializers.Serializer):
    """Serializer for community settings validation"""
    
    # Notification settings
    community_notifications = serializers.BooleanField(default=True)
    mention_notifications = serializers.BooleanField(default=True)
    follow_notifications = serializers.BooleanField(default=True)
    post_reactions = serializers.BooleanField(default=True)
    
    # Privacy settings
    post_visibility = serializers.ChoiceField(
        choices=['public', 'followers', 'private'],
        default='public',
        help_text="Default visibility for new posts"
    )
    content_moderation = serializers.ChoiceField(
        choices=['strict', 'moderate', 'minimal'],
        default='moderate',
        help_text="Level of content filtering"
    )
    
    # Social settings
    auto_follow_back = serializers.BooleanField(default=False)
    show_activity_status = serializers.BooleanField(default=True)
    share_learning_progress = serializers.BooleanField(default=True)
    allow_study_groups = serializers.BooleanField(default=True)
    
    # Digest settings
    digest_frequency = serializers.ChoiceField(
        choices=['daily', 'weekly', 'monthly', 'never'],
        default='weekly',
        help_text="Frequency of community digest emails"
    )
    
    def validate_post_visibility(self, value):
        """Ensure post visibility is valid"""
        valid_choices = ['public', 'followers', 'private']
        if value not in valid_choices:
            raise serializers.ValidationError(
                f"Post visibility must be one of: {', '.join(valid_choices)}"
            )
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        # If auto_follow_back is True, show_activity_status should also be True
        if data.get('auto_follow_back') and not data.get('show_activity_status'):
            # This is just a warning, not an error
            # You might want to log this or handle it differently
            pass
        
        # If share_learning_progress is False, ensure related settings make sense
        if not data.get('share_learning_progress') and data.get('allow_study_groups'):
            # Study groups might not work well without sharing progress
            # This could be a warning rather than an error
            pass
        
        return data
    
    def create(self, validated_data):
        """Create community settings - typically stored in user profile"""
        return validated_data
    
    def update(self, instance, validated_data):
        """Update community settings"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        return instance