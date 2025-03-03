# backend/revision/views/flashcard_views.py
from django.utils import timezone
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
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
    permission_classes = [IsAuthenticated]
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
        """Filtre les decks pour ne montrer que ceux de l'utilisateur actuel."""
        queryset = FlashcardDeck.objects.filter(user=self.request.user)
        
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
            
        return queryset

    def perform_create(self, serializer):
        """Associe automatiquement l'utilisateur actuel lors de la création d'un deck."""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get'])
    def cards(self, request, pk=None):
        """Récupérer toutes les cartes d'un deck spécifique."""
        try:
            # Vérifie que le deck appartient à l'utilisateur actuel
            deck = get_object_or_404(FlashcardDeck, id=pk, user=request.user)
            
            # Filtres optionnels
            learned = request.query_params.get('learned')
            cards_query = deck.flashcards.all()
            
            # Appliquer les filtres si présents
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
        
    @action(detail=True, methods=['patch'])
    def update_deck(self, request, pk=None):
        """Mettre à jour les informations d'un deck."""
        try:
            # Vérifie que le deck appartient à l'utilisateur actuel
            deck = get_object_or_404(FlashcardDeck, id=pk, user=request.user)
            
            serializer = self.get_serializer(deck, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
                
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error updating deck {pk}: {str(e)}")
            return Response(
                {"error": f"Failed to update deck: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

class FlashcardViewSet(viewsets.ModelViewSet):
    serializer_class = FlashcardSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['front_text', 'back_text']
    ordering_fields = ['created_at', 'last_reviewed', 'review_count']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filtrer les cartes par utilisateur, deck et statut."""
        # Filtrer par utilisateur actuel
        queryset = Flashcard.objects.filter(user=self.request.user)
        
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
        """Créer une nouvelle carte dans un deck spécifique."""
        deck_id = request.data.get('deck')
        
        try:
            # Vérifier que le deck existe et appartient à l'utilisateur actuel
            deck = get_object_or_404(FlashcardDeck, id=deck_id, user=request.user)
            
            # Créer la carte
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Associer utilisateur et deck
            serializer.save(user=request.user, deck=deck)
            
            logger.info(f"Created new flashcard in deck {deck_id} for user {request.user.username}")
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
            # Vérifie que la carte appartient à l'utilisateur actuel
            card = get_object_or_404(Flashcard, id=pk, user=request.user)
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
        """Mettre à jour une carte flashcard."""
        try:
            # Vérifier que la carte appartient à l'utilisateur actuel
            card = get_object_or_404(Flashcard, id=pk, user=request.user)
            
            serializer = self.get_serializer(card, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Error updating card {pk}: {str(e)}")
            return Response(
                {"error": f"Failed to update card: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def reset(self, request, pk=None):
        """Réinitialiser les statistiques d'apprentissage d'une carte."""
        try:
            # Vérifier que la carte appartient à l'utilisateur actuel
            card = get_object_or_404(Flashcard, id=pk, user=request.user)
            
            # Réinitialiser les statistiques
            card.reset_progress()
            
            serializer = self.get_serializer(card)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error resetting card {pk}: {str(e)}")
            return Response(
                {"error": f"Failed to reset card: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
class FlashcardImportView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        try:
            # Récupérer le fichier Excel et l'ID du deck
            excel_file = request.FILES.get('file')
            deck_id = request.data.get('deck_id')
            
            # Vérifier si le fichier est présent
            if not excel_file:
                return Response({"detail": "Aucun fichier n'a été fourni."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Vérifier le type de fichier
            if not excel_file.name.endswith(('.xls', '.xlsx')):
                return Response({"detail": "Le fichier doit être au format Excel (.xls ou .xlsx)."}, 
                               status=status.HTTP_400_BAD_REQUEST)

            # Vérifier si le deck existe et appartient à l'utilisateur
            try:
                deck = FlashcardDeck.objects.get(id=deck_id, user=request.user)
            except FlashcardDeck.DoesNotExist:
                return Response({"detail": "Le deck spécifié n'existe pas ou ne vous appartient pas."}, 
                               status=status.HTTP_404_NOT_FOUND)
            
            # Lire le fichier Excel
            df = pd.read_excel(excel_file, engine='openpyxl')
            
            # Vérifier que les colonnes nécessaires existent
            required_columns = ['front_text', 'back_text']
            # Si le fichier a des noms de colonnes différents (par exemple 'anglais', 'français'),
            # on peut les mapper automatiquement aux 2 premières colonnes
            if len(df.columns) < 2:
                return Response({"detail": "Le fichier doit contenir au moins 2 colonnes."}, 
                               status=status.HTTP_400_BAD_REQUEST)
            
            # Si les colonnes ne sont pas nommées front_text et back_text, on les renomme
            if df.columns[0] != 'front_text' or df.columns[1] != 'back_text':
                df = df.iloc[:, :2]  # Prendre seulement les 2 premières colonnes
                df.columns = ['front_text', 'back_text']
            
            # Créer les flashcards
            flashcards_created = 0
            flashcards_failed = 0
            
            for _, row in df.iterrows():
                front_text = str(row['front_text']).strip()
                back_text = str(row['back_text']).strip()
                
                # Ignorer les lignes vides
                if not front_text or not back_text or front_text == 'nan' or back_text == 'nan':
                    continue
                
                try:
                    Flashcard.objects.create(
                        deck=deck,
                        front_text=front_text,
                        back_text=back_text,
                        user=request.user
                    )
                    flashcards_created += 1
                except Exception as e:
                    flashcards_failed += 1
                    print(f"Erreur lors de la création d'une flashcard: {e}")
            
            return Response({
                "detail": f"{flashcards_created} cartes ont été importées avec succès. {flashcards_failed} imports ont échoué.",
                "created": flashcards_created,
                "failed": flashcards_failed
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({"detail": f"Une erreur s'est produite lors de l'importation: {str(e)}"}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)