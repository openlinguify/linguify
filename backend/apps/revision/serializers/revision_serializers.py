# revision/serializers.py
from rest_framework import serializers
from ..models import RevisionSession, VocabularyWord, VocabularyList
from .flashcard_serializers import FlashcardSerializer  # Import from specific module

class RevisionSessionSerializer(serializers.ModelSerializer):
    flashcards = FlashcardSerializer(many=True, read_only=True)
    due_date = serializers.SerializerMethodField()

    class Meta:
        model = RevisionSession
        fields = ['id', 'scheduled_date', 'completed_date', 'status', 
                 'success_rate', 'flashcards', 'due_date']
        read_only_fields = ['completed_date', 'status', 'success_rate']

    def get_due_date(self, obj):
        if obj.status == 'PENDING':
            return obj.scheduled_date
        return None

class VocabularyWordSerializer(serializers.ModelSerializer):
    # Add computed fields for backward compatibility with tests
    language = serializers.CharField(required=False, write_only=False)
    definition = serializers.CharField(source='notes', allow_blank=True, required=False)
    # Override required fields to make them optional at serializer level
    source_language = serializers.CharField(required=False)
    target_language = serializers.CharField(required=False)
    
    class Meta:
        model = VocabularyWord
        fields = ['id', 'word', 'translation', 'language', 'definition', 'source_language', 'target_language', 
                 'context', 'notes', 'created_at', 'last_reviewed', 'review_count', 
                 'mastery_level']
        read_only_fields = ['created_at', 'last_reviewed', 'review_count', 'mastery_level']

    def to_representation(self, instance):
        """Custom serialization to convert source_language to language"""
        data = super().to_representation(instance)
        # Convert source_language from uppercase to lowercase for API consistency
        data['language'] = instance.source_language.lower() if instance.source_language else None
        return data

    def validate(self, data):
        if not data.get('word') or not data.get('translation'):
            raise serializers.ValidationError("Both word and translation are required")
        
        # Handle the reverse mapping for 'language' -> 'source_language'
        if 'language' in data:
            language_code = data.pop('language')
            if language_code:
                data['source_language'] = language_code.upper()
                # If target_language is not provided, default to 'FR' (French)
                if 'target_language' not in data:
                    data['target_language'] = 'FR'
        
        # Ensure source_language and target_language are provided (either directly or via 'language')
        if not data.get('source_language'):
            raise serializers.ValidationError({"source_language": "This field is required (or provide 'language')."})
        if not data.get('target_language'):
            raise serializers.ValidationError({"target_language": "This field is required."})
        
        return data
    

class VocabularyListSerializer(serializers.ModelSerializer):
    words = VocabularyWordSerializer(many=True, read_only=True)
    word_count = serializers.SerializerMethodField()

    class Meta:
        model = VocabularyList
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 
                 'words', 'word_count']
        read_only_fields = ['created_at', 'updated_at']

    def get_word_count(self, obj):
        return obj.words.count()