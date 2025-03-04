# backend/revision/views/flashcard_views.py
from django.utils import timezone
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
import pandas as pd
from rest_framework import filters
from django.shortcuts import get_object_or_404
from revision.models import FlashcardDeck, Flashcard
from revision.serializers import (
    FlashcardDeckSerializer, 
    FlashcardSerializer,
    FlashcardDeckDetailSerializer,
    FlashcardDeckCreateSerializer
)

import logging
logger = logging.getLogger(__name__)

class FlashcardDeckViewSet(viewsets.ModelViewSet):
    serializer_class = FlashcardDeckSerializer
    # Changement ici pour permettre l'accès sans authentification
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Sélectionne le sérialiseur approprié selon l'action."""
        if self.action == 'create':
            return FlashcardDeckCreateSerializer
        elif self.action == 'retrieve':
            return FlashcardDeckDetailSerializer
        return FlashcardDeckSerializer

    def get_queryset(self):
        """Filtre les decks pour ne montrer que ceux de l'utilisateur actuel ou tous en mode sans authentification."""
        # Version modifiée pour permettre l'accès sans authentification
        if self.request.user.is_authenticated:
            # Si authentifié, retourne les decks de l'utilisateur
            return FlashcardDeck.objects.filter(user=self.request.user)
        else:
            # Si non authentifié, retourne tous les decks (ou ceux marqués comme publics si vous avez un tel champ)
            return FlashcardDeck.objects.all()

    def perform_create(self, serializer):
        """Associe automatiquement l'utilisateur actuel lors de la création d'un deck."""
        # Version modifiée pour permettre la création sans authentification
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            # Créer sans utilisateur ou avec un utilisateur par défaut (à adapter selon votre modèle)
            from django.contrib.auth import get_user_model
            User = get_user_model()
            default_user = User.objects.first()  # Utilisez une méthode appropriée pour trouver un utilisateur par défaut
            if default_user:
                serializer.save(user=default_user)
            else:
                # Gérer le cas où aucun utilisateur n'existe
                serializer.save()  # Assurez-vous que votre modèle accepte un user=null si nécessaire

    @action(detail=True, methods=['get'])
    def cards(self, request, pk=None):
        """Récupérer toutes les cartes d'un deck spécifique."""
        try:
            # Version modifiée pour permettre l'accès sans authentification
            if self.request.user.is_authenticated:
                deck = get_object_or_404(FlashcardDeck, id=pk, user=request.user)
                cards_query = deck.flashcards.filter(user=request.user)
            else:
                deck = get_object_or_404(FlashcardDeck, id=pk)
                cards_query = deck.flashcards.all()
            
            # Filtres optionnels
            learned = request.query_params.get('learned')
            if learned is not None:
                is_learned = learned.lower() == 'true'
                cards_query = cards_query.filter(learned=is_learned)
                
            # Trier par date de création décroissante
            cards = cards_query.order_by('-created_at')
            
            serializer = FlashcardSerializer(cards, many=True, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error fetching cards for deck {pk}: {str(e)}")
            return Response(
                {"error": f"Failed to fetch cards: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

class FlashcardViewSet(viewsets.ModelViewSet):
    serializer_class = FlashcardSerializer
    # Changement ici pour permettre l'accès sans authentification
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['front_text', 'back_text']
    ordering_fields = ['created_at', 'last_reviewed', 'review_count']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filtrer les cartes par utilisateur, deck et statut."""
        # Version modifiée pour permettre l'accès sans authentification
        if self.request.user.is_authenticated:
            # Si authentifié, retourne les flashcards de l'utilisateur
            queryset = Flashcard.objects.filter(user=self.request.user)
        else:
            # Si non authentifié, retourne toutes les flashcards (ou filtrez selon votre logique)
            queryset = Flashcard.objects.all()
        
        # Filtrer par deck si demandé
        deck_id = self.request.query_params.get('deck')
        if deck_id:
            queryset = queryset.filter(deck_id=deck_id)
        
        # Filtrer par statut learned si demandé
        learned = self.request.query_params.get('learned')
        if learned is not None:
            is_learned = learned.lower() == 'true'
            queryset = queryset.filter(learned=is_learned)
            
        return queryset

    def create(self, request, *args, **kwargs):
        """Créer une nouvelle carte dans un deck spécifique."""
        deck_id = request.data.get('deck')
        
        try:
            # Version modifiée pour permettre la création sans authentification
            if self.request.user.is_authenticated:
                deck = get_object_or_404(FlashcardDeck, id=deck_id, user=request.user)
                # Créer la carte
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save(user=request.user, deck=deck)
            else:
                deck = get_object_or_404(FlashcardDeck, id=deck_id)
                # Utiliser un utilisateur par défaut ou null selon votre modèle
                from django.contrib.auth import get_user_model
                User = get_user_model()
                default_user = User.objects.first()
                
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                
                if default_user:
                    serializer.save(user=default_user, deck=deck)
                else:
                    # Assurez-vous que votre modèle accepte user=null si nécessaire
                    serializer.save(deck=deck)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating flashcard: {str(e)}")
            return Response(
                {"error": f"Failed to create flashcard: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['patch'])
    def toggle_learned(self, request, pk=None):
        """Basculer l'état d'apprentissage et mettre à jour les statistiques."""
        try:
            # Version modifiée pour permettre l'accès sans authentification
            if self.request.user.is_authenticated:
                card = get_object_or_404(Flashcard, id=pk, user=request.user)
            else:
                card = get_object_or_404(Flashcard, id=pk)
                
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
        """Récupérer les cartes à réviser pour l'utilisateur actuel."""
        try:
            limit = int(request.query_params.get('limit', 10))
            deck_id = request.query_params.get('deck', None)
            
            # Version modifiée pour permettre l'accès sans authentification
            if self.request.user.is_authenticated:
                # Construction de la requête - filtrer par utilisateur
                query = Q(user=request.user) & (Q(next_review__lte=timezone.now()) | Q(next_review__isnull=True))
                
                if deck_id:
                    # Vérifier que le deck appartient à l'utilisateur
                    if not FlashcardDeck.objects.filter(id=deck_id, user=request.user).exists():
                        return Response(
                            {"error": "Deck not found or access denied"},
                            status=status.HTTP_404_NOT_FOUND
                        )
                    query &= Q(deck_id=deck_id)
            else:
                # Pour les utilisateurs non authentifiés, juste filtrer par next_review et deck_id si fourni
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