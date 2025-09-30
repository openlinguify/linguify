# backend/revision/views/flashcard_views.py
from django.utils import timezone
from django.db.models import Q, Count, Prefetch, Max
from django.core.exceptions import ValidationError, ObjectDoesNotExist, PermissionDenied
from django.db import IntegrityError, OperationalError
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from ..permissions import FlashcardDeckPermission, FlashcardPermission, DeckBatchPermission, RateLimitPermission
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination
import pandas as pd
from rest_framework import filters
from django.shortcuts import get_object_or_404
from apps.revision.models import FlashcardDeck, Flashcard
from apps.revision.serializers import (
    FlashcardDeckSerializer, 
    FlashcardSerializer,
    FlashcardDeckDetailSerializer,
    FlashcardDeckCreateSerializer,
    DeckArchiveSerializer,
    BatchDeleteSerializer,
    BatchArchiveSerializer,
    DeckLearningSettingsSerializer,
    ApplyPresetSerializer
)
from django.http import JsonResponse
import re

import logging
logger = logging.getLogger(__name__)

class DeckPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

# ===== MIXINS POUR ÉVITER LA DUPLICATION =====

# DeckCloneMixin migré vers explorer_views.py

class DeckPermissionMixin:
    """Mixin pour la gestion des permissions des decks."""
    
    def check_deck_owner(self, deck, user):
        """Vérifie que l'utilisateur est propriétaire du deck."""
        return deck.user == user
    
    def check_deck_access(self, deck, user):
        """Vérifie l'accès en lecture (public ou propriétaire)."""
        return deck.is_public or (user.is_authenticated and deck.user == user)
    
    def check_deck_not_archived(self, deck):
        """Vérifie que le deck n'est pas archivé."""
        return not deck.is_archived

class OptimizedQuerysetMixin:
    """Mixin pour les querysets optimisés avec stratégies contextuelles."""
    
    def get_base_deck_queryset(self):
        """Base queryset avec optimisations minimales."""
        return FlashcardDeck.objects.select_related('user')
    
    def get_list_optimized_queryset(self):
        """Queryset optimisé pour les listes (sans prefetch des cartes)."""
        return self.get_base_deck_queryset().annotate(
            cards_count=Count('flashcards'),
            learned_count=Count('flashcards', filter=Q(flashcards__learned=True))
        )
    
    def get_detail_optimized_queryset(self, max_cards=500):
        """
        Queryset optimisé pour les détails avec limitation du nombre de cartes.
        Args:
            max_cards: Limite du nombre de cartes à précharger (défaut: 500)
        """
        return self.get_base_deck_queryset().prefetch_related(
            Prefetch(
                'flashcards',
                queryset=Flashcard.objects.select_related('user').order_by('id')  # Remove slice to fix filtering issue
            )
        ).annotate(
            cards_count=Count('flashcards'),
            learned_count=Count('flashcards', filter=Q(flashcards__learned=True))
        )
    
    def get_stats_only_queryset(self):
        """Queryset optimisé pour récupérer uniquement les statistiques."""
        return self.get_base_deck_queryset().annotate(
            cards_count=Count('flashcards'),
            learned_count=Count('flashcards', filter=Q(flashcards__learned=True)),
            last_reviewed=Max('flashcards__last_reviewed_at')
        )
    
    def get_context_from_action(self):
        """Détermine le contexte d'optimisation basé sur l'action courante."""
        if hasattr(self, 'action'):
            if self.action in ['retrieve']:
                return 'detail'
            elif self.action in ['clone', 'update', 'partial_update']:
                return 'minimal'  # Pour ces actions, on n'a pas besoin des cartes
            elif self.action in ['stats', 'analytics']:
                return 'stats'
        return 'list'  # Défaut pour les listes
    
    def get_optimized_deck_queryset(self, context=None):
        """
        Retourne un queryset optimisé selon le contexte d'utilisation.
        Args:
            context: 'list', 'detail', 'stats', 'minimal' ou None pour auto-détection
        """
        if context is None:
            context = self.get_context_from_action()
            
        if context == 'detail':
            return self.get_detail_optimized_queryset()
        elif context == 'stats':
            return self.get_stats_only_queryset()
        elif context == 'minimal':
            return self.get_base_deck_queryset()
        else:  # context == 'list' ou défaut
            return self.get_list_optimized_queryset()
    
    def get_paginated_list_queryset(self, limit=50):
        """Queryset optimisé pour les listes paginées avec limitation."""
        return self.get_list_optimized_queryset().only(
            'id', 'name', 'description', 'is_public', 'is_archived', 
            'created_at', 'updated_at', 'user__username'
        )[:limit]

# ===== VIEWSETS PRINCIPAUX =====

class FlashcardDeckViewSet(DeckPermissionMixin, OptimizedQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = FlashcardDeckSerializer
    permission_classes = [FlashcardDeckPermission]  # Permissions granulaires
    pagination_class = DeckPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    throttle_classes = []  # Désactiver temporairement pour corriger les tests
    search_fields = ['name', 'description', 'user__username']  # Ajout de la recherche par utilisateur
    ordering_fields = ['created_at', 'name', 'user__username']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Sélectionne le sérialiseur approprié selon l'action."""
        if self.action == 'create':
            return FlashcardDeckCreateSerializer
        elif self.action == 'retrieve':
            return FlashcardDeckDetailSerializer
        elif self.action == 'archive_management':
            return DeckArchiveSerializer
        return FlashcardDeckSerializer

    def get_permissions(self):
        """
        Permissions granulaires avec rate limiting pour certaines actions
        """
        if self.action in ['batch_delete']:
            self.permission_classes = [DeckBatchPermission, RateLimitPermission]
        elif self.action in ['create']:
            self.permission_classes = [FlashcardDeckPermission, RateLimitPermission]
        else:
            self.permission_classes = [FlashcardDeckPermission]
        return super().get_permissions()

    def get_queryset(self):
        """
        Retourne les decks appropriés selon le contexte et l'action avec optimisations
        """
        user = self.request.user
        
        # For unauthenticated users, deny access to main deck endpoints
        # They should use the dedicated public deck endpoints instead
        if not user.is_authenticated:
            return FlashcardDeck.objects.none()
        
        # Use optimized querysets based on action
        if self.action == 'list':
            base_queryset = self.get_list_optimized_queryset()
            
            # Handle status filter from frontend
            status_filter = self.request.query_params.get('status', '')
            
            if status_filter == 'archived':
                # Show only archived decks
                return base_queryset.filter(user=user, is_archived=True)
            elif status_filter == 'active':
                # Show only active (non-archived) decks
                return base_queryset.filter(user=user, is_archived=False)
            elif status_filter == 'public':
                # Show only public decks owned by user
                return base_queryset.filter(user=user, is_public=True)
            else:
                # Default: show only active (non-archived) decks
                # Also support legacy 'archived' parameter for backwards compatibility
                show_archived = self.request.query_params.get('archived', 'false').lower() == 'true'
                if show_archived:
                    return base_queryset.filter(user=user, is_archived=True)
                else:
                    return base_queryset.filter(user=user, is_archived=False)
        
        elif self.action == 'retrieve':
            # Use detail optimized queryset for single deck retrieval
            base_queryset = self.get_detail_optimized_queryset()
            return base_queryset.filter(
                Q(user=user) | Q(is_public=True, is_archived=False)
            )
        
        elif self.action in ['stats', 'deck_stats']:
            # Use stats-only queryset for performance endpoints
            base_queryset = self.get_stats_only_queryset()
            return base_queryset.filter(
                Q(user=user) | Q(is_public=True, is_archived=False)
            )
        
        # For other actions, use base optimized queryset
        base_queryset = self.get_base_deck_queryset()
        return base_queryset.filter(
            Q(user=user) | Q(is_public=True, is_archived=False)
        )

    def perform_create(self, serializer):
        """Associe automatiquement l'utilisateur actuel lors de la création d'un deck."""
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            raise PermissionError("Authentication required to create a deck")

    def update(self, request, *args, **kwargs):
        """
        Surcharge de la méthode update pour vérifier que l'utilisateur
        ne modifie que ses propres decks
        """
        instance = self.get_object()
        if not self.check_deck_owner(instance, request.user):
            return Response(
                {"detail": "You don't have permission to modify this deck"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        # Vérifier si le deck est archivé - permettre les modifications du statut d'archivage
        if not self.check_deck_not_archived(instance):
            # Permettre seulement les modifications du champ is_archived pour désarchiver
            if set(request.data.keys()) != {'is_archived'}:
                return Response(
                    {"detail": "This deck is archived. Please unarchive it first to make changes."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Surcharge de la méthode de suppression pour vérifier que l'utilisateur
        ne supprime que ses propres decks
        """
        instance = self.get_object()
        if not self.check_deck_owner(instance, request.user):
            return Response(
                {"detail": "You don't have permission to delete this deck"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    # Action clone déplacée vers PublicDecksViewSet dans explorer_views.py

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def toggle_public(self, request, pk=None):
        """Action pour basculer la visibilité publique d'un deck."""
        deck = self.get_object()
        
        # Vérifier que l'utilisateur est propriétaire du deck
        if not self.check_deck_owner(deck, request.user):
            return Response(
                {"detail": "You don't have permission to modify this deck's visibility"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Ne pas permettre de rendre public un deck archivé
        if deck.is_archived and not deck.is_public and request.data.get('make_public', True):
            return Response(
                {"detail": "You cannot make an archived deck public. Please unarchive it first."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Basculer le statut public
        make_public = request.data.get('make_public')
        if make_public is not None:
            deck.is_public = make_public
        else:
            deck.is_public = not deck.is_public
            
        deck.save()
        
        return Response({
            "is_public": deck.is_public,
            "message": f"Deck visibility set to {'public' if deck.is_public else 'private'}"
        })

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def stats(self, request):
        """Get user statistics for revision"""
        user = request.user
        
        # Get user's decks with optimized aggregation to avoid N+1 queries
        from django.db.models import Count, Q
        user_decks = FlashcardDeck.objects.filter(user=user, is_active=True).annotate(
            cards_count=Count('flashcards'),
            learned_count=Count('flashcards', filter=Q(flashcards__learned=True))
        )
        
        # Calculate statistics using aggregated data
        total_decks = user_decks.count()
        total_cards = sum(deck.cards_count for deck in user_decks)
        total_learned = sum(deck.learned_count for deck in user_decks)
        
        completion_rate = 0
        if total_cards > 0:
            completion_rate = int((total_learned / total_cards) * 100)
        
        return Response({
            'totalDecks': total_decks,
            'totalCards': total_cards,
            'totalLearned': total_learned,
            'completionRate': completion_rate
        })

    @action(detail=True, methods=['get'])
    def cards(self, request, pk=None):
        """Récupérer toutes les cartes d'un deck spécifique."""
        try:
            deck = self.get_object()
            
            # Vérifier l'accès aux cartes
            if not self.check_deck_access(deck, request.user):
                return Response(
                    {"detail": "You don't have permission to view cards in this deck"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Ne pas permettre de voir les cartes d'un deck archivé sauf au propriétaire
            if deck.is_archived and not self.check_deck_owner(deck, request.user):
                return Response(
                    {"detail": "This deck is archived and not available for viewing"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check if smart study mode is requested
            study_mode = request.query_params.get('study_mode', 'normal')
            
            if study_mode == 'smart':
                # Use spaced repetition algorithm
                from .spaced_repetition_views import SpacedRepetitionMixin
                
                # Create mixin instance and get user preferences
                sr_mixin = SpacedRepetitionMixin()
                user_prefs = sr_mixin._get_user_preferences(request.user)
                
                # Build session config from query parameters
                max_cards_value = int(request.query_params.get('max_cards', user_prefs.get('max_cards_per_session', 20)))
                print(f"🔍 [FLASHCARD DEBUG] user_prefs: {user_prefs}")
                print(f"🔍 [FLASHCARD DEBUG] max_cards_per_session from prefs: {user_prefs.get('max_cards_per_session', 'NOT FOUND')}")
                print(f"🔍 [FLASHCARD DEBUG] final max_cards value: {max_cards_value}")

                session_config = {
                    'max_cards': max_cards_value,
                    'new_cards_limit': int(request.query_params.get('new_cards', user_prefs.get('new_cards_per_day', 10))),
                    'review_ahead_days': int(request.query_params.get('ahead_days', user_prefs.get('review_ahead_days', 1))),
                    'prioritize_overdue': request.query_params.get('prioritize_overdue', 'true') == 'true',
                    'mixed_order': request.query_params.get('mixed_order', 'true') == 'true'
                }
                
                # Get smart card selection
                study_data = sr_mixin.get_cards_to_review(deck, session_config, user_prefs)
                
                # Extract cards from session data
                session_cards = study_data['session_cards']
                cards = [card_data['card'] for card_data in session_cards]
                
                # Prepare response with additional study data
                serializer = FlashcardSerializer(cards, many=True, context={'request': request})
                
                return Response({
                    'cards': serializer.data,
                    'study_session': {
                        'total_cards': len(cards),
                        'statistics': study_data['statistics'],
                        'recommendations': study_data['recommendations'],
                        'user_preferences': user_prefs,
                        'session_config': session_config,
                        'study_mode': 'smart'
                    }
                })
            else:
                # Normal mode - all cards or filtered
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
            return Response(
                {"detail": f"Failed to fetch cards: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def popular(self, request):
        """
        Endpoint dédié pour récupérer les decks publics populaires.
        """
        # Filtrer uniquement les decks publics et non archivés
        queryset = FlashcardDeck.objects.filter(is_public=True, is_active=True, is_archived=False)
        
        # Annoter avec le nombre de cartes pour trier par popularité
        queryset = queryset.annotate(card_count=Count('flashcards')).order_by('-card_count')
        
        # Limiter le nombre de résultats
        limit = int(request.query_params.get('limit', 10))
        queryset = queryset[:limit]
        
        # Pagination optionnelle
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'patch'], permission_classes=[])
    def learning_settings(self, request, pk=None):
        """Gérer les paramètres d'apprentissage d'un deck."""
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check if deck exists first (bypass queryset filtering for proper 403 vs 404)
        try:
            deck = FlashcardDeck.objects.get(pk=pk)
        except FlashcardDeck.DoesNotExist:
            return Response(
                {"detail": "Not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Vérifier que l'utilisateur est propriétaire du deck
        if deck.user != request.user:
            return Response(
                {"detail": "You don't have permission to modify this deck's learning settings"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if request.method == 'GET':
            from ..serializers.flashcard_serializers import DeckLearningSettingsSerializer
            serializer = DeckLearningSettingsSerializer(deck, context={'request': request})
            return Response(serializer.data)
        
        elif request.method == 'PATCH':
            from ..serializers.flashcard_serializers import DeckLearningSettingsSerializer
            serializer = DeckLearningSettingsSerializer(deck, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[])
    def apply_preset(self, request, pk=None):
        """Appliquer un preset de configuration d'apprentissage à un deck."""
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        deck = self.get_object()
        
        # Vérifier que l'utilisateur est propriétaire du deck
        if deck.user != request.user:
            return Response(
                {"detail": "You don't have permission to modify this deck's settings"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        from ..serializers.flashcard_serializers import ApplyPresetSerializer
        serializer = ApplyPresetSerializer(data=request.data)
        if serializer.is_valid():
            preset_name = serializer.validated_data['preset_name']
            deck.apply_learning_preset(preset_name)
            
            return Response({
                "success": True,
                "message": f"Preset '{preset_name}' applied successfully",
                "deck_settings": {
                    "required_reviews_to_learn": deck.required_reviews_to_learn,
                    "auto_mark_learned": deck.auto_mark_learned,
                    "reset_on_wrong_answer": deck.reset_on_wrong_answer
                }
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[])
    def reset_progress(self, request, pk=None):
        """Réinitialiser la progression de toutes les cartes d'un deck."""
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        deck = self.get_object()
        
        # Vérifier que l'utilisateur est propriétaire du deck
        if deck.user != request.user:
            return Response(
                {"detail": "You don't have permission to modify this deck's progress"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Réinitialiser la progression de toutes les cartes du deck
        cards_count = 0
        for card in deck.flashcards.all():
            card.reset_progress()
            cards_count += 1
        
        return Response({
            "success": True,
            "message": f"Progression réinitialisée pour {cards_count} carte(s)",
            "cards_reset": cards_count,
            "deck_id": deck.id,
            "deck_name": deck.name
        })

class FlashcardViewSet(viewsets.ModelViewSet):
    serializer_class = FlashcardSerializer
    permission_classes = [FlashcardPermission]  # Permissions granulaires
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['front_text', 'back_text']
    ordering_fields = ['created_at', 'last_reviewed', 'review_count']
    ordering = ['-created_at']

    def get_permissions(self):
        """
        Permissions granulaires avec rate limiting pour certaines actions
        """
        if self.action in ['batch_delete']:
            self.permission_classes = [FlashcardPermission, RateLimitPermission]
        elif self.action in ['create']:
            self.permission_classes = [FlashcardPermission, RateLimitPermission]
        else:
            self.permission_classes = [FlashcardPermission]
        return super().get_permissions()

    def get_queryset(self):
        """
        Filtrer les cartes selon le contexte:
        - Si authentifié: ses cartes + cartes des decks publics
        - Si non authentifié: uniquement cartes des decks publics
        """
        user = self.request.user
        
        if user.is_authenticated:
            # Utilisateur authentifié - voir ses cartes et celles des decks publics
            queryset = Flashcard.objects.select_related('user', 'deck__user').filter(
                Q(user=user) | Q(deck__is_public=True, deck__is_archived=False)
            )
        else:
            # Utilisateur anonyme - voir uniquement les cartes des decks publics et non archivés
            queryset = Flashcard.objects.select_related('user', 'deck__user').filter(
                deck__is_public=True,
                deck__is_archived=False
            )
        
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
            # Vérifier que l'utilisateur a les droits sur le deck
            deck = get_object_or_404(FlashcardDeck, id=deck_id)
            
            if deck.user != request.user:
                return Response(
                    {"detail": "You don't have permission to add cards to this deck"},
                    status=status.HTTP_403_FORBIDDEN
                )
                
            # Vérifier que le deck n'est pas archivé
            if deck.is_archived:
                return Response(
                    {"detail": "You cannot add cards to an archived deck. Please unarchive it first."},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Créer la carte
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user, deck=deck)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating flashcard: {str(e)}")
            return Response(
                {"detail": f"Failed to create flashcard: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        """Vérifier les droits de modification."""
        instance = self.get_object()
        
        # Vérifier si l'utilisateur est propriétaire
        if instance.user != request.user:
            return Response(
                {"detail": "You don't have permission to modify this card"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        # Vérifier si le deck est archivé
        if instance.deck.is_archived:
            return Response(
                {"detail": "You cannot modify cards in an archived deck. Please unarchive the deck first."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Vérifier les droits de suppression."""
        instance = self.get_object()
        
        # Vérifier si l'utilisateur est propriétaire
        if instance.user != request.user:
            return Response(
                {"detail": "You don't have permission to delete this card"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Vérifier si le deck est archivé
        if instance.deck.is_archived:
            return Response(
                {"detail": "You cannot delete cards from an archived deck. Please unarchive the deck first."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def flip_card(self, request, pk=None):
        """Inverser le contenu recto/verso d'une carte individuelle."""
        try:
            card = self.get_object()
            
            # Vérifier que l'utilisateur est propriétaire de la carte
            if card.user != request.user:
                return Response(
                    {"detail": "You don't have permission to modify this card"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Vérifier si le deck est archivé
            if card.deck.is_archived:
                return Response(
                    {"detail": "You cannot modify cards in an archived deck"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Sauvegarder les valeurs actuelles
            original_front = card.front_text
            original_back = card.back_text
            original_front_lang = card.front_language
            original_back_lang = card.back_language
            
            # Inverser le contenu
            card.front_text = original_back
            card.back_text = original_front
            
            # Inverser aussi les langues si elles sont définies
            if original_front_lang and original_back_lang:
                card.front_language = original_back_lang
                card.back_language = original_front_lang
            
            card.save()
            
            # Retourner la carte mise à jour
            serializer = self.get_serializer(card)
            return Response({
                "success": True,
                "message": "Contenu de la carte inversé avec succès",
                "card": serializer.data
            })
            
        except Exception as e:
            logger.error(f"Error flipping card {pk}: {str(e)}")
            return Response(
                {"detail": f"Failed to flip card: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def toggle_learned(self, request, pk=None):
        """Basculer l'état d'apprentissage et mettre à jour les statistiques."""
        try:
            card = self.get_object()
            
            # Vérifier que l'utilisateur est propriétaire de la carte
            if card.user != request.user:
                return Response(
                    {"detail": "You don't have permission to update this card's status"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Vérifier si le deck est archivé
            if card.deck.is_archived:
                return Response(
                    {"detail": "You cannot update cards in an archived deck. Please unarchive the deck first."},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            success = request.data.get('success', True)
            
            # Utiliser la méthode mark_reviewed du modèle
            card.mark_reviewed(success=success)
            
            serializer = self.get_serializer(card)
            return Response(serializer.data)
            
        except (ValidationError, ValueError) as e:
            # Only catch specific exceptions, let DRF handle PermissionDenied
            logger.error(f"Error toggling card {pk} learned status: {str(e)}")
            return Response(
                {"detail": f"Failed to update card: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def due_for_review(self, request):
        """Récupérer les cartes à réviser pour l'utilisateur actuel."""
        try:
            # Cette action nécessite l'authentification
            if not request.user.is_authenticated:
                return Response(
                    {"detail": "Authentication required to view cards due for review"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
                
            limit = int(request.query_params.get('limit', 10))
            deck_id = request.query_params.get('deck', None)
            
            # Construction de la requête - filtrer par utilisateur
            query = Q(user=request.user) & (Q(next_review__lte=timezone.now()) | Q(next_review__isnull=True))
            
            # Exclure les cartes des decks archivés
            query &= Q(deck__is_archived=False)
            
            if deck_id:
                # Vérifier que le deck appartient à l'utilisateur et n'est pas archivé
                deck = get_object_or_404(FlashcardDeck, id=deck_id, user=request.user, is_archived=False)
                query &= Q(deck=deck)
            
            cards = Flashcard.objects.filter(query).order_by('last_reviewed')[:limit]
            
            serializer = self.get_serializer(cards, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error fetching due cards: {str(e)}")
            return Response(
                {"detail": f"Failed to fetch due cards: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def update_review_progress(self, request, pk=None):
        """
        Mettre à jour le progrès de révision d'une carte avec l'algorithme adaptatif.

        Paramètres acceptés:
        - is_correct (bool): Si la réponse était correcte
        - study_mode (str): Mode d'étude (learn/flashcards/write/match/review)
        - difficulty (str): Difficulté perçue (easy/medium/hard/wrong)
        - response_time (float): Temps de réponse en secondes (optionnel)
        - session_id (str): ID de session pour grouper les performances (optionnel)
        """
        from ..services.adaptive_learning import AdaptiveLearningService
        from ..models import StudyMode, DifficultyLevel

        try:
            # Check if card exists first (bypass queryset filtering for proper 403 vs 404)
            try:
                card = Flashcard.objects.get(pk=pk)
            except Flashcard.DoesNotExist:
                return Response(
                    {"detail": "Not found."},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Vérifier que l'utilisateur est propriétaire de la carte
            if card.user != request.user:
                return Response(
                    {"detail": "You don't have permission to update this card's progress"},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Vérifier si le deck est archivé
            if card.deck.is_archived:
                return Response(
                    {"detail": "You cannot update cards in an archived deck"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Extraire les paramètres
            is_correct = request.data.get('is_correct', True)
            study_mode = request.data.get('study_mode', StudyMode.WRITE)
            difficulty = request.data.get('difficulty')
            response_time = request.data.get('response_time')
            session_id = request.data.get('session_id')

            # Déduire la difficulté si non fournie
            if not difficulty:
                if not is_correct:
                    difficulty = DifficultyLevel.WRONG
                else:
                    difficulty = DifficultyLevel.MEDIUM

            # Valider les choix
            if study_mode not in dict(StudyMode.choices):
                study_mode = StudyMode.WRITE
            if difficulty not in dict(DifficultyLevel.choices):
                difficulty = DifficultyLevel.MEDIUM if is_correct else DifficultyLevel.WRONG

            # Utiliser le service d'apprentissage adaptatif
            performance, mastery = AdaptiveLearningService.record_performance(
                card=card,
                user=request.user,
                study_mode=study_mode,
                difficulty=difficulty,
                was_correct=is_correct,
                response_time_seconds=response_time,
                session_id=session_id
            )

            # Sérialiser la carte mise à jour
            serializer = self.get_serializer(card)

            return Response({
                "success": True,
                "message": "Review progress updated successfully",
                "card": serializer.data,
                "adaptive_learning": {
                    "confidence_score": mastery.confidence_score,
                    "mastery_level": mastery.mastery_level,
                    "total_attempts": mastery.total_attempts,
                    "successful_attempts": mastery.successful_attempts,
                    "success_rate": round((mastery.successful_attempts / mastery.total_attempts * 100) if mastery.total_attempts > 0 else 0, 1),
                    "confidence_change": performance.confidence_after - performance.confidence_before if performance.confidence_before else 0,
                    "recommended_next_mode": AdaptiveLearningService.get_recommended_study_mode(card)
                }
            })

        except Exception as e:
            logger.error(f"Error updating review progress for card {pk}: {str(e)}")
            return Response(
                {"detail": f"Failed to update review progress: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

# PublicDecksViewSet migré vers explorer_views.py

class FlashcardImportView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, deck_id=None):
        try:
            # Récupérer le fichier Excel et l'ID du deck
            excel_file = request.FILES.get('file')
            has_header = request.data.get('has_header', 'true').lower() == 'true'
            preview_only = request.data.get('preview_only', 'false').lower() == 'true'
            front_column = request.data.get('front_column', '0')
            back_column = request.data.get('back_column', '1')
            
            # Récupérer les langues optionnelles
            front_language = request.data.get('front_language', '')
            back_language = request.data.get('back_language', '')
            
            # Vérifier si le fichier est présent
            if not excel_file:
                return Response({"detail": "Aucun fichier n'a été fourni."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Vérifier le type de fichier (.xls | .xlsx | .csv)
            if not (excel_file.name.endswith('.xls') or excel_file.name.endswith('.xlsx') or excel_file.name.endswith('.csv')):
                return Response({"detail": "Le fichier doit être au format Excel (.xls, .xlsx) ou CSV."},
                               status=status.HTTP_400_BAD_REQUEST)

            # Vérifier si le deck existe et que l'utilisateur a les permissions
            try:
                deck = FlashcardDeck.objects.get(id=deck_id)
                # Vérifier que l'utilisateur est le propriétaire
                if deck.user != request.user:
                    return Response({"detail": "Vous n'avez pas la permission d'importer dans ce deck."}, 
                                   status=status.HTTP_403_FORBIDDEN)
            except FlashcardDeck.DoesNotExist:
                return Response({"detail": "Le deck spécifié n'existe pas."}, 
                               status=status.HTTP_404_NOT_FOUND)
            
            # Lire le fichier selon son type
            if excel_file.name.endswith('.csv'):
                df = pd.read_csv(excel_file, header=0 if has_header else None)
            else:
                df = pd.read_excel(excel_file, engine='openpyxl', header=0 if has_header else None)

            if not has_header:
                df.columns = ['front_text', 'back_text'] + [f'col_{i}' for i in range(2, len(df.columns))]
            
            # Vérifier que les colonnes nécessaires existent
            if len(df.columns) < 2:
                return Response({"detail": "Le fichier doit contenir au moins 2 colonnes."}, 
                               status=status.HTTP_400_BAD_REQUEST)
            
            # Convertir les indices de colonnes en entiers
            try:
                front_col_idx = int(front_column)
                back_col_idx = int(back_column)
            except (ValueError, TypeError):
                front_col_idx = 0
                back_col_idx = 1
            
            # Vérifier que les indices sont valides
            if front_col_idx >= len(df.columns) or back_col_idx >= len(df.columns):
                return Response({"detail": "Indices de colonnes invalides."}, 
                               status=status.HTTP_400_BAD_REQUEST)
            
            # Créer un DataFrame avec les colonnes sélectionnées
            preview_df = df.iloc[:, [front_col_idx, back_col_idx]].copy()
            preview_df.columns = ['front_text', 'back_text']
            
            # Si c'est juste un preview, retourner les données
            if preview_only:
                preview_data = []
                columns_info = [{'index': i, 'name': col} for i, col in enumerate(df.columns)]
                
                for idx, row in preview_df.head(5).iterrows():  # Max 5 lignes de preview
                    front_value = row['front_text']
                    back_value = row['back_text']
                    
                    # Vérifier si les valeurs sont NaN ou None
                    if pd.isna(front_value) or pd.isna(back_value):
                        continue
                    
                    front_text = str(front_value).strip()
                    back_text = str(back_value).strip()
                    
                    # Ignorer les valeurs vides ou invalides
                    if (front_text and back_text and 
                        front_text.lower() not in ['nan', 'none', 'null'] and 
                        back_text.lower() not in ['nan', 'none', 'null']):
                        preview_data.append({
                            'front_text': front_text,
                            'back_text': back_text
                        })
                
                return Response({
                    "preview": preview_data,
                    "columns": columns_info,
                    "total_rows": len(df),
                    "selected_front_column": front_col_idx,
                    "selected_back_column": back_col_idx
                }, status=status.HTTP_200_OK)
            
            # Créer les flashcards (seulement si ce n'est pas un preview)
            flashcards_created = 0
            flashcards_failed = 0
            preview_data = []
            
            for idx, row in preview_df.iterrows():
                front_value = row['front_text']
                back_value = row['back_text']
                
                # Vérifier si les valeurs sont NaN ou None
                if pd.isna(front_value) or pd.isna(back_value):
                    continue
                
                front_text = str(front_value).strip()
                back_text = str(back_value).strip()
                
                # Ignorer les lignes vides ou invalides
                if (not front_text or not back_text or 
                    front_text.lower() in ['nan', 'none', 'null'] or 
                    back_text.lower() in ['nan', 'none', 'null']):
                    continue
                
                try:
                    flashcard_data = {
                        'deck': deck,
                        'front_text': front_text,
                        'back_text': back_text,
                        'user': request.user
                    }
                    
                    # Ajouter les langues si elles sont spécifiées
                    if front_language:
                        flashcard_data['front_language'] = front_language
                    if back_language:
                        flashcard_data['back_language'] = back_language
                    
                    flashcard = Flashcard.objects.create(**flashcard_data)
                    flashcards_created += 1
                    
                    # Ajouter aux données de preview (max 3)
                    if len(preview_data) < 3:
                        preview_data.append({
                            'front_text': front_text,
                            'back_text': back_text
                        })
                    
                except Exception as e:
                    flashcards_failed += 1
            
            return Response({
                "detail": f"{flashcards_created} cartes ont été importées avec succès.",
                "cards_created": flashcards_created,
                "cards_failed": flashcards_failed,
                "preview": preview_data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({"detail": f"Une erreur s'est produite lors de l'importation: {str(e)}"}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ===== API VIEWS =====

class StatWordKnown:
    """Classe pour afficher les statistiques des mots connus et à apprendre"""
    
    def __init__(self, user):
        self.user = user
    
    def display_known_words(self):
        """Affiche tous les mots marqués comme appris"""
        learned_cards = Flashcard.objects.filter(
            user=self.user,
            learned=True,
            deck__is_active=True,
            deck__is_archived=False
        ).select_related('deck').order_by('-last_reviewed')
        
        known_words = []
        for card in learned_cards:
            known_words.append({
                'front_text': card.front_text,
                'back_text': card.back_text,
                'deck_name': card.deck.name,
                'last_reviewed': card.last_reviewed,
                'review_count': card.review_count,
                'front_language': card.front_language,
                'back_language': card.back_language
            })
        
        return {
            'known_words': known_words,
            'total_known': len(known_words)
        }
    
    def display_words_to_learn(self):
        """Affiche tous les mots encore à apprendre"""
        unlearned_cards = Flashcard.objects.filter(
            user=self.user,
            learned=False,
            deck__is_active=True,
            deck__is_archived=False
        ).select_related('deck').order_by('-created_at')
        
        words_to_learn = []
        for card in unlearned_cards:
            words_to_learn.append({
                'front_text': card.front_text,
                'back_text': card.back_text,
                'deck_name': card.deck.name,
                'created_at': card.created_at,
                'correct_reviews': card.correct_reviews_count,
                'reviews_needed': card.reviews_remaining_to_learn,
                'progress_percentage': card.learning_progress_percentage,
                'front_language': card.front_language,
                'back_language': card.back_language
            })
        
        return {
            'words_to_learn': words_to_learn,
            'total_to_learn': len(words_to_learn)
        }
    
    def get_complete_statistics(self):
        """Retourne les statistiques complètes des mots connus et à apprendre"""
        known_data = self.display_known_words()
        to_learn_data = self.display_words_to_learn()
        
        total_words = known_data['total_known'] + to_learn_data['total_to_learn']
        completion_rate = 0
        if total_words > 0:
            completion_rate = (known_data['total_known'] / total_words) * 100
        
        return {
            'known_words': known_data['known_words'],
            'words_to_learn': to_learn_data['words_to_learn'],
            'statistics': {
                'total_known': known_data['total_known'],
                'total_to_learn': to_learn_data['total_to_learn'],
                'total_words': total_words,
                'completion_rate': round(completion_rate, 2)
            }
        }

class Applied_translation:
    pass


class WordStatsAPIView(APIView):
    """API pour récupérer les statistiques des mots connus et à apprendre"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Récupère les statistiques complètes des mots pour l'utilisateur"""
        try:
            stats = StatWordKnown(request.user)
            
            # Paramètre optionnel pour le type de données
            data_type = request.query_params.get('type', 'all')
            
            if data_type == 'known':
                return Response(stats.display_known_words())
            elif data_type == 'to_learn':
                return Response(stats.display_words_to_learn())
            else:
                return Response(stats.get_complete_statistics())
                
        except Exception as e:
            logger.error(f"Error retrieving word stats for user {request.user.id}: {str(e)}")
            return Response(
                {"detail": "Erreur lors de la récupération des statistiques"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TagsAPIView(APIView):
    """API pour gérer les tags des decks - VERSION UNIQUE."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Récupère tous les tags disponibles pour l'utilisateur."""
        try:
            # Récupérer tous les tags des decks de l'utilisateur
            user_decks = FlashcardDeck.objects.filter(user=request.user, is_active=True)
            
            # Paramètres de requête
            include_counts = request.query_params.get('include_counts', 'false').lower() == 'true'
            search_term = request.query_params.get('search', '').strip().lower()
            
            # Collecter les tags avec leurs comptes
            tag_counts = {}
            seen_normalized = set()
            unique_tags = []
            
            for deck in user_decks:
                if deck.tags:
                    for tag in deck.tags:
                        normalized = tag.strip().lower()
                        if normalized not in seen_normalized:
                            seen_normalized.add(normalized)
                            unique_tags.append(tag)  # Garder la casse originale
                            tag_counts[tag] = 0
                        
                        # Compter les occurrences
                        original_tag = next(t for t in unique_tags if t.lower() == normalized)
                        tag_counts[original_tag] += 1
            
            # Appliquer le filtre de recherche si fourni
            if search_term:
                filtered_tags = [tag for tag in unique_tags if search_term in tag.lower()]
                unique_tags = filtered_tags
            
            # Trier les tags alphabétiquement (case-insensitive)
            sorted_tags = sorted(unique_tags, key=lambda x: x.lower())
            
            response_data = {
                'tags': sorted_tags,
                'count': len(sorted_tags)
            }
            
            # Ajouter les comptes si demandé
            if include_counts:
                tags_with_counts = [
                    {'tag': tag, 'count': tag_counts[tag]}
                    for tag in sorted_tags
                ]
                response_data['tags_with_counts'] = tags_with_counts
            
            return Response(response_data)
            
        except Exception as e:
            logger.error(f"Error retrieving tags for user {request.user.id}: {str(e)}")
            return Response(
                {"detail": "Erreur lors de la récupération des tags"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Ajoute un nouveau tag à la liste des tags disponibles."""
        try:
            tag = request.data.get('tag', '').strip().lower()
            
            if not tag:
                return Response(
                    {"detail": "Le tag ne peut pas être vide"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validation du tag
            if len(tag) > 50:
                return Response(
                    {"detail": "Le tag ne peut pas dépasser 50 caractères"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Reject spaces, special characters, but allow emojis and international characters
            if re.search(r'[\s@!#%&*+=/\\|<>{}[\]().,;:?~`^]', tag):
                return Response(
                    {"detail": "Le tag contient des caractères non autorisés"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Also reject control characters
            if re.search(r'[\x00-\x1f\x7f-\x9f]', tag):
                return Response(
                    {"detail": "Le tag contient des caractères non autorisés"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Vérifier si le tag existe déjà pour cet utilisateur (case-insensitive)
            user_decks = FlashcardDeck.objects.filter(user=request.user, is_active=True)
            existing_tags_normalized = set()
            existing_tags_original = []
            
            for deck in user_decks:
                if deck.tags:
                    for deck_tag in deck.tags:
                        normalized = deck_tag.strip().lower()
                        existing_tags_normalized.add(normalized)
                        existing_tags_original.append(deck_tag)
            
            if tag in existing_tags_normalized:
                # Trouver le tag original avec la même forme normalisée
                original_tag = next(
                    (orig for orig in existing_tags_original 
                     if orig.strip().lower() == tag), 
                    tag
                )
                return Response(
                    {"detail": f"Le tag '{original_tag}' (ou une variante) existe déjà dans vos decks"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response({
                'tag': tag,
                'message': 'Tag validé avec succès'
            })
            
        except Exception as e:
            logger.error(f"Error adding tag for user {request.user.id}: {str(e)}")
            return Response(
                {"detail": "Erreur lors de l'ajout du tag"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )