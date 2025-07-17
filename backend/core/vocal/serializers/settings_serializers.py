"""
Voice settings serializers for vocal app
"""
from rest_framework import serializers


class VoiceSettingsSerializer(serializers.Serializer):
    """Serializer for voice settings validation"""
    
    # Speech settings
    speech_rate = serializers.ChoiceField(
        choices=['slow', 'normal', 'fast'],
        default='normal',
        help_text="Speed of speech synthesis"
    )
    voice_pitch = serializers.FloatField(
        min_value=0.5,
        max_value=2.0,
        default=1.0,
        help_text="Pitch of synthesized voice"
    )
    
    # Microphone settings
    mic_sensitivity = serializers.IntegerField(
        min_value=0,
        max_value=100,
        default=70,
        help_text="Microphone sensitivity level"
    )
    noise_reduction = serializers.BooleanField(
        default=True,
        help_text="Enable noise reduction for voice input"
    )
    
    # Language settings
    accent = serializers.ChoiceField(
        choices=['auto', 'us', 'uk', 'au', 'ca', 'fr', 'es', 'de', 'it', 'pt', 'jp', 'cn', 'kr'],
        default='auto',
        help_text="Preferred accent for speech"
    )
    
    # Feedback settings
    pronunciation_feedback = serializers.BooleanField(
        default=True,
        help_text="Show pronunciation feedback"
    )
    continuous_conversation = serializers.BooleanField(
        default=False,
        help_text="Enable continuous conversation mode"
    )
    
    def validate_voice_pitch(self, value):
        """Ensure voice pitch is within reasonable range"""
        if value < 0.5 or value > 2.0:
            raise serializers.ValidationError(
                "Voice pitch must be between 0.5 and 2.0"
            )
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        # If continuous conversation is enabled, pronunciation feedback should be on
        if data.get('continuous_conversation') and not data.get('pronunciation_feedback'):
            data['pronunciation_feedback'] = True
            
        return data
    
    def create(self, validated_data):
        """Create voice settings - typically stored in user profile"""
        return validated_data
    
    def update(self, instance, validated_data):
        """Update voice settings"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        return instance