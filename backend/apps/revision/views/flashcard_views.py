# backend/revision/views/flashcard_views.py
from django.utils import timezone
from django.db.models import Q, Count, Prefetch
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

import logging
logger = logging.getLogger(__name__)

class DeckPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class FlashcardDeckViewSet(viewsets.ModelViewSet):
    serializer_class = FlashcardDeckSerializer
    permission_classes = [FlashcardDeckPermission]  # Permissions granulaires
    pagination_class = DeckPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
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

    def _get_optimized_queryset(self):
        """
        Retourne un queryset optimisé avec les relations préchargées et les annotations
        pour éviter les requêtes N+1
        """
        return FlashcardDeck.objects.select_related('user').prefetch_related(
            Prefetch(
                'flashcards',
                queryset=Flashcard.objects.select_related('user')
            )
        ).annotate(
            cards_count=Count('flashcards'),
            learned_count=Count('flashcards', filter=Q(flashcards__learned=True))
        )

    def get_queryset(self):
        """
        Retourne les decks appropriés selon le contexte
        """
        user = self.request.user
        # Handle public_access parameter for direct access to a public deck
        public_access = self.request.query_params.get('public_access', '').lower() == 'true'
        
        # If requesting a specific deck with public_access=true
        if public_access:
            # Return both public decks and user's own decks (if authenticated)
            if user.is_authenticated:
                return self._get_optimized_queryset().filter(
                    Q(is_public=True, is_archived=False) | Q(user=user)
                )
            else:
                # For anonymous users, only return public decks
                return self._get_optimized_queryset().filter(
                    is_public=True, 
                    is_archived=False
                )
        
        # If user is not authenticated, return empty queryset for personal space
        if not user.is_authenticated:
            return FlashcardDeck.objects.none()
        # Paramètres de requête
        show_public = self.request.query_params.get('public', 'false').lower() == 'true'
        show_mine = self.request.query_params.get('mine', 'true').lower() == 'true' and user.is_authenticated
        show_archived = self.request.query_params.get('archived', 'false').lower() == 'true'
        username_filter = self.request.query_params.get('username')
        search_query = self.request.query_params.get('search', '')
        
        logger.debug(f"Query params: public={show_public}, mine={show_mine}, archived={show_archived}, search='{search_query}', user_authenticated={user.is_authenticated}")
        if user.is_authenticated:
            logger.debug(f"User: {user.username}, total decks: {FlashcardDeck.objects.filter(user=user).count()}")
        
        # Cas de base : si aucun filtre n'est spécifié, afficher les cartes de l'utilisateur
        # Important pour l'espace personnel
        if not search_query and not username_filter and not show_public and show_mine and user.is_authenticated:
            # Filtre simple pour espace personnel
            personal_query = Q(user=user, is_active=True)
            if not show_archived:
                personal_query &= Q(is_archived=False)
            queryset = self._get_optimized_queryset().filter(personal_query)
            logger.debug(f"Personal decks query for user {user.username}: {queryset.count()} decks")
            return queryset
        
        # Si recherche ou filtre username
        if search_query or username_filter:
            query = Q(is_active=True)
            
            # Pour l'explorateur, on veut les decks publics
            if show_public:
                query &= Q(is_public=True, is_archived=False)
            
            # Pour les decks perso
            if show_mine and user.is_authenticated:
                user_query = Q(user=user)
                if not show_archived:
                    user_query &= Q(is_archived=False)
                    
                if show_public:
                    query |= user_query
                else:
                    query &= user_query
                    
            # Filtre par username
            if username_filter:
                query &= Q(user__username__icontains=username_filter)
                
            # Recherche textuelle
            if search_query:
                search_filter = Q(name__icontains=search_query) | Q(description__icontains=search_query)
                query &= search_filter
                
            return self._get_optimized_queryset().filter(query).distinct()
        
        # Construction de la requête pour les autres cas
        query = Q(is_active=True)
        
        # Logique pour les decks personnels et publics
        if show_mine and user.is_authenticated:
            personal_filter = Q(user=user)
            if not show_archived:
                personal_filter &= Q(is_archived=False)
                
            if show_public:
                public_filter = Q(is_public=True, is_archived=False)
                if user.is_authenticated:
                    public_filter &= ~Q(user=user)  # Exclure decks perso des publics
                    
                # Combinaison OR entre perso et public
                query &= (personal_filter | public_filter)
            else:
                query &= personal_filter
        elif show_public:
            query &= Q(is_public=True, is_archived=False)
        else:
            # Default fallback: if user is authenticated, show their personal decks
            if user.is_authenticated:
                logger.debug(f"Default fallback: showing personal decks for {user.username}")
                return self._get_optimized_queryset().filter(user=user, is_active=True, is_archived=False)
            else:
                return FlashcardDeck.objects.none()
            
        return self._get_optimized_queryset().filter(query)

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
        if instance.user != request.user:
            return Response(
                {"detail": "You don't have permission to modify this deck"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        # Vérifier si le deck est archivé
        if instance.is_archived:
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
        if instance.user != request.user:
            return Response(
                {"detail": "You don't have permission to delete this deck"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def toggle_public(self, request, pk=None):
        """Action pour basculer la visibilité publique d'un deck."""
        deck = self.get_object()
        
        # Vérifier que l'utilisateur est propriétaire du deck
        if deck.user != request.user:
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

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def archive_management(self, request):
        """
        Endpoint pour gérer l'archivage et la prolongation des decks.
        Permet d'archiver, désarchiver ou prolonger la date d'expiration.
        """
        serializer = DeckArchiveSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            result = serializer.save()
            return Response(result)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def clone(self, request, pk=None):
        """Action pour cloner un deck public"""
        source_deck = self.get_object()
        
        # Journaliser pour le débogage
        logger.debug(f"Tentative de clonage du deck public {pk} par l'utilisateur {request.user.username}")
        logger.debug(f"Données de la requête: {request.data}")
        
        # Vérifier que le deck est public
        if not source_deck.is_public:
            return Response(
                {"detail": "You can only clone public decks"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Créer un nouveau deck pour l'utilisateur
            new_deck = FlashcardDeck.objects.create(
                user=request.user,
                # Fournir des valeurs par défaut pour éviter les erreurs
                name=request.data.get('name') or f"Clone of {source_deck.name}",
                description=request.data.get('description') or f"Cloned from {source_deck.user.username}'s deck: {source_deck.description}",
                is_active=True,
                is_public=False,
                is_archived=False
            )
            
            # Copier toutes les cartes
            cards_created = 0
            for card in source_deck.flashcards.all():
                Flashcard.objects.create(
                    user=request.user,
                    deck=new_deck,
                    front_text=card.front_text,
                    back_text=card.back_text,
                    learned=False,
                    review_count=0
                )
                cards_created += 1
            
            serializer = FlashcardDeckSerializer(new_deck, context={'request': request})
            return Response({
                "message": f"Successfully cloned '{source_deck.name}' with {cards_created} cards",
                "deck": serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Erreur lors du clonage du deck {pk}: {str(e)}")
            return Response(
                {"detail": f"Failed to clone deck: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def stats(self, request):
        """Get user statistics for revision"""
        user = request.user
        
        # Get user's decks
        user_decks = FlashcardDeck.objects.filter(user=user, is_active=True)
        
        # Calculate statistics
        total_decks = user_decks.count()
        total_cards = 0
        total_learned = 0
        
        for deck in user_decks:
            deck_cards = deck.flashcards.count()
            deck_learned = deck.flashcards.filter(learned=True).count()
            total_cards += deck_cards
            total_learned += deck_learned
        
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
            
            # Vérifier l'accès aux cartes - autoriser pour les decks publics
            if not deck.is_public and (not request.user.is_authenticated or deck.user != request.user):
                return Response(
                    {"detail": "You don't have permission to view cards in this deck"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Ne pas permettre de voir les cartes d'un deck archivé sauf au propriétaire
            if deck.is_archived and (not request.user.is_authenticated or deck.user != request.user):
                return Response(
                    {"detail": "This deck is archived and not available for viewing"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
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
        Les decks sont triés par nombre de cartes ou de clones.
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
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def archived(self, request):
        """Récupère tous les decks archivés de l'utilisateur courant."""
        queryset = FlashcardDeck.objects.filter(
            user=request.user, 
            is_archived=True
        ).order_by('expiration_date')
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def expiring_soon(self, request):
        """Récupère les decks qui vont expirer bientôt."""
        # Utiliser la méthode de classe pour trouver les decks à avertir
        queryset = FlashcardDeck.get_decks_needing_warning(user=request.user)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "count": queryset.count(),
            "decks": serializer.data
        })
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def cleanup_expired(self, request):
        """Action pour nettoyer les decks expirés (admin uniquement)."""
        # Vérifier que l'utilisateur est superutilisateur
        if not request.user.is_superuser:
            return Response(
                {"detail": "Only administrators can perform this action"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        # Exécuter le nettoyage
        count = FlashcardDeck.cleanup_expired()
        
        return Response({
            "message": f"Cleanup completed: {count} expired decks deleted",
            "count": count
        })
        
    @action(detail=False, methods=['post'])
    def batch_delete(self, request):
        """Supprimer plusieurs decks en une seule requête avec validation sécurisée."""
        serializer = BatchDeleteSerializer(data=request.data, context={'request': request})
        
        if not serializer.is_valid():
            return Response(
                {"detail": "Données invalides", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            deck_ids = serializer.validated_data['deck_ids']
            
            # Supprimer les decks (permissions déjà vérifiées dans le sérialiseur)
            queryset = FlashcardDeck.objects.filter(
                id__in=deck_ids,
                user=request.user
            )
            
            deleted_count, _ = queryset.delete()
            
            logger.info(f"User {request.user.id} deleted {deleted_count} decks: {deck_ids}")
            
            return Response({
                "message": f"Suppression réussie de {deleted_count} deck(s)",
                "deleted": deleted_count,
                "deck_ids": deck_ids
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error batch deleting decks for user {request.user.id}: {str(e)}")
            return Response(
                {"detail": "Erreur lors de la suppression des decks"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def batch_archive(self, request):
        """Archiver/désarchiver plusieurs decks en une seule requête avec validation sécurisée."""
        serializer = BatchArchiveSerializer(data=request.data, context={'request': request})
        
        if not serializer.is_valid():
            return Response(
                {"detail": "Données invalides", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            deck_ids = serializer.validated_data['deck_ids']
            action_type = serializer.validated_data['action']
            
            # Mettre à jour les decks
            queryset = FlashcardDeck.objects.filter(
                id__in=deck_ids,
                user=request.user
            )
            
            if action_type == 'archive':
                updated_count = 0
                for deck in queryset:
                    deck.archive()
                    updated_count += 1
                message = f"Archivage réussi de {updated_count} deck(s)"
            else:  # unarchive
                updated_count = queryset.update(is_archived=False, expiration_date=None)
                message = f"Désarchivage réussi de {updated_count} deck(s)"
            
            logger.info(f"User {request.user.id} {action_type}d {updated_count} decks: {deck_ids}")
            
            return Response({
                "message": message,
                "updated": updated_count,
                "action": action_type,
                "deck_ids": deck_ids
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error batch {action_type} for user {request.user.id}: {str(e)}")
            return Response(
                {"detail": f"Erreur lors de l'{action_type} des decks"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, *args, **kwargs):
        """
        Récupère un deck spécifique.
        Permet l'accès aux decks publics pour tous les utilisateurs
        """
        try:
            instance = self.get_object()
            
            # Vérification des permissions - autoriser l'accès aux decks publics
            if not instance.is_public and instance.user != request.user:
                return Response(
                    {"detail": "You don't have permission to view this deck"},
                    status=status.HTTP_403_FORBIDDEN
                )
                
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving deck {kwargs.get('pk')}: {str(e)}")
            return Response(
                {"detail": "Erreur lors du chargement du deck"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get', 'patch'], permission_classes=[IsAuthenticated])
    def learning_settings(self, request, pk=None):
        """
        Endpoint pour gérer les paramètres d'apprentissage d'un deck.
        GET: récupère les paramètres actuels
        PATCH: met à jour les paramètres
        """
        deck = self.get_object()
        
        # Vérifier que l'utilisateur est propriétaire du deck
        if deck.user != request.user:
            return Response(
                {"detail": "You don't have permission to modify this deck's learning settings"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if request.method == 'GET':
            serializer = DeckLearningSettingsSerializer(deck, context={'request': request})
            return Response(serializer.data)
        
        elif request.method == 'PATCH':
            serializer = DeckLearningSettingsSerializer(
                deck, 
                data=request.data, 
                partial=True, 
                context={'request': request}
            )
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "Paramètres d'apprentissage mis à jour avec succès",
                    "settings": serializer.data
                })
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def apply_preset(self, request, pk=None):
        """
        Applique un preset de configuration d'apprentissage à un deck.
        """
        deck = self.get_object()
        
        # Vérifier que l'utilisateur est propriétaire du deck
        if deck.user != request.user:
            return Response(
                {"detail": "You don't have permission to modify this deck's learning settings"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ApplyPresetSerializer(data=request.data)
        
        if serializer.is_valid():
            preset_name = serializer.validated_data['preset_name']
            
            # Appliquer le preset
            success = deck.apply_learning_preset(preset_name)
            
            if success:
                # Récupérer les nouveaux paramètres
                settings_serializer = DeckLearningSettingsSerializer(deck, context={'request': request})
                
                return Response({
                    "message": f"Preset '{preset_name}' appliqué avec succès",
                    "preset_applied": preset_name,
                    "settings": settings_serializer.data
                })
            else:
                return Response(
                    {"detail": f"Erreur lors de l'application du preset '{preset_name}'"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def learning_statistics(self, request, pk=None):
        """
        Récupère les statistiques d'apprentissage détaillées d'un deck.
        """
        deck = self.get_object()
        
        # Vérifier que l'utilisateur est propriétaire du deck ou que le deck est public
        if not deck.is_public and deck.user != request.user:
            return Response(
                {"detail": "You don't have permission to view this deck's statistics"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        statistics = deck.get_learning_statistics()
        presets = deck.get_learning_presets()
        
        return Response({
            "deck_id": deck.id,
            "deck_name": deck.name,
            "statistics": statistics,
            "current_settings": {
                "required_reviews_to_learn": deck.required_reviews_to_learn,
                "auto_mark_learned": deck.auto_mark_learned,
                "reset_on_wrong_answer": deck.reset_on_wrong_answer
            },
            "available_presets": presets
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
            
        except Exception as e:
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
    
    @action(detail=False, methods=['get'])
    def ids(self, request):
        """Récupérer uniquement les IDs des flashcards, optionnellement filtrées par deck."""
        try:
            deck_id = request.query_params.get('deck')
            
            # Appliquer les filtres
            queryset = self.get_queryset()
            if deck_id:
                queryset = queryset.filter(deck_id=deck_id)
            
            # Récupérer seulement les IDs pour optimiser les performances
            card_ids = queryset.values_list('id', flat=True)
            
            return Response(list(card_ids))
            
        except Exception as e:
            logger.error(f"Error fetching card IDs: {str(e)}")
            return Response(
                {"detail": f"Failed to fetch card IDs: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def update_review_progress(self, request, pk=None):
        """
        Met à jour le progrès de révision d'une carte selon les paramètres du deck.
        """
        try:
            card = self.get_object()
            
            # Vérifier que l'utilisateur est propriétaire de la carte
            if card.user != request.user:
                return Response(
                    {"detail": "You don't have permission to update this card's progress"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Vérifier si le deck est archivé
            if card.deck.is_archived:
                return Response(
                    {"detail": "You cannot update cards in an archived deck."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Récupérer le paramètre de correction
            is_correct = request.data.get('is_correct', True)
            
            # Mettre à jour le progrès selon les paramètres du deck
            card.update_review_progress(is_correct=is_correct)
            
            # Retourner la carte mise à jour
            serializer = self.get_serializer(card)
            return Response({
                "message": "Progrès de révision mis à jour",
                "card": serializer.data,
                "learning_progress": {
                    "correct_reviews": card.correct_reviews_count,
                    "total_reviews": card.total_reviews_count,
                    "required_reviews": card.deck.required_reviews_to_learn,
                    "progress_percentage": card.learning_progress_percentage,
                    "reviews_remaining": card.reviews_remaining_to_learn,
                    "is_learned": card.learned
                }
            })
            
        except Exception as e:
            logger.error(f"Error updating review progress for card {pk}: {str(e)}")
            return Response(
                {"detail": f"Failed to update review progress: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def batch_delete(self, request):
        """Supprimer plusieurs flashcards en une seule requête."""
        try:
            card_ids = request.data.get('cardIds', [])
            
            if not card_ids:
                return Response(
                    {"detail": "No card IDs provided"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Vérifier que l'utilisateur est autorisé à supprimer ces cartes
            queryset = self.get_queryset().filter(
                id__in=card_ids,
                user=request.user,  # S'assurer que les cartes appartiennent à l'utilisateur
                deck__is_archived=False  # Ne pas permettre la suppression dans les decks archivés
            )
            
            # Stocker le nombre de cartes trouvées
            count = queryset.count()
            
            if count == 0:
                return Response(
                    {"detail": "No accessible cards found with these IDs or cards are in archived decks"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Supprimer les cartes
            deleted_count, _ = queryset.delete()
            
            return Response({
                "message": f"Successfully deleted {deleted_count} cards",
                "deleted": deleted_count
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error batch deleting cards: {str(e)}")
            return Response(
                {"detail": f"Failed to delete cards: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

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
            
            # to read the file taking into account the file type and the presence of a header
            if excel_file.name.endswith('.csv'):
                df = pd.read_csv(excel_file, header=0 if has_header else None)
            else:
                df=pd.read_excel(excel_file, engine='openpyxl', header=0 if has_header else None)

            if not has_header:
                df.columns = ['front_text', 'back_text'] + [f'col_{i}' for i in range(2, len(df.columns))]
            
            preview_data = df.head(5).to_dict(orient='records')
            if request.data.get('preview_only', 'false').lower() == 'true':
                return Response({
                    "preview": preview_data,
                    "total_rows": len(df),
                    "columns": list(df.columns),
                }, status=status.HTTP_200_OK)
            
            # Vérifier que les colonnes nécessaires existent
            required_columns = ['front_text', 'back_text']
            # Si le fichier a des noms de colonnes différents (par exemple 'anglais', 'français'),
            # on peut les mapper automatiquement aux 2 premières colonnes
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
                    front_text = str(row['front_text']).strip()
                    back_text = str(row['back_text']).strip()
                    
                    if front_text and back_text and front_text != 'nan' and back_text != 'nan':
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
                front_text = str(row['front_text']).strip()
                back_text = str(row['back_text']).strip()
                
                # Ignorer les lignes vides
                if not front_text or not back_text or front_text == 'nan' or back_text == 'nan':
                    continue
                
                try:
                    flashcard = Flashcard.objects.create(
                        deck=deck,
                        front_text=front_text,
                        back_text=back_text,
                        user=request.user
                    )
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
        
class PublicDecksViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet spécifique pour explorer les decks publics.
    En lecture seule, ne permet pas de modification.
    """
    serializer_class = FlashcardDeckSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'user__username']
    ordering_fields = ['created_at', 'name', 'user__username']
    ordering = ['-created_at']

    def get_queryset(self):
        """Ne retourne que les decks publics actifs et non archivés."""
        queryset = FlashcardDeck.objects.filter(
            is_public=True,
            is_active=True,
            is_archived=False
        )
        
        # Filtres supplémentaires
        language = self.request.query_params.get('language')
        username = self.request.query_params.get('username')
        search = self.request.query_params.get('search')
        
        # Filtrer par langue si spécifié
        if language:
            queryset = queryset.filter(language=language)
            
        # Filtrer par nom d'utilisateur si spécifié
        if username:
            queryset = queryset.filter(user__username__icontains=username)

        # Recherche textuelle
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search) | 
                Q(user__username__icontains=search)
            ).distinct()

        # Tri par popularité si demandé
        sort_by = self.request.query_params.get('sort_by')
        if sort_by == 'popularity':
            queryset = queryset.annotate(card_count=Count('flashcards')).order_by('-card_count')
                
        return queryset

    @action(detail=True, methods=['get'])
    def cards(self, request, pk=None):
        """Récupérer toutes les cartes d'un deck public spécifique."""
        try:
            deck = self.get_object()
            
            # Vérifier que le deck est bien public
            if not deck.is_public:
                return Response(
                    {"detail": "This deck is not public."},
                    status=status.HTTP_403_FORBIDDEN
                )
                
            # Ne pas permettre de voir les cartes d'un deck archivé
            if deck.is_archived:
                return Response(
                    {"detail": "This deck is archived and not available for viewing"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            cards = deck.flashcards.all().order_by('-created_at')
            serializer = FlashcardSerializer(cards, many=True, context={'request': request})
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error fetching cards for public deck {pk}: {str(e)}")
            return Response(
                {"detail": f"Failed to fetch cards: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def clone(self, request, pk=None):
        """
        Action pour cloner un deck public d'un autre utilisateur.
        Crée une copie du deck et de ses cartes pour l'utilisateur courant.
        """
        source_deck = self.get_object()
        
        # Vérifier que le deck est public ou appartient à l'utilisateur
        if not source_deck.is_public and source_deck.user != request.user:
            return Response(
                {"detail": "You can only clone public decks or your own decks"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Ne pas permettre de cloner un deck archivé, sauf s'il appartient à l'utilisateur
        if source_deck.is_archived and source_deck.user != request.user:
            return Response(
                {"detail": "You cannot clone an archived deck from another user"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Créer un nouveau deck pour l'utilisateur
            new_deck = FlashcardDeck.objects.create(
                user=request.user,
                name=request.data.get('name', f"Clone of {source_deck.name}"),
                description=request.data.get('description', 
                                        f"Cloned from {source_deck.user.username}'s deck: {source_deck.description}"),
                is_active=True,
                is_public=False,  # Par défaut, les clones sont privés
                is_archived=False # Les clones ne sont jamais archivés
            )
            
            # Copier toutes les cartes
            cards_created = 0
            for card in source_deck.flashcards.all():
                Flashcard.objects.create(
                    user=request.user,
                    deck=new_deck,
                    front_text=card.front_text,
                    back_text=card.back_text,
                    learned=False,  # Réinitialiser l'état d'apprentissage
                    review_count=0  # Réinitialiser les stats d'apprentissage
                )
                cards_created += 1
            
            # Retourner les informations sur le nouveau deck
            serializer = FlashcardDeckSerializer(new_deck, context={'request': request})
            
            return Response({
                "message": f"Successfully cloned '{source_deck.name}' with {cards_created} cards",
                "deck": serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"detail": f"Failed to clone deck: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """
        Liste les decks publics les plus populaires.
        Définit la popularité en fonction du nombre de cartes dans le deck.
        """
        queryset = self.get_queryset().annotate(
            card_count=Count('flashcards')
        ).order_by('-card_count')
        
        # Limiter le nombre de résultats
        limit = int(request.query_params.get('limit', 10))
        queryset = queryset[:limit]
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
        
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Liste les decks publics les plus récents."""
        queryset = self.get_queryset().order_by('-created_at')
        
        # Limiter le nombre de résultats
        limit = int(request.query_params.get('limit', 10))
        queryset = queryset[:limit]
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)