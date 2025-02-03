# backend/revision/serializers/flashcard_serializers.py
from rest_framework import serializers
from ..models import Flashcard, FlashcardDeck

class FlashcardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flashcard
        fields = ['id', 'front_text', 'back_text', 'learned', 'created_at', 
                 'last_reviewed', 'review_count', 'next_review']
        read_only_fields = ['created_at', 'last_reviewed', 'review_count', 'next_review']

    def validate(self, data):
        if not data.get('front_text') or not data.get('back_text'):
            raise serializers.ValidationError("Both front and back text are required")
        return data

class FlashcardDeckSerializer(serializers.ModelSerializer):
    flashcards = FlashcardSerializer(many=True, read_only=True)
    card_count = serializers.SerializerMethodField()
    learned_count = serializers.SerializerMethodField()

    class Meta:
        model = FlashcardDeck
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 
                 'is_active', 'flashcards', 'card_count', 'learned_count']
        read_only_fields = ['created_at', 'updated_at']

    def get_card_count(self, obj):
        return obj.flashcards.count()

    def get_learned_count(self, obj):
        return obj.flashcards.filter(learned=True).count()
