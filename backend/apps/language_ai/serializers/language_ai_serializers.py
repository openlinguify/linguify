from rest_framework import serializers
from ..models import ConversationTopic, AIConversation, ConversationMessage, ConversationFeedback


class ConversationTopicSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les sujets de conversation."""
    language_display = serializers.CharField(source='get_language_display', read_only=True)
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)

    class Meta:
        model = ConversationTopic
        fields = [
            'id', 'name', 'description', 'language', 'language_display',
            'difficulty', 'difficulty_display', 'is_active'
        ]


class ConversationMessageSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les messages de conversation."""
    message_type_display = serializers.CharField(source='get_message_type_display', read_only=True)
    has_feedback = serializers.SerializerMethodField()

    class Meta:
        model = ConversationMessage
        fields = [
            'id', 'conversation', 'message_type', 'message_type_display',
            'content', 'created_at', 'word_count', 'has_feedback'
        ]
        read_only_fields = ['word_count', 'created_at']

    def get_has_feedback(self, obj):
        return obj.feedback.exists()


class ConversationFeedbackSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les feedbacks sur les messages."""
    correction_type_display = serializers.CharField(source='get_correction_type_display', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = ConversationFeedback
        fields = [
            'id', 'message', 'user', 'user_name', 'correction_type',
            'correction_type_display', 'corrected_content',
            'explanation', 'created_at'
        ]
        read_only_fields = ['user', 'created_at']

    def create(self, validated_data):
        # Assigner l'utilisateur actuel
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AIConversationSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les conversations AI."""
    topic_name = serializers.CharField(source='topic.name', read_only=True)
    language_display = serializers.CharField(source='get_language_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    messages_count = serializers.IntegerField(source='message_count', read_only=True)
    duration = serializers.FloatField(source='duration_minutes', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = AIConversation
        fields = [
            'id', 'user', 'user_name', 'topic', 'topic_name', 'language',
            'language_display', 'ai_persona', 'status', 'status_display',
            'created_at', 'last_activity', 'feedback_summary',
            'messages_count', 'duration'
        ]
        read_only_fields = ['user', 'created_at', 'last_activity']

    def create(self, validated_data):
        # Assigner l'utilisateur actuel
        validated_data['user'] = self.context['request'].user
        
        # Assurer la cohérence entre le topic et le langage
        topic = validated_data.get('topic')
        if topic and not validated_data.get('language'):
            validated_data['language'] = topic.language
            
        return super().create(validated_data)


class ConversationDetailSerializer(AIConversationSerializer):
    """Sérialiseur détaillé pour une conversation avec ses messages."""
    messages = ConversationMessageSerializer(many=True, read_only=True)
    topic_details = ConversationTopicSerializer(source='topic', read_only=True)

    class Meta(AIConversationSerializer.Meta):
        fields = AIConversationSerializer.Meta.fields + ['messages', 'topic_details']