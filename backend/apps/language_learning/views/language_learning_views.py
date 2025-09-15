"""
Vues principales pour l'application Language Learning
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils.translation import gettext
from django.views.decorators.http import require_http_methods
from django.utils import timezone

# REST Framework imports
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import LanguagelearningItem, Language, UserLanguage, LANGUAGE_CHOICES, PROFICIENCY_LEVELS
from ..forms import LanguagelearningItemForm
from ..serializers.language_learning_serializers import (
    LanguageSerializer,
    UserLanguageSerializer,
    LanguagelearningItemSerializer,
    StartLanguageLearningSerializer,
    LanguageLearningStatsSerializer
)

import json
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# VUES WEB DJANGO (Pages HTML)
# =============================================================================

@login_required
def language_learning_home(request):
    """Page d'accueil de Language Learning - Personnalisé selon la langue cible de l'utilisateur"""
    items = LanguagelearningItem.objects.filter(
        user=request.user,
        is_active=True
    )
    
    paginator = Paginator(items, 10)
    page_number = request.GET.get('page')
    page_items = paginator.get_page(page_number)
    
    # Mapping entre les codes utilisateur (EN, FR, etc.) et nos codes internes (en, fr, etc.)
    auth_to_internal_mapping = {
        'EN': 'en',
        'FR': 'fr',
        'ES': 'es',
        'DE': 'de',
        'IT': 'it',
        'PT': 'pt',
        'NL': 'nl',
        'JA': 'ja',
    }
    
    # Obtenir la langue cible de l'utilisateur depuis ses paramètres
    user_target_language = request.user.target_language  # EN, FR, etc.
    user_target_internal = auth_to_internal_mapping.get(user_target_language, 'en')
    
    # Configuration des langues avec priorité pour la langue cible de l'utilisateur
    language_configs = {
        'en': ('English', 'Master English with interactive lessons', '🇬🇧'),
        'es': ('Spanish', 'Aprende español paso a paso', '🇪🇸'),
        'fr': ('French', 'Apprenez le français facilement', '🇫🇷'),
        'nl': ('Dutch', 'Leer Nederlands stap voor stap', '🇳🇱'),
    }
    
    # Créer la liste des langues avec la langue cible en premier
    available_languages = []
    
    # Ajouter d'abord la langue cible de l'utilisateur
    if user_target_internal in language_configs:
        code = user_target_internal
        name, description, flag = language_configs[code]
        lang, created = Language.objects.get_or_create(
            code=code,
            defaults={
                'name': name,
                'native_name': name,
                'flag_emoji': flag,
                'is_active': True
            }
        )
        available_languages.append({
            'code': code,
            'name': name,
            'description': description,
            'flag': flag,
            'is_learning': UserLanguage.objects.filter(user=request.user, language=lang).exists(),
            'is_target': True  # Marquer comme langue cible
        })
    
    # Ajouter les autres langues
    for code, (name, description, flag) in language_configs.items():
        if code == user_target_internal:
            continue  # Déjà ajoutée
            
        lang, created = Language.objects.get_or_create(
            code=code,
            defaults={
                'name': name,
                'native_name': name,
                'flag_emoji': flag,
                'is_active': True
            }
        )
        available_languages.append({
            'code': code,
            'name': name,
            'description': description,
            'flag': flag,
            'is_learning': UserLanguage.objects.filter(user=request.user, language=lang).exists(),
            'is_target': False
        })
    
    # Obtenir les langues que l'utilisateur apprend
    user_languages = UserLanguage.objects.filter(user=request.user, is_active=True).select_related('language')
    
    # Statistiques utilisateur (calculées dynamiquement)
    total_lessons = user_languages.count() * 8  # 8 leçons par langue en moyenne
    total_time = sum([ul.total_time_spent for ul in user_languages]) or 150  # en minutes
    max_streak = max([ul.streak_count for ul in user_languages]) if user_languages else 7
    
    # Convertir les minutes en heures/minutes
    hours = total_time // 60
    minutes = total_time % 60
    time_display = f"{hours}h {minutes:02d}m" if hours > 0 else f"{minutes}m"
    
    # Déterminer le niveau basé sur la langue cible spécifiquement
    target_lang_obj = Language.objects.filter(code=user_target_internal).first()
    user_target_progress = None
    if target_lang_obj:
        user_target_progress = UserLanguage.objects.filter(
            user=request.user, 
            language=target_lang_obj, 
            is_active=True
        ).first()
    
    current_level = 'Débutant'
    if user_target_progress:
        current_level = user_target_progress.get_proficiency_level_display()
    elif user_languages.count() > 1:
        current_level = 'Intermédiaire'
    
    user_stats = {
        'streak_days': max_streak,
        'completed_lessons': total_lessons,
        'total_time': time_display,
        'current_level': current_level,
        'target_language_name': language_configs.get(user_target_internal, ('English', '', ''))[0]
    }
    
    context = {
        'items': page_items,
        'total_items': items.count(),
        'available_languages': available_languages,
        'user_languages': user_languages,
        'user_stats': user_stats,
        'user_target_language': user_target_internal,
        'app_name': 'Language Learning',
    }
    return render(request, 'language_learning/home.html', context)


@login_required
def create_item(request):
    """Créer un nouvel item"""
    if request.method == 'POST':
        form = LanguagelearningItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            messages.success(request, f'{item.title} créé avec succès!')
            return redirect('language_learning:home')
    else:
        form = LanguagelearningItemForm()
    
    return render(request, 'language_learning/create_item.html', {'form': form})


@login_required
def edit_item(request, item_id):
    """Modifier un item"""
    item = get_object_or_404(LanguagelearningItem, id=item_id, user=request.user)
    
    if request.method == 'POST':
        form = LanguagelearningItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f'{item.title} modifié avec succès!')
            return redirect('language_learning:home')
    else:
        form = LanguagelearningItemForm(instance=item)
    
    return render(request, 'language_learning/edit_item.html', {'form': form, 'item': item})


@login_required
def delete_item(request, item_id):
    """Supprimer un item"""
    item = get_object_or_404(LanguagelearningItem, id=item_id, user=request.user)
    
    if request.method == 'POST':
        title = item.title
        item.delete()
        messages.success(request, f'{title} supprimé avec succès!')
        return redirect('language_learning:home')
    
    return render(request, 'language_learning/confirm_delete.html', {'item': item})


# =============================================================================
# API VIEWS DJANGO (JSON)
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_items(request):
    """API pour récupérer les items"""
    items = LanguagelearningItem.objects.filter(
        user=request.user,
        is_active=True
    ).values('id', 'title', 'description', 'created_at')
    
    return Response({
        'items': list(items),
        'count': len(items)
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_language_learning(request):
    """API pour démarrer l'apprentissage d'une langue"""
    try:
        data = json.loads(request.body)
        language_code = data.get('language_code')
        
        if not language_code:
            return Response(
                {'success': False, 'error': 'Language code is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Trouver ou créer la langue
        language = Language.objects.filter(code=language_code).first()
        if not language:
            return Response(
                {'success': False, 'error': 'Language not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Créer ou récupérer UserLanguage
        user_language, created = UserLanguage.objects.get_or_create(
            user=request.user,
            language=language,
            defaults={
                'proficiency_level': 'beginner',
                'target_level': 'intermediate',
                'daily_goal': 15,
                'is_active': True
            }
        )
        
        if not created:
            # Réactiver si c'était désactivé
            user_language.is_active = True
            user_language.save()
        
        return Response({
            'success': True, 
            'message': f'Apprentissage de {language.name} commencé !',
            'created': created
        })
        
    except json.JSONDecodeError:
        return Response(
            {'success': False, 'error': 'Invalid JSON'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error in start_language_learning: {e}")
        return Response(
            {'success': False, 'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# =============================================================================
# API REST VIEWSETS (DRF)
# =============================================================================

class LanguageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API REST pour les langues disponibles
    """
    serializer_class = LanguageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Retourne les langues actives"""
        return Language.objects.filter(is_active=True)
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Retourne les langues disponibles avec le statut d'apprentissage de l'utilisateur"""
        languages = self.get_queryset()
        serializer = self.get_serializer(languages, many=True)
        
        return Response({
            'success': True,
            'languages': serializer.data,
            'total': languages.count()
        })
    
    @action(detail=False, methods=['get'])
    def user_target(self, request):
        """Retourne la langue cible de l'utilisateur"""
        user_target = request.user.target_language
        
        # Mapping codes
        auth_to_internal = {
            'EN': 'en', 'FR': 'fr', 'ES': 'es', 'DE': 'de',
            'IT': 'it', 'PT': 'pt', 'NL': 'nl', 'JA': 'ja'
        }
        
        internal_code = auth_to_internal.get(user_target, 'en')
        language = Language.objects.filter(code=internal_code).first()
        
        if language:
            serializer = self.get_serializer(language)
            return Response({
                'success': True,
                'target_language': serializer.data,
                'auth_code': user_target,
                'internal_code': internal_code
            })
        
        return Response({
            'success': False,
            'error': 'Target language not found'
        }, status=status.HTTP_404_NOT_FOUND)


class UserLanguageViewSet(viewsets.ModelViewSet):
    """
    API REST pour les langues que l'utilisateur apprend
    """
    serializer_class = UserLanguageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtre par utilisateur connecté"""
        return UserLanguage.objects.filter(
            user=self.request.user
        ).select_related('language')
    
    def perform_create(self, serializer):
        """Associe à l'utilisateur connecté"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Retourne les langues activement étudiées"""
        active_languages = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(active_languages, many=True)
        
        return Response({
            'success': True,
            'active_languages': serializer.data,
            'count': active_languages.count()
        })
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Active/désactive une langue"""
        user_language = self.get_object()
        user_language.is_active = not user_language.is_active
        user_language.save()
        
        status_text = 'activé' if user_language.is_active else 'désactivé'
        
        return Response({
            'success': True,
            'message': f"Apprentissage de {user_language.language.name} {status_text}",
            'is_active': user_language.is_active
        })
    
    @action(detail=True, methods=['patch'])
    def update_progress(self, request, pk=None):
        """Met à jour le progrès d'apprentissage"""
        user_language = self.get_object()
        
        # Mise à jour des champs de progression
        if 'lessons_completed' in request.data:
            user_language.lessons_completed = request.data['lessons_completed']
        if 'total_time_spent' in request.data:
            user_language.total_time_spent += request.data.get('session_time', 0)
        if 'streak_count' in request.data:
            user_language.streak_count = request.data['streak_count']
        
        user_language.last_activity = timezone.now()
        user_language.save()
        
        serializer = self.get_serializer(user_language)
        return Response({
            'success': True,
            'message': 'Progrès mis à jour',
            'user_language': serializer.data
        })


class LanguagelearningItemViewSet(viewsets.ModelViewSet):
    """
    API REST pour les éléments d'apprentissage
    """
    serializer_class = LanguagelearningItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtre par utilisateur connecté"""
        return LanguagelearningItem.objects.filter(
            user=self.request.user
        ).select_related('language')
    
    def perform_create(self, serializer):
        """Associe à l'utilisateur connecté"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def by_language(self, request):
        """Retourne les items groupés par langue"""
        language_code = request.query_params.get('language', None)
        
        queryset = self.get_queryset().filter(is_active=True)
        if language_code:
            queryset = queryset.filter(language__code=language_code)
        
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'success': True,
            'items': serializer.data,
            'count': queryset.count(),
            'language_filter': language_code
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Statistiques d'apprentissage de l'utilisateur"""
        try:
            user = request.user
            user_languages = UserLanguage.objects.filter(user=user, is_active=True)
            
            # Calculs de base
            total_languages = user_languages.count()
            total_study_time = sum(ul.total_time_spent or 0 for ul in user_languages)
            longest_streak = max((ul.streak_count for ul in user_languages), default=0)
            total_lessons = sum(ul.lessons_completed or 0 for ul in user_languages)
            
            # Moyenne quotidienne (approximation basée sur 30 jours)
            average_daily_time = total_study_time / 30.0 if total_study_time > 0 else 0
            
            # Progrès par langue
            languages_progress = []
            for ul in user_languages:
                languages_progress.append({
                    'language_code': ul.language.code,
                    'language_name': ul.language.name,
                    'progress_percentage': ul.progress_percentage,
                    'proficiency_level': ul.proficiency_level,
                    'streak_count': ul.streak_count,
                    'time_spent': ul.total_time_spent or 0,
                    'lessons_completed': ul.lessons_completed or 0
                })
            
            # Activité récente (placeholder)
            recent_activity = [
                {
                    'date': timezone.now().date(),
                    'activity': 'Session d\'étude',
                    'language': ul.language.name,
                    'duration': 15
                } for ul in user_languages[:3]
            ]
            
            # Taux de completion des objectifs (placeholder)
            daily_goal_completion = 75.0
            
            # Progrès hebdomadaire (placeholder)
            weekly_progress = {
                'monday': 20,
                'tuesday': 15,
                'wednesday': 30,
                'thursday': 10,
                'friday': 25,
                'saturday': 0,
                'sunday': 20
            }
            
            stats_data = {
                'total_languages': total_languages,
                'active_languages': total_languages,
                'total_study_time': total_study_time,
                'longest_streak': longest_streak,
                'total_lessons_completed': total_lessons,
                'average_daily_time': average_daily_time,
                'languages_progress': languages_progress,
                'recent_activity': recent_activity,
                'daily_goal_completion_rate': daily_goal_completion,
                'weekly_progress': weekly_progress
            }
            
            return Response({
                'success': True,
                'stats': stats_data
            })
            
        except Exception as e:
            logger.error(f"Error calculating language learning stats: {e}")
            return Response({
                'success': False,
                'error': 'Erreur lors du calcul des statistiques'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)