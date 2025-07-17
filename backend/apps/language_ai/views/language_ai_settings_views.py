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
class LanguageAISettingsView(View):
    """Handle Language AI settings"""
    
    def get(self, request):
        """Display Language AI settings page"""
        try:
            # Get current language AI settings from user profile
            language_ai_settings = {}
            if hasattr(request.user, 'profile') and request.user.profile:
                language_ai_settings = request.user.profile.language_ai_settings or {}
            
            context = {
                'title': _('IA Linguistique - Linguify'),
                'user': request.user,
                'language_ai_settings': language_ai_settings,
                'active_tab': 'language_ai',
            }
            
            return render(request, 'language_ai/language_ai_settings.html', context)
            
        except Exception as e:
            logger.error(f"Error in LanguageAISettingsView GET: {e}")
            messages.error(request, _("Erreur lors du chargement des paramètres IA"))
            return redirect('saas_web:settings')
    
    def post(self, request):
        """Handle Language AI settings update"""
        try:
            # Check if it's an AJAX request
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
            # Get settings from POST data
            ai_model = request.POST.get('ai_model', 'gpt-3.5-turbo')
            response_style = request.POST.get('response_style', 'balanced')
            auto_correct = request.POST.get('auto_correct', 'true') == 'true'
            grammar_check = request.POST.get('grammar_check', 'true') == 'true'
            translation_enabled = request.POST.get('translation_enabled', 'true') == 'true'
            context_learning = request.POST.get('context_learning', 'true') == 'true'
            difficulty_level = request.POST.get('difficulty_level', 'intermediate')
            
            # Prepare settings data
            language_ai_settings = {
                'ai_model': ai_model,
                'response_style': response_style,
                'auto_correct': auto_correct,
                'grammar_check': grammar_check,
                'translation_enabled': translation_enabled,
                'context_learning': context_learning,
                'difficulty_level': difficulty_level,
            }
            
            # Update user profile
            if hasattr(request.user, 'profile') and request.user.profile:
                request.user.profile.language_ai_settings = language_ai_settings
                request.user.profile.save(update_fields=['language_ai_settings'])
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': _("Paramètres IA linguistique mis à jour avec succès")
                })
            else:
                messages.success(request, _("Paramètres IA linguistique mis à jour avec succès"))
                return redirect('saas_web:language_ai_settings')
                
        except Exception as e:
            logger.error(f"Error in LanguageAISettingsView POST: {e}")
            
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                messages.error(request, _("Erreur lors de la mise à jour des paramètres"))
                return redirect('saas_web:language_ai_settings')