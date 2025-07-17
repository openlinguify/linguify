"""
Notebook settings serializers
"""
from rest_framework import serializers


class NotebookSettingsSerializer(serializers.Serializer):
    """Serializer for notebook settings validation"""
    
    # Editor settings
    auto_save = serializers.BooleanField(default=True)
    markdown_preview = serializers.BooleanField(default=True)
    spell_check = serializers.BooleanField(default=True)
    version_history = serializers.BooleanField(default=True)
    
    # Appearance settings
    font_family = serializers.ChoiceField(
        choices=['system', 'serif', 'sans-serif', 'monospace'],
        default='system'
    )
    font_size = serializers.ChoiceField(
        choices=['small', 'medium', 'large', 'extra-large'],
        default='medium'
    )
    
    # Auto-save settings
    auto_save_interval = serializers.IntegerField(
        min_value=5,
        max_value=60,
        default=10,
        help_text="Auto-save interval in seconds"
    )
    
    # Organization settings
    auto_categorize = serializers.BooleanField(default=True)
    show_tags = serializers.BooleanField(default=True)
    recent_notes = serializers.BooleanField(default=True)
    
    # Display settings
    default_view = serializers.ChoiceField(
        choices=['list', 'grid', 'cards'],
        default='list'
    )
    default_sort = serializers.ChoiceField(
        choices=['created', 'modified', 'title', 'language'],
        default='modified'
    )
    notes_per_page = serializers.IntegerField(
        min_value=10,
        max_value=100,
        default=20,
        help_text="Number of notes to display per page"
    )
    
    # Sharing settings
    allow_sharing = serializers.BooleanField(default=False)
    public_notes = serializers.BooleanField(default=False)
    collaborative_editing = serializers.BooleanField(default=False)
    default_permissions = serializers.ChoiceField(
        choices=['private', 'view-only', 'edit'],
        default='private'
    )
    
    def validate_auto_save_interval(self, value):
        """Ensure auto-save interval is reasonable"""
        if value < 5:
            raise serializers.ValidationError(
                "Auto-save interval must be at least 5 seconds"
            )
        if value > 60:
            raise serializers.ValidationError(
                "Auto-save interval cannot exceed 60 seconds"
            )
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        # If public_notes is True, allow_sharing must also be True
        if data.get('public_notes') and not data.get('allow_sharing'):
            raise serializers.ValidationError({
                'public_notes': 'Cannot make notes public without enabling sharing'
            })
        
        # If collaborative_editing is True, allow_sharing must also be True
        if data.get('collaborative_editing') and not data.get('allow_sharing'):
            raise serializers.ValidationError({
                'collaborative_editing': 'Cannot enable collaborative editing without enabling sharing'
            })
        
        return data
    
    def create(self, validated_data):
        """Create notebook settings - typically stored in user profile"""
        return validated_data
    
    def update(self, instance, validated_data):
        """Update notebook settings"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        return instance