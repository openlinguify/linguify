# apps/revision/views/stats_api_views.py
"""
API endpoints for revision statistics
Separated from web_views.py for better organization
"""
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models.revision_flashcard import FlashcardDeck, Flashcard
from ..models.revision_models import RevisionSession

import logging
logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_revision_stats(request):
    """
    API endpoint pour récupérer les statistiques de révision de l'utilisateur
    Compatible avec l'authentification DRF et Django sessions
    """
    try:
        # Ne compter que les decks actifs, non archivés, avec du contenu
        user_decks = FlashcardDeck.objects.select_related('user').filter(
            user=request.user, 
            is_active=True, 
            is_archived=False
        ).annotate(
            cards_count=Count('flashcards'),
            learned_count=Count('flashcards', filter=Q(flashcards__learned=True))
        ).filter(cards_count__gt=0)
        
        total_decks = user_decks.count()
        total_cards = sum(deck.cards_count for deck in user_decks)
        total_learned = sum(deck.learned_count for deck in user_decks)
        
        stats = {
            'totalDecks': total_decks,
            'totalCards': total_cards,
            'totalLearned': total_learned,
            'completionRate': round((total_learned / total_cards * 100) if total_cards > 0 else 0),
        }
        
        return Response(stats)
        
    except Exception as e:
        logger.error(f"Error in get_user_revision_stats: {str(e)}")
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_detailed_stats(request):
    """
    Récupère des statistiques détaillées pour l'utilisateur connecté
    """
    try:
        user = request.user
        
        # Calculer les statistiques par période
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # Stats de base optimisées
        total_decks = FlashcardDeck.objects.filter(user=user, is_active=True).count()
        total_cards = Flashcard.objects.filter(deck__user=user, deck__is_active=True).count()
        learned_cards = Flashcard.objects.filter(deck__user=user, deck__is_active=True, learned=True).count()
        
        # Sessions cette semaine et ce mois
        weekly_sessions = RevisionSession.objects.filter(user=user, created_at__gte=week_ago).count()
        monthly_sessions = RevisionSession.objects.filter(user=user, created_at__gte=month_ago).count()
        
        stats = {
            'total_decks': total_decks,
            'total_cards': total_cards,
            'learned_cards': learned_cards,
            'learning_rate': round((learned_cards / total_cards * 100) if total_cards > 0 else 0, 1),
            'weekly_sessions': weekly_sessions,
            'monthly_sessions': monthly_sessions,
        }
        
        return Response(stats)
        
    except Exception as e:
        logger.error(f"Error in get_detailed_stats: {str(e)}")
        return Response({'error': 'Failed to fetch detailed stats'}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recent_sessions(request):
    """
    Récupère les sessions récentes de l'utilisateur
    """
    try:
        user = request.user
        limit = int(request.GET.get('limit', 10))
        
        sessions = RevisionSession.objects.filter(
            user=user
        ).select_related('user').order_by('-created_at')[:limit]
        
        sessions_data = []
        for session in sessions:
            sessions_data.append({
                'id': session.id,
                'created_at': session.created_at.isoformat(),
                'duration': getattr(session, 'duration', 0),
                'cards_studied': getattr(session, 'cards_studied', 0),
                'score': getattr(session, 'score', 0),
            })
        
        return Response({
            'sessions': sessions_data,
            'total_count': sessions.count()
        })
        
    except Exception as e:
        logger.error(f"Error in get_recent_sessions: {str(e)}")
        return Response({'error': 'Failed to fetch recent sessions'}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_study_goals(request):
    """
    Récupère les objectifs d'étude de l'utilisateur
    """
    try:
        user = request.user
        
        # Pour l'instant, retourner des objectifs par défaut
        # TODO: Implémenter la gestion des objectifs personnalisés
        goals = {
            'daily_target': 20,  # cartes par jour
            'weekly_target': 140,  # cartes par semaine
            'current_streak': 0,  # jours consécutifs
            'longest_streak': 0,  # meilleur streak
        }
        
        # Calculer le streak actuel (implémentation basique)
        today = timezone.now().date()
        sessions_today = RevisionSession.objects.filter(
            user=user,
            created_at__date=today
        ).exists()
        
        if sessions_today:
            goals['current_streak'] = 1  # Implémentation simplifiée
        
        return Response(goals)
        
    except Exception as e:
        logger.error(f"Error in get_study_goals: {str(e)}")
        return Response({'error': 'Failed to fetch study goals'}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_deck_performance(request):
    """
    Récupère les performances par deck pour l'utilisateur
    """
    try:
        user = request.user
        limit = int(request.GET.get('limit', 5))
        
        decks = FlashcardDeck.objects.filter(
            user=user,
            is_active=True,
            is_archived=False
        ).select_related('user').annotate(
            total_cards=Count('flashcards'),
            learned_cards=Count('flashcards', filter=Q(flashcards__learned=True))
        ).order_by('-total_cards')[:limit]
        
        deck_performance = []
        for deck in decks:
            if deck.total_cards > 0:
                completion_rate = round((deck.learned_cards / deck.total_cards * 100), 1)
            else:
                completion_rate = 0
                
            deck_performance.append({
                'id': deck.id,
                'name': deck.name,
                'total_cards': deck.total_cards,
                'learned_cards': deck.learned_cards,
                'completion_rate': completion_rate,
                'last_studied': deck.updated_at.isoformat() if deck.updated_at else None
            })
        
        return Response({
            'decks': deck_performance
        })
        
    except Exception as e:
        logger.error(f"Error in get_deck_performance: {str(e)}")
        return Response({'error': 'Failed to fetch deck performance'}, status=500)