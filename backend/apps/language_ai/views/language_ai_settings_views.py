# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib import messages
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from rest_framework import status
from app_manager.mixins import SettingsContextMixin
import json
import logging

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class LanguageAISettingsView(View):
    """Handle Language AI settings"""
    
    def get(self, request):
        """Display Language AI settings page"""
        try:
            # Check if it's an AJAX request for getting settings as JSON
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
            # Get settings from session since Profile model doesn't have language_ai_settings field
            session_key = f'language_ai_settings_{request.user.id}'
            settings = request.session.get(session_key, {})
            
            if not settings:
                # Return default settings
                settings = {
                    'ai_model': 'gpt-3.5-turbo',
                    'response_style': 'balanced',
                    'auto_correct': True,
                    'grammar_check': True,
                    'translation_enabled': True,
                    'context_learning': True,
                    'difficulty_level': 'intermediate',
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
                    active_tab_id='language_ai',
                    page_title='IA Linguistique',
                    page_subtitle='Configurez votre assistant IA pour l\'apprentissage des langues'
                )
                
                # Add Language AI specific data
                context.update({
                    'title': _('Paramètres IA Linguistique - Linguify'),
                    'language_ai_settings': settings,
                })
                
                
                return render(request, 'saas_web/settings/settings.html', context)
            
        except Exception as e:
            logger.error(f"Error in LanguageAISettingsView GET: {e}")
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': _('Erreur lors de la récupération des paramètres')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                messages.error(request, _("Erreur lors du chargement des paramètres IA"))
                return redirect('saas_web:settings')
    
    def post(self, request):
        """Handle Language AI settings update"""
        try:
            # Check if it's an AJAX request
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
            # Parse form data
            data = {
                'ai_model': request.POST.get('ai_model', 'gpt-3.5-turbo'),
                'response_style': request.POST.get('response_style', 'balanced'),
                'auto_correct': request.POST.get('auto_correct') == 'on',
                'grammar_check': request.POST.get('grammar_check') == 'on',
                'translation_enabled': request.POST.get('translation_enabled') == 'on',
                'context_learning': request.POST.get('context_learning') == 'on',
                'difficulty_level': request.POST.get('difficulty_level', 'intermediate'),
            }
            
            # Store validated language AI settings
            # TODO: Consider creating a dedicated LanguageAIUserSettings model
            # For now, store in user session since Profile model doesn't have language_ai_settings field
            session_key = f'language_ai_settings_{request.user.id}'
            request.session[session_key] = data
            logger.info(f"Language AI settings updated for user {request.user.id} (stored in session)")
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': _("Paramètres IA linguistique mis à jour avec succès"),
                    'data': data
                })
            else:
                messages.success(request, _("Paramètres IA linguistique mis à jour avec succès"))
                return redirect('saas_web:settings')
                
        except ValueError as e:
            # Handle conversion errors
            logger.error(f"Value error in language AI settings: {e}")
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
            logger.error(f"Error in LanguageAISettingsView POST: {e}")
            error_message = _("Erreur lors de la mise à jour des paramètres IA linguistique")
            
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': error_message
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                messages.error(request, error_message)
                return redirect('saas_web:settings')