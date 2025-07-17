# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib import messages
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from rest_framework import status
import json
import logging

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class RevisionSettingsView(View):
    """Handle revision settings - wrapper for the ViewSet-based implementation"""
    
    def get(self, request):
        """Display revision settings page"""
        try:
            # Get current revision settings from user profile
            revision_settings = {}
            if hasattr(request.user, 'profile') and request.user.profile:
                revision_settings = request.user.profile.revision_settings or {}
            
            context = {
                'title': _('Révision - Linguify'),
                'user': request.user,
                'revision_settings': revision_settings,
                'active_tab': 'revision',
            }
            
            return render(request, 'revision/revision_settings.html', context)
            
        except Exception as e:
            logger.error(f"Error in RevisionSettingsView GET: {e}")
            messages.error(request, _("Erreur lors du chargement des paramètres de révision"))
            return redirect('saas_web:settings')
    
    def post(self, request):
        """Handle revision settings update"""
        try:
            # Check if it's an AJAX request
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
            # Get settings from POST data
            daily_goal = int(request.POST.get('daily_goal', '10'))
            reminder_enabled = request.POST.get('reminder_enabled', 'true') == 'true'
            reminder_time = request.POST.get('reminder_time', '09:00')
            spaced_repetition = request.POST.get('spaced_repetition', 'true') == 'true'
            difficulty_adaptation = request.POST.get('difficulty_adaptation', 'true') == 'true'
            session_duration = int(request.POST.get('session_duration', '15'))
            
            # Prepare settings data
            revision_settings = {
                'daily_goal': daily_goal,
                'reminder_enabled': reminder_enabled,
                'reminder_time': reminder_time,
                'spaced_repetition': spaced_repetition,
                'difficulty_adaptation': difficulty_adaptation,
                'session_duration': session_duration,
            }
            
            # Update user profile
            if hasattr(request.user, 'profile') and request.user.profile:
                request.user.profile.revision_settings = revision_settings
                request.user.profile.save(update_fields=['revision_settings'])
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': _("Paramètres de révision mis à jour avec succès")
                })
            else:
                messages.success(request, _("Paramètres de révision mis à jour avec succès"))
                return redirect('saas_web:revision_settings')
                
        except Exception as e:
            logger.error(f"Error in RevisionSettingsView POST: {e}")
            
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                messages.error(request, _("Erreur lors de la mise à jour des paramètres"))
                return redirect('saas_web:revision_settings')
            
"""
Vue pour récupérer les paramètres utilisateur dans l'app révision
"""
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods


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
        })
        
        print(f"[USER_SETTINGS] Retrieved settings for {request.user.username}: {settings}")
        
        return JsonResponse({
            'success': True,
            'settings': settings
        })
        
    except Exception as e:
        print(f"[USER_SETTINGS] Error: {e}")
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
            }
        })


