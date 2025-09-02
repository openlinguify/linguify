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

from ..models.revision_flashcard import FlashcardDeck, Flashcard
from ..models.revision_schedule import RevisionSession
from apps.authentication.models import User


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
        
        # Tri
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
        else:  # relevance par défaut
            order_field = 'created_at'
        
        if sort_order == 'asc':
            decks = decks.order_by(order_field)
        else:
            decks = decks.order_by(f'-{order_field}')
        
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


@require_http_methods(["POST"])
@login_required
def import_deck_view(request, deck_id):
    """Vue HTMX pour importer un deck public"""
    
    source_deck = get_object_or_404(FlashcardDeck, id=deck_id, is_public=True)
    custom_name = request.POST.get('deck_name', '').strip()
    
    # Nom du nouveau deck
    if custom_name:
        new_name = custom_name
    else:
        new_name = f"{source_deck.name} (Copie)"
    
    # Création du deck copié
    new_deck = FlashcardDeck.objects.create(
        user=request.user,
        name=new_name,
        description=source_deck.description,
        category=source_deck.category,
        language=source_deck.language,
        level=source_deck.level,
        is_public=False,  # Copie privée par défaut
        original_deck_id=source_deck.id  # Référence au deck original
    )
    
    # Copie des flashcards
    for card in source_deck.flashcards.all():
        Flashcard.objects.create(
            deck=new_deck,
            question=card.question,
            answer=card.answer,
            category=card.category,
            difficulty=card.difficulty,
            notes=card.notes
        )
    
    # Réponse HTMX
    response = HttpResponse()
    response['HX-Trigger'] = json.dumps({
        'deckImported': {
            'deck_id': new_deck.id,
            'deck_name': new_name,
            'cards_count': new_deck.flashcards.count()
        },
        'showToast': {
            'type': 'success',
            'message': f'Deck "{new_name}" importé avec succès!'
        }
    })
    
    return response


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