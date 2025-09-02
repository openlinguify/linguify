"""
Vues HTMX pour l'exploration des decks publics
Migration du JavaScript vers HTMX pour une approche plus simple et performante
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count, Avg, F
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import json
from typing import Dict, Any, List
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination

from ..models.revision_flashcard import FlashcardDeck, Flashcard
from ..models.revision_schedule import RevisionSession
from apps.authentication.models import User
from django.core.exceptions import ValidationError, ObjectDoesNotExist, PermissionDenied
from django.db import IntegrityError, OperationalError
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


class DeckPagination(PageNumberPagination):
    """Pagination pour l'exploration des decks publics."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# ===== MIXINS POUR L'EXPLORATION =====

class DeckCloneMixin:
    """Mixin pour la fonctionnalité de clonage des decks publics dans l'exploration."""
    
    def clone_deck(self, source_deck, request):
        """
        Méthode commune pour cloner un deck public.
        """
        # Vérifier que le deck est public ou appartient à l'utilisateur
        if not source_deck.is_public and source_deck.user != request.user:
            return JsonResponse(
                {"detail": "You can only clone public decks or your own decks"},
                status=403
            )
        
        # Ne pas permettre de cloner un deck archivé, sauf s'il appartient à l'utilisateur
        if source_deck.is_archived and source_deck.user != request.user:
            return JsonResponse(
                {"detail": "You cannot clone an archived deck from another user"},
                status=400
            )
        
        try:
            # Récupérer le nom personnalisé depuis la requête POST
            custom_name = request.POST.get('deck_name', '').strip()
            
            # Créer un nouveau deck pour l'utilisateur
            new_deck = FlashcardDeck.objects.create(
                user=request.user,
                name=custom_name if custom_name else f"Clone of {source_deck.name}",
                description=f"Cloned from {source_deck.user.username}'s deck: {source_deck.description}",
                is_public=False,  # Par défaut, les clones sont privés
                is_archived=False # Les clones ne sont jamais archivés
            )
            
            # Copier toutes les cartes
            cards_created = 0
            for card in source_deck.flashcards.all():
                Flashcard.objects.create(
                    user=request.user,
                    deck=new_deck,
                    question=card.question,
                    answer=card.answer,
                    category=card.category,
                    difficulty=card.difficulty,
                    notes=card.notes,
                    learned=False,  # Réinitialiser l'état d'apprentissage
                    review_count=0  # Réinitialiser les stats d'apprentissage
                )
                cards_created += 1
            
            # Retourner les informations sur le nouveau deck pour HTMX
            return JsonResponse({
                "success": True,
                "message": f"Successfully cloned '{source_deck.name}' with {cards_created} cards",
                "deck": {
                    "id": new_deck.id,
                    "name": new_deck.name,
                    "cards_count": cards_created
                }
            })
            
        except ValidationError as e:
            logger.error(f"Validation error cloning deck {source_deck.id}: {str(e)}")
            return JsonResponse(
                {"detail": f"Validation failed: {str(e)}"},
                status=400
            )
        except IntegrityError as e:
            logger.error(f"Database integrity error cloning deck {source_deck.id}: {str(e)}")
            return JsonResponse(
                {"detail": "Database integrity error - this deck might already exist"},
                status=409
            )
        except PermissionDenied as e:
            logger.error(f"Permission denied cloning deck {source_deck.id}: {str(e)}")
            return JsonResponse(
                {"detail": "Permission denied"},
                status=403
            )
        except Exception as e:
            logger.exception(f"Unexpected error cloning deck {source_deck.id}")
            return JsonResponse(
                {"detail": "An unexpected error occurred. Please contact support."},
                status=500
            )


class ExploreBaseView(View):
    """Vue de base pour l'exploration des decks publics"""
    
    def get_base_context(self, request) -> Dict[str, Any]:
        """Contexte de base pour toutes les vues d'exploration"""
        return {
            'user_data': {
                'id': request.user.id if request.user.is_authenticated else None,
                'username': request.user.username if request.user.is_authenticated else None,
                'is_authenticated': request.user.is_authenticated,
            },
            'api_base_url': '/api/v1/revision',
            'debug': settings.DEBUG,
        }


class ExploreMainView(ExploreBaseView):
    """Vue principale de l'exploration - remplace la page statique"""
    
    def get(self, request):
        context = self.get_base_context(request)
        context.update({
            'page_title': 'Révision - Explorer les Flashcards Publiques',
            'app_name': 'revision',
            'view_type': 'explore',
        })
        
        # Si c'est une requête HTMX, on ne retourne que le contenu
        if request.headers.get('HX-Request'):
            return render(request, 'revision/explore/partials/explore_welcome.html', context)
        
        return render(request, 'revision/explore/explore.html', context)


class SearchDecksView(ExploreBaseView):
    """Vue HTMX pour la recherche de decks"""
    
    def get(self, request):
        # Paramètres de recherche
        query = request.GET.get('q', '').strip()
        category = request.GET.get('category', '')
        language = request.GET.get('language', '')
        level = request.GET.get('level', '')
        author = request.GET.get('author', '')
        min_cards = request.GET.get('min_cards', '')
        max_cards = request.GET.get('max_cards', '')
        min_rating = request.GET.get('rating', '0')
        sort_by = request.GET.get('sort', 'relevance')
        sort_order = request.GET.get('order', 'desc')
        page = request.GET.get('page', 1)
        per_page = int(request.GET.get('per_page', 20))
        
        # Construction de la requête
        decks = FlashcardDeck.objects.filter(is_public=True)
        
        # Filtres de recherche
        if query:
            decks = decks.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(user__username__icontains=query)
            )
        
        if category:
            decks = decks.filter(category=category)
            
        if language:
            decks = decks.filter(language=language)
            
        if level:
            decks = decks.filter(level=level)
            
        if author:
            decks = decks.filter(user__username__icontains=author)
            
        # Filtre par nombre de cartes
        if min_cards:
            try:
                min_val = int(min_cards)
                decks = decks.annotate(cards_count=Count('flashcards')).filter(cards_count__gte=min_val)
            except ValueError:
                pass
                
        if max_cards:
            try:
                max_val = int(max_cards)
                decks = decks.annotate(cards_count=Count('flashcards')).filter(cards_count__lte=max_val)
            except ValueError:
                pass
        
        # Annotation pour les statistiques
        decks = decks.annotate(
            cards_count=Count('flashcards'),
            avg_rating=Avg('ratings__rating'),  # Supposant un modèle Rating
            downloads_count=Count('revision_sessions__user', distinct=True)
        ).select_related('user')
        
        # Tri optimisé pour l'exploration
        if sort_by == 'popularity':
            order_field = 'downloads_count'
        elif sort_by == 'rating':
            order_field = 'avg_rating'  
        elif sort_by == 'created_at':
            order_field = 'created_at'
        elif sort_by == 'name':
            order_field = 'name'
        elif sort_by == 'cards_count':
            order_field = 'cards_count'
        else:  # relevance par défaut - utiliser popularité
            # Pour l'exploration, on privilégie les decks avec plus de cartes
            order_field = 'cards_count'
        
        if sort_order == 'asc':
            decks = decks.order_by(order_field)
        else:
            decks = decks.order_by(f'-{order_field}')
        
        # Optimisation spéciale pour l'exploration : prioriser les decks actifs et bien remplis
        if sort_by == 'relevance' or not sort_by:
            # Filtrer les decks avec au moins 5 cartes pour la pertinence
            decks = decks.filter(cards_count__gte=5)
        
        # Pagination
        paginator = Paginator(decks, per_page)
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        
        context = self.get_base_context(request)
        context.update({
            'decks': page_obj,
            'query': query,
            'total_results': paginator.count,
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'has_previous': page_obj.has_previous(),
            'has_next': page_obj.has_next(),
            'filters': {
                'category': category,
                'language': language,
                'level': level,
                'author': author,
                'min_cards': min_cards,
                'max_cards': max_cards,
                'min_rating': min_rating,
                'sort_by': sort_by,
                'sort_order': sort_order,
            }
        })
        
        return render(request, 'revision/explore/partials/search_results.html', context)


class DeckDetailsView(ExploreBaseView):
    """Vue HTMX pour les détails d'un deck public"""
    
    def get(self, request, deck_id):
        deck = get_object_or_404(FlashcardDeck, id=deck_id, is_public=True)
        
        # Récupération des cartes (avec pagination)
        cards = deck.flashcards.all()[:10]  # Limite pour l'aperçu
        
        # Statistiques du deck
        total_cards = deck.flashcards.count()
        # Calculer les sessions via les flashcards du deck
        total_sessions = RevisionSession.objects.filter(
            flashcards__deck=deck
        ).values('user').distinct().count()
        
        # Évaluations (si le modèle existe)
        # avg_rating = deck.ratings.aggregate(Avg('rating'))['rating__avg']
        # reviews = deck.reviews.all()[:5]
        
        context = self.get_base_context(request)
        context.update({
            'deck': deck,
            'cards': cards,
            'total_cards': total_cards,
            'total_sessions': total_sessions,
            'can_import': request.user.is_authenticated,
            # 'avg_rating': avg_rating,
            # 'reviews': reviews,
        })
        
        return render(request, 'revision/explore/partials/deck_details.html', context)


class ImportDeckView(DeckCloneMixin, View):
    """Vue HTMX pour importer un deck public utilisant le mixin de clonage"""
    
    @method_decorator(login_required)
    def post(self, request, deck_id):
        """Import d'un deck public via HTMX"""
        source_deck = get_object_or_404(FlashcardDeck, id=deck_id, is_public=True)
        
        # Utiliser le mixin pour cloner le deck
        clone_result = self.clone_deck(source_deck, request)
        
        # Si c'est un JsonResponse d'erreur, on la convertit en HttpResponse pour HTMX
        if hasattr(clone_result, 'status_code') and clone_result.status_code != 200:
            response = HttpResponse()
            response['HX-Trigger'] = json.dumps({
                'showToast': {
                    'type': 'error',
                    'message': json.loads(clone_result.content)['detail']
                }
            })
            return response
        
        # Succès - extraire les données et créer la réponse HTMX
        clone_data = json.loads(clone_result.content)
        response = HttpResponse()
        response['HX-Trigger'] = json.dumps({
            'deckImported': {
                'deck_id': clone_data['deck']['id'],
                'deck_name': clone_data['deck']['name'],
                'cards_count': clone_data['deck']['cards_count']
            },
            'showToast': {
                'type': 'success',
                'message': clone_data['message']
            }
        })
        
        return response

# Vue fonction wrapper pour compatibilité URLs
@require_http_methods(["POST"])
@login_required  
def import_deck_view(request, deck_id):
    """Wrapper fonction pour ImportDeckView"""
    view = ImportDeckView()
    return view.post(request, deck_id)


class FilterOptionsView(ExploreBaseView):
    """Vue HTMX pour charger les options de filtres dynamiquement"""
    
    def get(self, request):
        filter_type = request.GET.get('type', '')
        
        if filter_type == 'categories':
            # Récupérer toutes les catégories disponibles
            categories = FlashcardDeck.objects.filter(
                is_public=True
            ).values_list('category', flat=True).distinct().order_by('category')
            
            return JsonResponse({
                'options': [{'value': cat, 'label': cat.title()} for cat in categories if cat]
            })
        
        elif filter_type == 'languages':
            languages = FlashcardDeck.objects.filter(
                is_public=True
            ).values_list('language', flat=True).distinct().order_by('language')
            
            return JsonResponse({
                'options': [{'value': lang, 'label': lang.upper()} for lang in languages if lang]
            })
        
        elif filter_type == 'authors':
            query = request.GET.get('q', '')
            authors = User.objects.filter(
                flashcard_decks__is_public=True,
                username__icontains=query
            ).distinct()[:10]
            
            return JsonResponse({
                'options': [{'value': user.username, 'label': user.username} for user in authors]
            })
        
        return JsonResponse({'options': []})


class StatsView(ExploreBaseView):
    """Vue HTMX pour les statistiques globales"""
    
    def get(self, request):
        stats = {
            'total_decks': FlashcardDeck.objects.filter(is_public=True).count(),
            'total_cards': Flashcard.objects.filter(deck__is_public=True).count(),
            'total_authors': User.objects.filter(
                flashcard_decks__is_public=True
            ).distinct().count(),
            'weekly_activity': RevisionSession.objects.filter(
                completed_date__gte=timezone.now() - timedelta(days=7)
            ).count()
        }
        
        context = self.get_base_context(request)
        context.update({'stats': stats})
        
        return render(request, 'revision/explore/partials/community_stats.html', context)


class TrendingDecksView(ExploreBaseView):
    """Vue HTMX pour les decks tendance"""
    
    def get(self, request):
        period = request.GET.get('period', 'week')
        
        # Calcul de la période
        
        if period == 'week':
            since = timezone.now() - timedelta(days=7)
        elif period == 'month':
            since = timezone.now() - timedelta(days=30)
        else:  # all-time
            since = None
        
        # Decks les plus utilisés (via les flashcards)
        base_query = RevisionSession.objects.filter(flashcards__deck__is_public=True)
        if since:
            base_query = base_query.filter(completed_date__gte=since)
        
        trending = base_query.values('flashcards__deck').annotate(
            sessions_count=Count('id'),
            unique_users=Count('user', distinct=True)
        ).order_by('-sessions_count')[:10]
        
        # Récupération des decks complets
        deck_ids = [item['flashcards__deck'] for item in trending if item['flashcards__deck']]
        decks = FlashcardDeck.objects.filter(id__in=deck_ids).annotate(
            cards_count=Count('flashcards')
        )
        
        # Mappage des stats
        deck_stats = {item['flashcards__deck']: item for item in trending}
        
        context = self.get_base_context(request)
        context.update({
            'decks': decks,
            'deck_stats': deck_stats,
            'period': period
        })
        
        return render(request, 'revision/explore/partials/trending_decks.html', context)


class PopularDecksView(ExploreBaseView):
    """Vue HTMX pour les decks publics populaires - optimisée exploration"""
    
    def get(self, request):
        limit = int(request.GET.get('limit', 10))
        category = request.GET.get('category', '')
        
        # Requête optimisée pour les decks populaires
        queryset = FlashcardDeck.objects.filter(
            is_public=True,
            is_archived=False,
        ).select_related('user').annotate(
            cards_count=Count('flashcards'),
            sessions_count=Count('revision_sessions', distinct=True),
            # Score de popularité composite
            popularity_score=F('cards_count') + F('sessions_count') * 2
        )
        
        # Filtre par catégorie si spécifié
        if category and category != 'all':
            queryset = queryset.filter(category=category)
        
        # Filtrer les decks avec au moins 3 cartes
        queryset = queryset.filter(cards_count__gte=3)
        
        # Trier par score de popularité
        popular_decks = queryset.order_by('-popularity_score', '-cards_count')[:limit]
        
        context = self.get_base_context(request)
        context.update({
            'decks': popular_decks,
            'category': category,
            'limit': limit,
        })
        
        return render(request, 'revision/explore/partials/popular_decks.html', context)


class PublicDecksViewSet(DeckCloneMixin, viewsets.ReadOnlyModelViewSet):
    """
    ViewSet API pour explorer les decks publics.
    En lecture seule, ne permet pas de modification.
    Migré depuis flashcard_views.py pour centraliser la logique d'exploration.
    """
    permission_classes = [AllowAny]
    pagination_class = DeckPagination
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
        ).select_related('user').prefetch_related('flashcards').annotate(
            cards_count=Count('flashcards'),
            learned_count=Count('flashcards', filter=Q(flashcards__learned=True))
        )
        
        # Filtres supplémentaires
        username = self.request.query_params.get('username')
        author = self.request.query_params.get('author')
        search = self.request.query_params.get('search')
        min_cards = self.request.query_params.get('minCards')
        max_cards = self.request.query_params.get('maxCards')
            
        # Filtrer par nom d'utilisateur si spécifié
        if username:
            queryset = queryset.filter(user__username__icontains=username)
            
        # Filtrer par auteur (alternative pour username)
        if author:
            queryset = queryset.filter(user__username__icontains=author)

        # Recherche textuelle
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search) | 
                Q(user__username__icontains=search)
            ).distinct()

        # Filtrer par nombre de cartes
        if min_cards:
            try:
                min_cards = int(min_cards)
                queryset = queryset.filter(cards_count__gte=min_cards)
            except ValueError:
                pass
                
        if max_cards:
            try:
                max_cards = int(max_cards)
                queryset = queryset.filter(cards_count__lte=max_cards)
            except ValueError:
                pass

        # Tri par popularité si demandé
        sort_by = self.request.query_params.get('sort_by') or self.request.query_params.get('sortBy')
        if sort_by == 'popularity':
            queryset = queryset.order_by('-cards_count')
        elif sort_by == 'cards_count':
            queryset = queryset.order_by('-cards_count')
        elif sort_by == 'name':
            queryset = queryset.order_by('name')
                
        return queryset

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Récupérer les statistiques des decks publics."""
        try:
            public_decks = FlashcardDeck.objects.filter(
                is_public=True,
                is_active=True,
                is_archived=False
            ).select_related('user').prefetch_related('flashcards')
            
            total_decks = public_decks.count()
            total_cards = sum(deck.flashcards.count() for deck in public_decks)
            total_authors = public_decks.values('user').distinct().count()
            
            stats = {
                'totalDecks': total_decks,
                'totalCards': total_cards,
                'totalAuthors': total_authors
            }
            
            return Response(stats)
            
        except Exception as e:
            logger.error(f"Error fetching public decks stats: {str(e)}")
            return Response(
                {"detail": f"Failed to fetch stats: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

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
            # Note: Nous utiliserions FlashcardSerializer ici, mais nous gardons la logique simple
            # pour éviter les dépendances circulaires dans cette migration
            cards_data = [{
                'id': card.id,
                'front': card.front,
                'back': card.back,
                'learned': card.learned,
                'created_at': card.created_at.isoformat() if card.created_at else None
            } for card in cards]
            
            return Response(cards_data)
            
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
        Utilise le mixin DeckCloneMixin pour la logique de clonage.
        """
        source_deck = self.get_object()
        return self.clone_deck(source_deck, request)

    @action(detail=False, methods=['get'])
    def popular(self, request):
        """
        Liste les decks publics les plus populaires.
        """
        queryset = self.get_queryset().annotate(
            card_count=Count('flashcards')
        ).order_by('-card_count')
        
        # Limiter le nombre de résultats
        limit = int(request.query_params.get('limit', 10))
        queryset = queryset[:limit]
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            # Utilisation d'une sérialisation simple pour éviter les dépendances
            data = self._serialize_decks_simple(page)
            return self.get_paginated_response(data)
            
        data = self._serialize_decks_simple(queryset)
        return Response(data)

    def _serialize_decks_simple(self, decks):
        """Sérialisation simple des decks pour éviter les dépendances circulaires."""
        return [{
            'id': deck.id,
            'name': deck.name,
            'description': deck.description,
            'cards_count': getattr(deck, 'cards_count', deck.flashcards.count()),
            'learned_count': getattr(deck, 'learned_count', 0),
            'user': {
                'username': deck.user.username,
                'id': deck.user.id
            },
            'created_at': deck.created_at.isoformat() if deck.created_at else None,
            'is_public': deck.is_public,
            'is_archived': deck.is_archived
        } for deck in decks]


class SearchSuggestionsView(ExploreBaseView):
    """Vue HTMX pour les suggestions de recherche"""
    
    def get(self, request):
        query = request.GET.get('q', '').strip().lower()
        
        if not query or len(query) < 2:
            return JsonResponse({'suggestions': []})
        
        # Suggestions basées sur les noms de decks
        deck_suggestions = FlashcardDeck.objects.filter(
            is_public=True,
            name__icontains=query
        ).values_list('name', flat=True)[:5]
        
        # Suggestions basées sur les catégories
        category_suggestions = FlashcardDeck.objects.filter(
            is_public=True,
            category__icontains=query
        ).values_list('category', flat=True).distinct()[:3]
        
        # Suggestions basées sur les auteurs
        author_suggestions = User.objects.filter(
            flashcard_decks__is_public=True,
            username__icontains=query
        ).values_list('username', flat=True).distinct()[:3]
        
        suggestions = []
        
        # Formatage des suggestions
        for name in deck_suggestions:
            suggestions.append({
                'type': 'deck',
                'text': name,
                'icon': 'bi-stack'
            })
        
        for category in category_suggestions:
            suggestions.append({
                'type': 'category',
                'text': category,
                'icon': 'bi-folder2'
            })
        
        for author in author_suggestions:
            suggestions.append({
                'type': 'author',
                'text': f"Par {author}",
                'icon': 'bi-person-circle'
            })
        
        return JsonResponse({'suggestions': suggestions[:8]})


# Vues utilitaires pour les actions HTMX

@require_http_methods(["POST"])
@login_required
def toggle_favorite_view(request, deck_id):
    """Vue HTMX pour ajouter/retirer des favoris"""
    # Implementation dépend du modèle Favorite
    pass


@require_http_methods(["POST"]) 
@login_required
def add_to_collection_view(request, deck_id):
    """Vue HTMX pour ajouter un deck à une collection"""
    # Implementation dépend du modèle Collection
    pass


@require_http_methods(["POST"])
@login_required  
def rate_deck_view(request, deck_id):
    """Vue HTMX pour noter un deck"""
    # Implementation dépend du modèle Rating
    pass