"""
Vues unifiées pour les paramètres de Language Learning - Interface web et API REST
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib import messages
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.contrib.auth import get_user_model

# REST Framework imports
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# App specific imports
from app_manager.mixins import SettingsContextMixin
from ..models import UserLanguage, Language, LanguageLearningSettings
from ..serializers.settings_serializers import (
    LanguageLearningSettingsSerializer,
    ApplyLanguageLearningPresetSerializer,
    LanguageLearningSessionConfigSerializer,
    UserLanguagePreferencesSerializer
)

import json
import logging
from datetime import datetime, time

logger = logging.getLogger(__name__)
User = get_user_model()


# =============================================================================
# INTERFACE WEB DJANGO (Pages HTML)
# =============================================================================

@method_decorator(login_required, name='dispatch')
class LanguageLearningSettingsView(View):
    """Interface web pour les paramètres d'apprentissage des langues"""
    
    def get(self, request):
        """Affiche la page des paramètres d'apprentissage des langues"""
        try:
            # Check if it's an AJAX request for getting settings as JSON
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
            # Get or create language learning settings from database
            language_learning_settings, created = LanguageLearningSettings.objects.get_or_create(
                user=request.user,
                defaults={
                    'preferred_study_time': timezone.datetime.strptime('18:00', '%H:%M').time(),
                    'daily_goal_minutes': 15,
                    'weekly_goal_days': 5,
                    'reminder_enabled': True,
                    'reminder_frequency': 'daily',
                    'streak_notifications': True,
                    'achievement_notifications': True,
                    'auto_difficulty_adjustment': True,
                    'preferred_difficulty': 'adaptive',
                    'show_pronunciation_hints': True,
                    'enable_audio_playback': True,
                    'audio_playback_speed': 1.0,
                    'show_progress_animations': True,
                    'font_size': 'medium'
                }
            )
            
            if created:
                logger.info(f"Created new LanguageLearningSettings for user {request.user.username}")
            
            # Convert model to dict for template usage
            settings = {
                'preferred_study_time': language_learning_settings.preferred_study_time.strftime('%H:%M'),
                'daily_goal_minutes': language_learning_settings.daily_goal_minutes,
                'weekly_goal_days': language_learning_settings.weekly_goal_days,
                'reminder_enabled': language_learning_settings.reminder_enabled,
                'reminder_frequency': language_learning_settings.reminder_frequency,
                'streak_notifications': language_learning_settings.streak_notifications,
                'achievement_notifications': language_learning_settings.achievement_notifications,
                'auto_difficulty_adjustment': language_learning_settings.auto_difficulty_adjustment,
                'preferred_difficulty': language_learning_settings.preferred_difficulty,
                'show_pronunciation_hints': language_learning_settings.show_pronunciation_hints,
                'enable_audio_playback': language_learning_settings.enable_audio_playback,
                'audio_playback_speed': language_learning_settings.audio_playback_speed,
                'show_progress_animations': language_learning_settings.show_progress_animations,
                'font_size': language_learning_settings.font_size,
                'target_language': request.user.target_language or 'EN',
                'interface_language': 'fr',
                # Add some default learning methods for backward compatibility
                'learning_methods': ['flashcards', 'vocabulary', 'listening'],
            }
            
            # Récupérer les langues que l'utilisateur apprend actuellement
            user_languages = UserLanguage.objects.filter(
                user=request.user, 
                is_active=True
            ).select_related('language')
            
            # Ajouter les informations des langues actives
            active_languages_info = []
            for ul in user_languages:
                active_languages_info.append({
                    'code': ul.language.code,
                    'name': ul.language.name,
                    'flag': ul.language.flag_emoji,
                    'proficiency_level': ul.proficiency_level,
                    'daily_goal': ul.daily_goal,
                    'streak_count': ul.streak_count,
                    'progress_percentage': ul.progress_percentage
                })
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'settings': settings,
                    'active_languages': active_languages_info
                })
            else:
                # Use standardized context mixin
                mixin = SettingsContextMixin()
                context = mixin.get_settings_context(
                    user=request.user,
                    active_tab_id='language_learning',
                    page_title='Apprentissage des Langues',
                    page_subtitle='Configurez vos préférences d\'apprentissage et objectifs'
                )
                
                # Add Language Learning specific data
                context.update({
                    'title': gettext('Paramètres Apprentissage des Langues - Linguify'),
                    'language_learning_settings': settings,
                    'active_languages': active_languages_info,
                    'available_learning_methods': [
                        ('flashcards', 'Cartes mémoire'),
                        ('listening', 'Écoute'),
                        ('speaking', 'Expression orale'),
                        ('reading', 'Lecture'),
                        ('writing', 'Écriture'),
                        ('grammar', 'Grammaire'),
                        ('vocabulary', 'Vocabulaire')
                    ],
                    'difficulty_levels': [
                        ('easy', 'Facile'),
                        ('normal', 'Normal'),
                        ('hard', 'Difficile'),
                        ('adaptive', 'Adaptatif')
                    ],
                    'reminder_frequencies': [
                        ('daily', 'Quotidien'),
                        ('weekdays', 'Jours de semaine'),
                        ('custom', 'Personnalisé')
                    ]
                })
                
                return render(request, 'saas_web/settings/settings.html', context)
            
        except Exception as e:
            logger.error(f"Error in LanguageLearningSettingsView GET: {e}")
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': gettext('Erreur lors de la récupération des paramètres')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                messages.error(request, gettext("Erreur lors du chargement des paramètres d'apprentissage"))
                return redirect('saas_web:settings')
    
    def post(self, request):
        """Traite la mise à jour des paramètres d'apprentissage des langues"""
        try:
            # Check if it's an AJAX request
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
            # Parse form data with validation
            try:
                daily_goal_minutes = int(request.POST.get('daily_goal_minutes', '15'))
                weekly_goal_days = int(request.POST.get('weekly_goal_days', '5'))
                audio_playback_speed = float(request.POST.get('audio_playback_speed', '1.0'))
            except (ValueError, TypeError):
                raise ValueError("Valeurs numériques invalides dans les paramètres")
            
            # Validation des données
            if daily_goal_minutes < 5 or daily_goal_minutes > 300:
                raise ValueError("L'objectif quotidien doit être entre 5 et 300 minutes")
            
            if weekly_goal_days < 1 or weekly_goal_days > 7:
                raise ValueError("L'objectif hebdomadaire doit être entre 1 et 7 jours")
            
            if not (0.5 <= audio_playback_speed <= 2.0):
                raise ValueError("La vitesse audio doit être entre 0.5 et 2.0")
            
            # Get or create the settings model
            language_learning_settings, created = LanguageLearningSettings.objects.get_or_create(
                user=request.user
            )
            
            # Update settings in database
            language_learning_settings.preferred_study_time = timezone.datetime.strptime(
                request.POST.get('preferred_study_time', '18:00'), '%H:%M'
            ).time()
            language_learning_settings.daily_goal_minutes = daily_goal_minutes
            language_learning_settings.weekly_goal_days = weekly_goal_days
            language_learning_settings.reminder_enabled = request.POST.get('reminder_enabled') == 'on'
            language_learning_settings.reminder_frequency = request.POST.get('reminder_frequency', 'daily')
            language_learning_settings.streak_notifications = request.POST.get('streak_notifications') == 'on'
            language_learning_settings.achievement_notifications = request.POST.get('achievement_notifications') == 'on'
            language_learning_settings.auto_difficulty_adjustment = request.POST.get('auto_difficulty_adjustment') == 'on'
            language_learning_settings.preferred_difficulty = request.POST.get('preferred_difficulty', 'adaptive')
            language_learning_settings.show_pronunciation_hints = request.POST.get('show_pronunciation_hints') == 'on'
            language_learning_settings.enable_audio_playback = request.POST.get('enable_audio_playback') == 'on'
            language_learning_settings.audio_playback_speed = audio_playback_speed
            language_learning_settings.show_progress_animations = request.POST.get('show_progress_animations') == 'on'
            language_learning_settings.font_size = request.POST.get('font_size', 'medium')
            
            language_learning_settings.save()
            
            # Mettre à jour la langue cible dans le profil utilisateur si différente
            target_language = request.POST.get('target_language', request.user.target_language or 'EN')
            if target_language != request.user.target_language:
                request.user.target_language = target_language
                request.user.save(update_fields=['target_language'])
                logger.info(f"Updated target language for user {request.user.username}: {target_language}")
            
            logger.info(f"Language learning settings updated in database for user {request.user.username}")
            
            # Create response data
            data = {
                'preferred_study_time': language_learning_settings.preferred_study_time.strftime('%H:%M'),
                'daily_goal_minutes': language_learning_settings.daily_goal_minutes,
                'weekly_goal_days': language_learning_settings.weekly_goal_days,
                'target_language': target_language,
            }
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': gettext("Paramètres d'apprentissage des langues mis à jour avec succès"),
                    'data': data
                })
            else:
                messages.success(request, gettext("Paramètres d'apprentissage des langues mis à jour avec succès"))
                return redirect('saas_web:settings')
                
        except ValueError as e:
            # Handle validation errors
            logger.error(f"Validation error in language learning settings: {e}")
            error_message = str(e)
            
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': error_message
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                messages.error(request, error_message)
                return redirect('saas_web:settings')
                
        except Exception as e:
            logger.error(f"Error in LanguageLearningSettingsView POST: {e}")
            error_message = gettext("Erreur lors de la mise à jour des paramètres d'apprentissage")
            
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': error_message
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                messages.error(request, error_message)
                return redirect('saas_web:settings')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_language_learning_settings(request):
    """
    Récupère les paramètres d'apprentissage des langues de l'utilisateur
    """
    try:
        # Récupérer depuis la session
        session_key = f'language_learning_settings_{request.user.id}'
        settings = request.session.get(session_key, {
            'daily_goal_minutes': 15,
            'weekly_goal_days': 5,
            'preferred_difficulty': 'adaptive',
            'enable_audio_playback': True,
            'audio_playback_speed': 1.0,
            'learning_methods': ['flashcards', 'vocabulary'],
            'reminder_enabled': True,
            'target_language': request.user.target_language or 'EN'
        })
        
        # Ajouter les informations des langues actives
        user_languages = UserLanguage.objects.filter(
            user=request.user, 
            is_active=True
        ).select_related('language')
        
        active_languages = []
        for ul in user_languages:
            active_languages.append({
                'code': ul.language.code,
                'name': ul.language.name,
                'proficiency_level': ul.proficiency_level,
                'progress_percentage': ul.progress_percentage,
                'streak_count': ul.streak_count,
                'daily_goal': ul.daily_goal
            })
        
        logger.info(f"Retrieved language learning settings for {request.user.username}")
        
        return Response({
            'success': True,
            'settings': settings,
            'active_languages': active_languages
        })
        
    except Exception as e:
        logger.error(f"Error getting language learning settings: {e}")
        return Response({
            'success': False,
            'error': str(e),
            'settings': {
                'daily_goal_minutes': 15,
                'weekly_goal_days': 5,
                'preferred_difficulty': 'adaptive',
                'enable_audio_playback': True,
                'audio_playback_speed': 1.0,
                'learning_methods': ['flashcards', 'vocabulary'],
                'reminder_enabled': True
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# API REST (JSON)
# =============================================================================

class LanguageLearningSettingsViewSet(viewsets.ViewSet):
    """
    API REST pour gérer les paramètres d'apprentissage des langues
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Récupère les paramètres d'apprentissage de l'utilisateur"""
        try:
            session_key = f'language_learning_settings_{request.user.id}'
            settings = request.session.get(session_key, {})
            
            # Paramètres par défaut si aucun n'est défini
            default_settings = {
                'preferred_study_time': '18:00',
                'daily_goal_minutes': 15,
                'weekly_goal_days': 5,
                'reminder_enabled': True,
                'reminder_frequency': 'daily',
                'auto_difficulty_adjustment': True,
                'preferred_difficulty': 'adaptive',
                'enable_audio_playback': True,
                'audio_playback_speed': 1.0,
                'learning_methods': ['flashcards', 'vocabulary', 'listening'],
                'target_language': request.user.target_language or 'EN'
            }
            
            # Merger les paramètres par défaut avec ceux enregistrés
            final_settings = {**default_settings, **settings}
            
            serializer = LanguageLearningSettingsSerializer(data=final_settings)
            if serializer.is_valid():
                return Response(serializer.data)
            else:
                return Response(final_settings)
                
        except Exception as e:
            logger.error(f"Error retrieving language learning settings: {e}")
            return Response(
                {'error': 'Erreur lors de la récupération des paramètres'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def update(self, request, pk=None):
        """Met à jour les paramètres d'apprentissage"""
        try:
            serializer = LanguageLearningSettingsSerializer(data=request.data)
            
            if serializer.is_valid():
                # Sauvegarder en session
                session_key = f'language_learning_settings_{request.user.id}'
                request.session[session_key] = serializer.validated_data
                
                # Mettre à jour la langue cible si nécessaire
                target_language = serializer.validated_data.get('target_language')
                if target_language and target_language != request.user.target_language:
                    request.user.target_language = target_language
                    request.user.save(update_fields=['target_language'])
                
                logger.info(f"Updated language learning settings for user {request.user.username}")
                return Response({
                    'success': True,
                    'message': 'Paramètres mis à jour avec succès',
                    'settings': serializer.validated_data
                })
            else:
                return Response({
                    'success': False,
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error updating language learning settings: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def apply_preset(self, request):
        """Applique un preset de configuration d'apprentissage"""
        serializer = ApplyLanguageLearningPresetSerializer(data=request.data)
        
        if serializer.is_valid():
            preset_name = serializer.validated_data['preset_name']
            
            logger.info(f"Applying language learning preset '{preset_name}' for user {request.user.username}")
            
            # Définir les presets
            presets = {
                'casual': {
                    'daily_goal_minutes': 10,
                    'weekly_goal_days': 3,
                    'preferred_difficulty': 'easy',
                    'auto_difficulty_adjustment': True,
                    'reminder_frequency': 'custom',
                    'learning_methods': ['flashcards', 'vocabulary']
                },
                'regular': {
                    'daily_goal_minutes': 15,
                    'weekly_goal_days': 5,
                    'preferred_difficulty': 'normal',
                    'auto_difficulty_adjustment': True,
                    'reminder_frequency': 'weekdays',
                    'learning_methods': ['flashcards', 'vocabulary', 'listening']
                },
                'intensive': {
                    'daily_goal_minutes': 30,
                    'weekly_goal_days': 6,
                    'preferred_difficulty': 'hard',
                    'auto_difficulty_adjustment': False,
                    'reminder_frequency': 'daily',
                    'learning_methods': ['flashcards', 'vocabulary', 'listening', 'grammar']
                },
                'immersion': {
                    'daily_goal_minutes': 60,
                    'weekly_goal_days': 7,
                    'preferred_difficulty': 'hard',
                    'auto_difficulty_adjustment': False,
                    'reminder_frequency': 'daily',
                    'learning_methods': ['flashcards', 'listening', 'speaking', 'reading', 'writing']
                }
            }
            
            preset_settings = presets.get(preset_name, {})
            if preset_settings:
                # Récupérer les paramètres actuels
                session_key = f'language_learning_settings_{request.user.id}'
                current_settings = request.session.get(session_key, {})
                
                # Appliquer le preset
                current_settings.update(preset_settings)
                request.session[session_key] = current_settings
                
                return Response({
                    'success': True,
                    'message': f"Preset '{preset_name}' appliqué avec succès",
                    'preset_applied': preset_name,
                    'settings': current_settings
                })
            else:
                return Response({
                    'success': False,
                    'error': f"Preset '{preset_name}' non trouvé"
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def user_languages_preferences(self, request):
        """Retourne les préférences spécifiques par langue de l'utilisateur"""
        try:
            user_languages = UserLanguage.objects.filter(
                user=request.user, 
                is_active=True
            ).select_related('language')
            
            preferences = []
            for ul in user_languages:
                # Récupérer les préférences spécifiques depuis la session
                pref_key = f'lang_preferences_{request.user.id}_{ul.language.code}'
                lang_prefs = request.session.get(pref_key, {
                    'audio_enabled': True,
                    'preferred_voice_gender': 'auto',
                    'audio_speed': 1.0,
                    'show_romanization': True,
                    'font_size': 'medium',
                    'focus_skills': ['vocabulary', 'grammar'],
                    'review_frequency': 'medium',
                    'mistake_emphasis': True
                })
                
                preferences.append({
                    'language_code': ul.language.code,
                    'language_name': ul.language.name,
                    'preferences': lang_prefs
                })
            
            return Response({
                'success': True,
                'languages_preferences': preferences
            })
            
        except Exception as e:
            logger.error(f"Error getting language preferences: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def update_language_preferences(self, request):
        """Met à jour les préférences pour une langue spécifique"""
        try:
            language_code = request.data.get('language_code')
            preferences = request.data.get('preferences', {})
            
            if not language_code:
                return Response({
                    'success': False,
                    'error': 'Code de langue requis'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Valider les préférences avec le serializer
            serializer = UserLanguagePreferencesSerializer(data={
                'language_code': language_code,
                **preferences
            })
            
            if serializer.is_valid():
                # Sauvegarder les préférences en session
                pref_key = f'lang_preferences_{request.user.id}_{language_code}'
                request.session[pref_key] = serializer.validated_data
                
                logger.info(f"Updated preferences for language {language_code} for user {request.user.username}")
                
                return Response({
                    'success': True,
                    'message': f'Préférences mises à jour pour {language_code}',
                    'preferences': serializer.validated_data
                })
            else:
                return Response({
                    'success': False,
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error updating language preferences: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)