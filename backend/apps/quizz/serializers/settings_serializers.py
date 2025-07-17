"""
Quiz settings serializers
"""
from rest_framework import serializers


class QuizSettingsSerializer(serializers.Serializer):
    """Serializer for quiz settings validation"""
    
    # Basic quiz settings
    auto_correct = serializers.BooleanField(default=True)
    show_explanation = serializers.BooleanField(default=True)
    timed_quiz = serializers.BooleanField(default=False)
    random_questions = serializers.BooleanField(default=True)
    multiple_attempts = serializers.BooleanField(default=True)
    
    # Difficulty and timing
    default_difficulty = serializers.ChoiceField(
        choices=['easy', 'medium', 'hard'],
        default='medium'
    )
    time_per_question = serializers.IntegerField(
        min_value=10,
        max_value=300,
        default=30,
        help_text="Time in seconds per question"
    )
    questions_per_quiz = serializers.IntegerField(
        min_value=5,
        max_value=50,
        default=10
    )
    
    # Progress tracking
    track_progress = serializers.BooleanField(default=True)
    show_statistics = serializers.BooleanField(default=True)
    mistake_review = serializers.BooleanField(default=True)
    adaptive_difficulty = serializers.BooleanField(default=False)
    streak_tracking = serializers.BooleanField(default=True)
    success_target = serializers.IntegerField(
        min_value=0,
        max_value=100,
        default=80,
        help_text="Target success percentage"
    )
    
    # Gamification
    enable_badges = serializers.BooleanField(default=True)
    leaderboard = serializers.BooleanField(default=True)
    daily_challenges = serializers.BooleanField(default=True)
    points_system = serializers.BooleanField(default=True)
    achievement_notifications = serializers.BooleanField(default=True)
    challenge_frequency = serializers.ChoiceField(
        choices=['daily', 'weekly', 'monthly'],
        default='daily'
    )
    
    def validate_time_per_question(self, value):
        """Ensure time per question is reasonable"""
        if value < 10:
            raise serializers.ValidationError(
                "Time per question must be at least 10 seconds"
            )
        return value
    
    def validate_questions_per_quiz(self, value):
        """Ensure number of questions is reasonable"""
        if value < 1:
            raise serializers.ValidationError(
                "Quiz must have at least 1 question"
            )
        return value
    
    def create(self, validated_data):
        """Create quiz settings - typically stored in user profile"""
        # This would be implemented based on your storage strategy
        return validated_data
    
    def update(self, instance, validated_data):
        """Update quiz settings"""
        # This would be implemented based on your storage strategy
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        return instance