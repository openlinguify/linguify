"""
Learning settings serializers for course app
"""
from rest_framework import serializers
from apps.authentication.models import User


class LearningSettingsSerializer(serializers.ModelSerializer):
    """Serializer for learning preferences"""
    
    class Meta:
        model = User
        fields = [
            'daily_goal',
            'weekday_reminders',
            'weekend_reminders', 
            'reminder_time',
            'speaking_exercises',
            'listening_exercises',
            'reading_exercises',
            'writing_exercises',
            'native_language',
            'target_language',
            'language_level',
            'objectives',
        ]
        
    def validate(self, data):
        """Validate that native and target languages are different"""
        native_lang = data.get('native_language', self.instance.native_language if self.instance else None)
        target_lang = data.get('target_language', self.instance.target_language if self.instance else None)
        
        if native_lang and target_lang and native_lang == target_lang:
            raise serializers.ValidationError(
                "Native language and target language must be different"
            )
        
        return data