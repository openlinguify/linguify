# backend/revision/serializers/flashcard_serializers.py
from rest_framework import serializers
from ..models import FlashcardDeck, Flashcard

class FlashcardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flashcard
        fields = ['id', 'deck', 'front_text', 'back_text', 'learned', 'created_at', 'updated_at', 
                  'last_reviewed', 'review_count', 'next_review']
        read_only_fields = ['created_at', 'updated_at', 'last_reviewed', 'review_count', 'next_review']

    def validate(self, data):
        if not data.get('front_text') or not data.get('back_text'):
            raise serializers.ValidationError("Both front and back text are required")
        return data

class FlashcardDeckSerializer(serializers.ModelSerializer):
    cards = FlashcardSerializer(many=True, read_only=True)
    class Meta:
        model = FlashcardDeck
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'is_active', 'cards']
        read_only_fields = ['created_at', 'updated_at']
