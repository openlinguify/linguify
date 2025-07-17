from rest_framework import serializers


class CommunitySettingsSerializer(serializers.Serializer):
    """Serializer for community settings"""
    community_notifications = serializers.BooleanField(default=True)
    mention_notifications = serializers.BooleanField(default=True)
    follow_notifications = serializers.BooleanField(default=True)
    post_reactions = serializers.BooleanField(default=True)
    post_visibility = serializers.ChoiceField(
        choices=[('public', 'Public'), ('friends', 'Friends'), ('private', 'Private')],
        default='public'
    )
    content_moderation = serializers.ChoiceField(
        choices=[('strict', 'Strict'), ('moderate', 'Moderate'), ('relaxed', 'Relaxed')],
        default='moderate'
    )
    auto_follow_back = serializers.BooleanField(default=False)
    show_activity_status = serializers.BooleanField(default=True)
    share_learning_progress = serializers.BooleanField(default=True)
    allow_study_groups = serializers.BooleanField(default=True)
    digest_frequency = serializers.ChoiceField(
        choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'), ('never', 'Never')],
        default='weekly'
    )