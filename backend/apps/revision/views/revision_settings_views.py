# -*- coding: utf-8 -*-
"""
Vues unifiées pour les paramètres de révision - Interface web et API REST
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib import messages
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Count, Avg, Sum
from datetime import timedelta

# REST Framework imports
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# App specific imports
from app_manager.mixins import SettingsContextMixin
from ..models.settings_models import RevisionSettings, RevisionSessionConfig
from ..serializers.settings_serializers import (
    RevisionSettingsSerializer, 
    RevisionSessionConfigSerializer,
    ApplyPresetSerializer,
    RevisionStatsSerializer
)

import json
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# INTERFACE WEB DJANGO (Pages HTML)
# =============================================================================

@method_decorator(login_required, name='dispatch')
class RevisionSettingsView(View):
    """Interface web pour les paramètres de révision"""
    
    def get(self, request):
        """Affiche la page des paramètres de révision"""
        try:
            # Check if it's an AJAX request for getting settings as JSON
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
            # Get settings from session since Profile model doesn't have revision_settings field
            session_key = f'revision_settings_{request.user.id}'
            settings = request.session.get(session_key, {})
            
            if not settings:
                # Return default settings
                settings = {
                    'daily_goal': 10,
                    'reminder_enabled': True,
                    'reminder_time': '09:00',
                    'spaced_repetition': True,
                    'difficulty_adaptation': True,
                    'session_duration': 15,
                    'cards_per_session': 20,
                    'default_study_mode': 'spaced',
                    'default_difficulty': 'normal',
                    'auto_advance': True,
                    'show_word_stats': True,
                    'stats_display_mode': 'detailed',
                    'hide_learned_words': False,
                    'group_by_deck': False,
                }
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'settings': settings
                })
            else:
                # Use standardized context mixin
                mixin = SettingsContextMixin()
                context = mixin.get_settings_context(
                    user=request.user,
                    active_tab_id='revision',
                    page_title='Révision',
                    page_subtitle='Configurez vos paramètres de révision et répétition espacée'
                )
                
                # Add Revision specific data
                context.update({
                    'title': _('Paramètres Révision - Linguify'),
                    'revision_settings': settings,
                })
                
                return render(request, 'saas_web/settings/settings.html', context)
            
        except Exception as e:
            logger.error(f"Error in RevisionSettingsView GET: {e}")
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': _('Erreur lors de la récupération des paramètres')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                messages.error(request, _("Erreur lors du chargement des paramètres de révision"))
                return redirect('saas_web:settings')
    
    def post(self, request):
        """Traite la mise à jour des paramètres de révision"""
        try:
            # Check if it's an AJAX request
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
            # Check if this is a word_stats specific form
            setting_type = request.POST.get('setting_type', 'revision')
            
            if setting_type == 'word_stats':
                # Handle word stats settings separately
                session_key = f'revision_settings_{request.user.id}'
                current_settings = request.session.get(session_key, {})
                
                # Update only word stats settings
                current_settings.update({
                    'show_word_stats': request.POST.get('show_word_stats') == 'on',
                    'stats_display_mode': request.POST.get('stats_display_mode', 'detailed'),
                    'hide_learned_words': request.POST.get('hide_learned_words') == 'on',
                    'group_by_deck': request.POST.get('group_by_deck') == 'on',
                })
                
                request.session[session_key] = current_settings
                data = current_settings
            elif setting_type == 'notifications':
                # Handle notification settings - update User model
                user = request.user
                
                # Update the User model's notification fields
                reminder_time_str = request.POST.get('reminder_time', '18:00')
                weekday_reminders = request.POST.get('weekday_reminders') == 'on'
                
                try:
                    from datetime import datetime
                    reminder_time = datetime.strptime(reminder_time_str, '%H:%M').time()
                    user.reminder_time = reminder_time
                    user.weekday_reminders = weekday_reminders
                    user.save(update_fields=['reminder_time', 'weekday_reminders'])
                    
                    # ALSO update RevisionSettings for consistency
                    revision_settings, created = RevisionSettings.objects.get_or_create(user=user)
                    revision_settings.reminder_time = reminder_time
                    revision_settings.daily_reminder_enabled = weekday_reminders
                    revision_settings.save(update_fields=['reminder_time', 'daily_reminder_enabled'])
                    
                    logger.info(f"Updated notification settings for user {user.id}: reminder_time={reminder_time}, weekday_reminders={weekday_reminders}")
                except ValueError as e:
                    logger.error(f"Invalid time format for reminder_time: {reminder_time_str}, error: {e}")
                    reminder_time = user.reminder_time  # Keep current value
                    user.weekday_reminders = weekday_reminders
                    user.save(update_fields=['weekday_reminders'])
                
                data = {
                    'reminder_time': reminder_time.strftime('%H:%M'),
                    'weekday_reminders': weekday_reminders,
                    'notification_frequency': request.POST.get('notification_frequency', 'daily'),
                }
            else:
                # Parse all form data for other settings
                data = {
                    'daily_goal': int(request.POST.get('daily_goal', '10')),
                    'reminder_enabled': request.POST.get('reminder_enabled') == 'on',
                    'reminder_time': request.POST.get('reminder_time', '09:00'),
                    'spaced_repetition': request.POST.get('spaced_repetition') == 'on',
                    'difficulty_adaptation': request.POST.get('difficulty_adaptation') == 'on',
                    'session_duration': int(request.POST.get('session_duration', '15')),
                    'cards_per_session': int(request.POST.get('cards_per_session', '20')),
                    'default_study_mode': request.POST.get('default_study_mode', 'spaced'),
                    'default_difficulty': request.POST.get('default_difficulty', 'normal'),
                    'auto_advance': request.POST.get('auto_advance') == 'on',
                    'show_word_stats': request.POST.get('show_word_stats') == 'on',
                    'stats_display_mode': request.POST.get('stats_display_mode', 'detailed'),
                    'hide_learned_words': request.POST.get('hide_learned_words') == 'on',
                    'group_by_deck': request.POST.get('group_by_deck') == 'on',
                }
            
            # Store validated revision settings
            # TODO: Consider creating a dedicated RevisionUserSettings model
            # For now, store in user session since Profile model doesn't have revision_settings field
            session_key = f'revision_settings_{request.user.id}'
            request.session[session_key] = data
            logger.info(f"Revision settings updated for user {request.user.id} (stored in session)")
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': _("Paramètres de révision mis à jour avec succès"),
                    'data': data
                })
            else:
                messages.success(request, _("Paramètres de révision mis à jour avec succès"))
                return redirect('saas_web:settings')
                
        except ValueError as e:
            # Handle conversion errors
            logger.error(f"Value error in revision settings: {e}")
            error_message = _("Valeur invalide dans les paramètres")
            
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': error_message
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                messages.error(request, error_message)
                return redirect('saas_web:settings')
                
        except Exception as e:
            logger.error(f"Error in RevisionSettingsView POST: {e}")
            error_message = _("Erreur lors de la mise à jour des paramètres de révision")
            
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': error_message
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                messages.error(request, error_message)
                return redirect('saas_web:settings')


@login_required
@require_http_methods(["GET"])
def get_user_revision_settings(request):
    """
    Récupère les paramètres de révision de l'utilisateur pour l'app révision
    """
    try:
        # Récupérer depuis la session (comme dans Settings)
        session_key = f'revision_settings_{request.user.id}'
        settings = request.session.get(session_key, {
            'cards_per_session': 20,
            'default_session_duration': 20,
            'required_reviews_to_learn': 3,
            'default_study_mode': 'spaced',
            'default_difficulty': 'normal',
            'auto_advance': True,
            'show_word_stats': True,
            'stats_display_mode': 'detailed',
            'hide_learned_words': False,
            'group_by_deck': False,
        })
        
        logger.info(f"[USER_SETTINGS] Retrieved settings for {request.user.username}: {settings}")
        
        return JsonResponse({
            'success': True,
            'settings': settings
        })
        
    except Exception as e:
        logger.error(f"[USER_SETTINGS] Error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'settings': {
                'cards_per_session': 20,
                'default_session_duration': 20,
                'required_reviews_to_learn': 3,
                'default_study_mode': 'spaced',
                'default_difficulty': 'normal',
                'auto_advance': True,
                'show_word_stats': True,
                'stats_display_mode': 'detailed',
                'hide_learned_words': False,
                'group_by_deck': False,
            }
        })


# =============================================================================
# API REST (JSON)
# =============================================================================

class RevisionSettingsViewSet(viewsets.ModelViewSet):
    """
    API REST pour gérer les paramètres de révision des utilisateurs
    """
    serializer_class = RevisionSettingsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtre les paramètres par utilisateur connecté"""
        return RevisionSettings.objects.filter(user=self.request.user)
    
    def get_object(self):
        """Récupère ou crée les paramètres pour l'utilisateur connecté"""
        settings, created = RevisionSettings.objects.get_or_create(user=self.request.user)
        if created:
            logger.info(f"Created revision settings for user {self.request.user.username}")
        return settings
    
    def list(self, request):
        """Liste les paramètres de l'utilisateur (retourne un seul objet)"""
        settings = self.get_object()
        serializer = self.get_serializer(settings)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """Récupère les paramètres (ignore pk, retourne les paramètres de l'utilisateur)"""
        return self.list(request)
    
    def update(self, request, pk=None, partial=True):
        """Met à jour les paramètres"""
        logger.info(f"Updating revision settings for user {request.user.username}")
        settings = self.get_object()
        serializer = self.get_serializer(settings, data=request.data, partial=partial)
        
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Revision settings updated successfully for user {request.user.username}")
            return Response(serializer.data)
        else:
            logger.warning(f"Revision settings update failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def create(self, request):
        """Crée les paramètres (retourne les paramètres existants ou nouvellement créés)"""
        return self.list(request)
    
    def destroy(self, request, pk=None):
        """Remet les paramètres par défaut"""
        logger.info(f"Resetting revision settings for user {request.user.username}")
        settings = self.get_object()
        
        # Sauvegarder les paramètres actuels pour le log
        old_settings = {
            'study_mode': settings.default_study_mode,
            'difficulty': settings.default_difficulty,
            'cards_per_session': settings.cards_per_session,
        }
        
        # Supprimer et recréer avec les valeurs par défaut
        settings.delete()
        new_settings = RevisionSettings.objects.create(user=request.user)
        
        logger.info(f"Revision settings reset for user {request.user.username}")
        logger.debug(f"Old settings: {old_settings}")
        
        serializer = self.get_serializer(new_settings)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def apply_preset(self, request):
        """Applique un preset de configuration"""
        serializer = ApplyPresetSerializer(data=request.data)
        
        if serializer.is_valid():
            preset_name = serializer.validated_data['preset_name']
            override = serializer.validated_data['override_user_settings']
            
            logger.info(f"Applying preset '{preset_name}' for user {request.user.username}")
            
            settings = self.get_object()
            success = settings.apply_preset(preset_name)
            
            if success:
                # Retourner les paramètres mis à jour
                response_serializer = self.get_serializer(settings)
                return Response({
                    'success': True,
                    'message': f"Preset '{preset_name}' appliqué avec succès",
                    'preset_applied': preset_name,
                    'settings': response_serializer.data
                })
            else:
                return Response({
                    'success': False,
                    'error': f"Erreur lors de l'application du preset '{preset_name}'"
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Retourne les statistiques de révision de l'utilisateur"""
        try:
            # Importer les modèles de révision pour les stats
            from ..models.revision_flashcard import FlashcardDeck, Flashcard
            
            user = request.user
            now = timezone.now()
            
            # Statistiques de base
            total_decks = FlashcardDeck.objects.filter(user=user, is_active=True).count()
            total_cards = Flashcard.objects.filter(deck__user=user, deck__is_active=True).count()
            
            # Cartes apprises (basé sur le champ learned s'il existe)
            cards_learned = Flashcard.objects.filter(
                deck__user=user,
                deck__is_active=True,
                learned=True
            ).count() if hasattr(Flashcard, 'learned') else 0
            
            # Cartes en cours
            cards_in_progress = total_cards - cards_learned
            
            # Calcul du streak (simulation pour l'instant)
            daily_streak = 0  # TODO: calculer depuis les sessions
            
            # Temps d'étude total (simulation pour l'instant)
            total_study_time = 0  # TODO: calculer depuis les sessions
            
            # Taux de succès réel basé sur les cartes apprises
            success_rate = (cards_learned / total_cards) if total_cards > 0 else 0.0
            
            # Dernière date d'étude (simulation pour l'instant)
            last_study_date = None  # TODO: calculer depuis les sessions
            
            stats_data = {
                'total_cards': total_cards,
                'cards_learned': cards_learned,
                'cards_in_progress': cards_in_progress,
                'daily_streak': daily_streak,
                'total_study_time': total_study_time,
                'average_session_duration': 0,  # TODO: calculer depuis les sessions
                'success_rate': success_rate,
                'last_study_date': last_study_date,
                'cards_by_difficulty': {
                    'easy': total_cards // 3 if total_cards > 0 else 0,
                    'normal': total_cards // 2 if total_cards > 0 else 0,
                    'hard': total_cards // 6 if total_cards > 0 else 0,
                },
                'performance_trend': [],  # TODO: calculer depuis l'historique
                'upcoming_reviews': cards_in_progress,  # Cartes non apprises à réviser
            }
            
            # Ajouter des headers pour débugger
            response = Response(stats_data)
            response['Access-Control-Allow-Origin'] = '*'
            response['Content-Type'] = 'application/json'
            return response
            
        except ImportError as e:
            logger.warning(f"Revision models not available for stats: {e}")
            return Response({
                'error': 'Statistiques non disponibles'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            logger.error(f"Error calculating revision stats: {e}")
            return Response({
                'error': 'Erreur lors du calcul des statistiques'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def test_stats(self, request):
        """Test endpoint pour vérifier que l'API fonctionne"""
        return Response({
            'message': 'API fonctionne!',
            'total_cards': 19,
            'cards_learned': 7,
            'success_rate': 0.368,
            'daily_streak': 0
        })
    
    @action(detail=False, methods=['get'])
    def session_config(self, request):
        """Retourne la configuration recommandée pour une session"""
        settings = self.get_object()
        config = settings.get_session_config()
        
        # Ajouter des informations contextuelles
        now = timezone.now()
        config.update({
            'recommended_time': now.strftime('%H:%M'),
            'optimal_duration': min(settings.default_session_duration, 25),  # Pomodoro technique
            'break_reminder': settings.default_session_duration > 20,
        })
        
        return Response(config)


class RevisionSessionConfigViewSet(viewsets.ModelViewSet):
    """
    API REST pour gérer les configurations de session de révision
    """
    serializer_class = RevisionSessionConfigSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtre les configurations par utilisateur connecté"""
        return RevisionSessionConfig.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Associe la configuration à l'utilisateur connecté"""
        logger.info(f"Creating session config for user {self.request.user.username}")
        serializer.save(user=self.request.user)
    
    def perform_update(self, serializer):
        """Log de mise à jour"""
        logger.info(f"Updating session config '{serializer.instance.name}' for user {self.request.user.username}")
        serializer.save()
    
    def perform_destroy(self, instance):
        """Log de suppression"""
        logger.info(f"Deleting session config '{instance.name}' for user {self.request.user.username}")
        super().perform_destroy(instance)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Définit cette configuration comme celle par défaut"""
        config = self.get_object()
        
        # Retirer le défaut des autres configurations
        RevisionSessionConfig.objects.filter(
            user=request.user,
            is_default=True
        ).update(is_default=False)
        
        # Définir cette configuration comme défaut
        config.is_default = True
        config.save()
        
        logger.info(f"Set default session config to '{config.name}' for user {request.user.username}")
        
        serializer = self.get_serializer(config)
        return Response({
            'success': True,
            'message': f"Configuration '{config.name}' définie par défaut",
            'config': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def default(self, request):
        """Retourne la configuration par défaut"""
        try:
            config = self.get_queryset().get(is_default=True)
            serializer = self.get_serializer(config)
            return Response(serializer.data)
        except RevisionSessionConfig.DoesNotExist:
            return Response({
                'error': 'Aucune configuration par défaut définie'
            }, status=status.HTTP_404_NOT_FOUND)