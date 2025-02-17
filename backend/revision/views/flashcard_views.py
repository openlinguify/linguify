# backend/revision/views/flashcard_views.py
from django.utils import timezone
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.utils.decorators import method_decorator
from revision.models import FlashcardDeck, Flashcard
from revision.serializers import FlashcardDeckSerializer, FlashcardSerializer

import logging

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class FlashcardDeckViewSet(viewsets.ModelViewSet):
    queryset = FlashcardDeck.objects.all()
    serializer_class = FlashcardDeckSerializer
    permission_classes = [AllowAny]

    @action(detail=True, methods=['get'])
    def cards(self, request, pk=None):
        deck = self.get_object()
        cards = deck.flashcards.filter(deck=deck)
        serializer = FlashcardSerializer(cards, many=True)
        return Response(serializer.data)

class FlashcardViewSet(viewsets.ModelViewSet):
    queryset = Flashcard.objects.all()
    serializer_class = FlashcardSerializer
    permission_classes = [AllowAny]

    @action(detail=True, methods=['patch'])
    def toggle_learned(self, request, pk=None):
        card = self.get_object()
        card.learned = not card.learned
        card.save()
        return Response({"status": "success"})
    
    @action(detail=True, methods=['delete'])
    def delete_card(self, request, pk=None):
        try:
            card = self.get_object()
            card.delete()
            return Response({"message": "Card deleted successfully"}), status.HTTP_204_NO_CONTENT
        except Exception as e:
            return Response({"error": str(e)}, status.HTTP_400_BAD_REQUEST)
    
