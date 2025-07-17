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
                # Complete context with full sidebar
                context = {
                    'title': _('Paramètres IA Linguistique - Linguify'),
                    'user': request.user,
                    'language_ai_settings': settings,
                    'active_tab': 'language_ai',
                    'page_title': 'IA Linguistique',
                    'page_subtitle': 'Configurez votre assistant IA pour l\'apprentissage des langues',
                    'breadcrumb_active': 'IA Linguistique',
                    'settings_categories': {
                        'personal': {
                            'name': 'Personnel',
                            'icon': 'bi-person',
                            'order': 1,
                            'tabs': [
                                {'id': 'profile', 'name': 'Profil & Compte', 'icon': 'bi-person-circle', 'active': False}
                            ]
                        },
                        'interface': {
                            'name': 'Interface',
                            'icon': 'bi-palette',
                            'order': 2,
                            'tabs': [
                                {'id': 'interface', 'name': 'Thème & Apparence', 'icon': 'bi-palette', 'active': False},
                                {'id': 'voice', 'name': 'Assistant Vocal', 'icon': 'bi-mic', 'active': False}
                            ]
                        },
                        'applications': {
                            'name': 'Applications',
                            'icon': 'bi-grid-3x3-gap',
                            'order': 3,
                            'tabs': [
                                {'id': 'learning', 'name': 'Apprentissage', 'icon': 'bi-book', 'active': False},
                                {'id': 'chat', 'name': 'Chat', 'icon': 'bi-chat-dots', 'active': False},
                                {'id': 'community', 'name': 'Communauté', 'icon': 'bi-people', 'active': False},
                                {'id': 'notebook', 'name': 'Notes', 'icon': 'bi-journal-text', 'active': False},
                                {'id': 'quiz', 'name': 'Quiz', 'icon': 'bi-question-circle', 'active': False},
                                {'id': 'revision', 'name': 'Révision', 'icon': 'bi-arrow-repeat', 'active': False},
                                {'id': 'language_ai', 'name': 'IA Linguistique', 'icon': 'bi-cpu', 'active': True}
                            ]
                        }
                    },
                    'settings_tabs': [
                        {'id': 'language_ai', 'name': 'IA Linguistique', 'icon': 'bi-cpu', 'active': True}
                    ],
                    'settings_urls': {
                        'profile': '/settings/profile/',
                        'interface': '/settings/interface/',
                        'voice': '/settings/voice/',
                        'vocal': '/settings/voice/',
                        'learning': '/settings/learning/',
                        'chat': '/settings/chat/',
                        'community': '/settings/community/',
                        'notebook': '/settings/notebook/',
                        'notes': '/settings/notebook/',
                        'quiz': '/settings/quiz/',
                        'quizz': '/settings/quiz/',
                        'revision': '/settings/revision/',
                        'language_ai': '/settings/language-ai/',
                        'language-ai': '/settings/language-ai/',
                        'notifications': '/settings/notifications/',
                        'notification': '/settings/notifications/',
                    }
                }
                
                
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