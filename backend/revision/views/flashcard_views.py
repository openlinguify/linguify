# backend/revision/views/flashcard_views.py
from django.utils import timezone
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from revision.models import FlashcardDeck, Flashcard
from revision.serializers import FlashcardDeckSerializer, FlashcardSerializer

import logging

logger = logging.getLogger(__name__)

class FlashcardDeckViewSet(viewsets.ModelViewSet):
    serializer_class = FlashcardDeckSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return FlashcardDeck.objects.filter(is_active=True)

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        deck = self.get_object()
        deck.is_active = False
        deck.save()
        return Response({'status': 'deck archived'})

class FlashcardViewSet(viewsets.ModelViewSet):
    serializer_class = FlashcardSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        deck_id = self.request.query_params.get('deck')
        queryset = Flashcard.objects.all()

        if deck_id:
            queryset = queryset.filter(deck_id=deck_id)

        return queryset

    def perform_create(self, serializer):
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def mark_reviewed(self, request, pk=None):
        try:
            flashcard = self.get_object()
            success = request.data.get('success', True)
            flashcard.mark_reviewed(success=success)
            serializer = self.get_serializer(flashcard)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error marking flashcard as reviewed: {str(e)}")
            return Response(
                {'error': 'Failed to mark flashcard as reviewed'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def due_for_review(self, request):
        limit = int(request.query_params.get('limit', 10))
        queryset = self.get_queryset().filter(
            Q(next_review__isnull=True) |
            Q(next_review__lte=timezone.now())
        ).order_by('?')[:limit]
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
