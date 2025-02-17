# backend/revision/views/flashcard_views.py
from django.utils import timezone
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from rest_framework import filters
from django.shortcuts import get_object_or_404
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
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = FlashcardDeck.objects.all()
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset

    @action(detail=True, methods=['get'])
    def cards(self, request, pk=None):
        """Récupérer toutes les cartes d'un deck spécifique"""
        try:
            deck = self.get_object()
            # Utilisation de related_name='flashcards' défini dans le modèle
            cards = deck.flashcards.all().order_by('-created_at')
            serializer = FlashcardSerializer(cards, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error fetching cards for deck {pk}: {str(e)}")
            return Response(
                {"error": f"Failed to fetch cards: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )


class FlashcardViewSet(viewsets.ModelViewSet):
    serializer_class = FlashcardSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['front_text', 'back_text']
    ordering_fields = ['created_at', 'last_reviewed', 'review_count']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filtrer les cartes par deck et statut"""
        queryset = Flashcard.objects.all()
        
        # Filtrer par deck
        deck_id = self.request.query_params.get('deck', None)
        if deck_id:
            queryset = queryset.filter(deck_id=deck_id)
        
        # Filtrer par statut learned
        learned = self.request.query_params.get('learned', None)
        if learned is not None:
            queryset = queryset.filter(learned=learned.lower() == 'true')
        
        return queryset

    def create(self, request, *args, **kwargs):
        """Créer une nouvelle carte dans un deck spécifique"""
        deck_id = request.data.get('deck')
        
        try:
            # Vérifier que le deck existe
            deck = get_object_or_404(FlashcardDeck, id=deck_id)
            
            # Créer la carte
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(deck=deck)
            
            logger.info(f"Created new flashcard in deck {deck_id}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating flashcard: {str(e)}")
            return Response(
                {"error": f"Failed to create flashcard: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['patch'])
    def toggle_learned(self, request, pk=None):
        """Basculer l'état d'apprentissage et mettre à jour les statistiques"""
        try:
            card = self.get_object()
            success = request.data.get('success', True)
            
            # Utiliser la méthode mark_reviewed du modèle
            card.mark_reviewed(success=success)
            
            serializer = self.get_serializer(card)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error toggling card {pk} learned status: {str(e)}")
            return Response(
                {"error": f"Failed to update card: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def due_for_review(self, request):
        """Récupérer les cartes à réviser"""
        try:
            limit = int(request.query_params.get('limit', 10))
            deck_id = request.query_params.get('deck', None)
            
            # Construction de la requête
            query = Q(next_review__lte=timezone.now()) | Q(next_review__isnull=True)
            if deck_id:
                query &= Q(deck_id=deck_id)
            
            cards = Flashcard.objects.filter(query).order_by('last_reviewed')[:limit]
            
            serializer = self.get_serializer(cards, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error fetching due cards: {str(e)}")
            return Response(
                {"error": f"Failed to fetch due cards: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
    @action(detail=True, methods=['patch'])
    def update_card(self, request, pk=None):
        try:
            card = self.get_object()
            serializer = self.get_serializer(card, data=request.data, partial=True)

            if serializer.is_valid():
                if 'front_text' in request.data:
                    card.front_text = request.data['front_text']
                if 'back_text' in request.data:
                    card.back_text = request.data['back_text']
                if 'learned' in request.data:
                    card.learned = request.data['learned']
                card.save()
                return Response(serializer.data)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response(
                {"error": f"Failed to update card: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )   