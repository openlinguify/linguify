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
from ..models.revision_schedule import RevisionSession

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
            'total_decks': total_decks,
            'total_cards': total_cards,
            'total_learned': total_learned,
            'completion_percentage': round((total_learned / total_cards * 100) if total_cards > 0 else 0),
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
        period = int(request.GET.get('period', 30))
        
        # Calculer les statistiques par période
        now = timezone.now()
        period_ago = now - timedelta(days=period)
        
        # Sessions complétées dans la période
        period_sessions = RevisionSession.objects.filter(
            user=user, 
            status='COMPLETED',
            completed_date__gte=period_ago
        ).prefetch_related('flashcards')
        
        # Calculer les statistiques réelles basées sur les sessions
        total_studied_cards = 0
        total_sessions = period_sessions.count()
        total_success_rate = 0
        
        for session in period_sessions:
            # Compter les flashcards dans cette session
            flashcards_count = session.flashcards.count()
            total_studied_cards += flashcards_count
            
            # Ajouter le taux de succès
            if session.success_rate is not None:
                total_success_rate += session.success_rate
        
        # Calculer le taux d'exactitude moyen
        accuracy_rate = round(total_success_rate / total_sessions) if total_sessions > 0 else 0
        
        # Calculer le streak actuel (jours consécutifs avec des sessions complétées)
        current_streak = 0
        check_date = now.date()
        while True:
            has_session = RevisionSession.objects.filter(
                user=user, 
                status='COMPLETED',
                completed_date__date=check_date
            ).exists()
            
            if has_session:
                current_streak += 1
                check_date -= timedelta(days=1)
            else:
                break
            
            # Limite de sécurité
            if current_streak > 365:
                break
        
        # Estimation du temps d'étude (2 minutes par carte en moyenne)
        estimated_study_time = total_studied_cards * 2
        
        # Calculer la répartition des performances basée sur les taux de succès
        total_correct = round(total_studied_cards * accuracy_rate / 100) if accuracy_rate > 0 else 0
        total_incorrect = total_studied_cards - total_correct
        
        stats = {
            'total_studied_cards': total_studied_cards,
            'accuracy_rate': accuracy_rate,
            'total_study_time': estimated_study_time,  # en minutes
            'current_streak': current_streak,
            'daily_activity': [],  # TODO: Implémenter les données journalières
            'performance_breakdown': {
                'correct': total_correct,
                'incorrect': total_incorrect,
                'skipped': 0  # TODO: Ajouter les cartes sautées
            }
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
            user=user,
            status='COMPLETED'
        ).select_related('user').prefetch_related('flashcards').order_by('-completed_date')[:limit]
        
        sessions_data = []
        for session in sessions:
            # Get deck name from first flashcard in the session
            deck_name = "Mixed Study Session"  # Default fallback
            flashcards = session.flashcards.all()
            if flashcards.exists():
                # Get the deck from the first flashcard
                first_deck = flashcards.first().deck
                if first_deck:
                    deck_name = first_deck.name
            
            sessions_data.append({
                'id': session.id,
                'created_at': session.completed_date.isoformat() if session.completed_date else session.scheduled_date.isoformat(),
                'deck_name': deck_name,
                'mode': 'Review',  # Default mode
                'cards_studied': flashcards.count(),
                'accuracy': round(session.success_rate) if session.success_rate else 0,
            })
        
        return Response({
            'results': sessions_data,
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
        
        # Calculer les statistiques actuelles
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        
        # Cartes étudiées aujourd'hui
        today_sessions = RevisionSession.objects.filter(
            user=user,
            status='COMPLETED',
            completed_date__date=today
        ).prefetch_related('flashcards')
        
        today_cards = 0
        for session in today_sessions:
            today_cards += session.flashcards.count()
        
        # Temps d'étude cette semaine (estimation: 2 minutes par carte)
        week_sessions = RevisionSession.objects.filter(
            user=user,
            status='COMPLETED',
            completed_date__date__gte=week_start
        ).prefetch_related('flashcards')
        
        week_cards = 0
        for session in week_sessions:
            week_cards += session.flashcards.count()
        week_time = week_cards * 2  # 2 minutes par carte
        
        # Calculer l'exactitude récente (30 derniers jours)
        month_ago = today - timedelta(days=30)
        recent_sessions = RevisionSession.objects.filter(
            user=user,
            status='COMPLETED',
            completed_date__date__gte=month_ago
        )
        
        total_score = 0
        session_count = 0
        for session in recent_sessions:
            if session.success_rate is not None:
                total_score += session.success_rate
                session_count += 1
        
        current_accuracy = round(total_score / session_count) if session_count > 0 else 0
        
        goals = {
            'daily_cards_progress': {
                'current': today_cards,
                'target': 20
            },
            'weekly_time_progress': {
                'current': week_time,
                'target': 300  # 5 heures par semaine
            },
            'accuracy_progress': {
                'current': current_accuracy,
                'target': 85
            }
        }
        
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
                'description': deck.description or '',
                'cards_count': deck.total_cards,
                'mastered_cards': deck.learned_cards,
                'mastery_percentage': completion_rate,
                'accuracy': completion_rate,  # Using completion rate as accuracy for now
                'last_studied': deck.updated_at.isoformat() if deck.updated_at else None
            })
        
        return Response({
            'results': deck_performance
        })
        
    except Exception as e:
        logger.error(f"Error in get_deck_performance: {str(e)}")
        return Response({'error': 'Failed to fetch deck performance'}, status=500)