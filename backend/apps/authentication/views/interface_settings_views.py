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
class InterfaceSettingsView(View):
    """Handle interface and theme settings"""
    
    def get(self, request):
        """Display interface settings page"""
        from app_manager.services import UserAppService, AppSettingsService
        
        try:
            # Check if it's an AJAX request for getting settings as JSON
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
            # Get settings from session since Profile model doesn't have interface_settings field
            session_key = f'interface_settings_{request.user.id}'
            interface_settings = request.session.get(session_key, {})
            
            if not interface_settings:
                # Return default settings
                interface_settings = {
                    'theme': 'light',
                    'color_scheme': 'default',
                    'font_size': 'medium',
                    'language': 'fr',
                    'sidebar_collapsed': False,
                    'animations_enabled': True,
                }
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'settings': interface_settings
                })
            else:
                context = {
                    'title': _('Interface & Thème - Linguify'),
                    'user': request.user,
                    'interface_settings': interface_settings,
                    'active_tab': 'interface',
                    'page_title': 'Thème & Apparence',
                    'page_subtitle': 'Personnalisez l\'apparence et l\'interface de Linguify',
                    'breadcrumb_active': 'Thème & Apparence',
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
                                {'id': 'interface', 'name': 'Thème & Apparence', 'icon': 'bi-palette', 'active': True},
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
                                {'id': 'language_ai', 'name': 'IA Linguistique', 'icon': 'bi-cpu', 'active': False}
                            ]
                        }
                    },
                    'settings_tabs': [
                        {'id': 'interface', 'name': 'Thème & Apparence', 'icon': 'bi-palette', 'active': True}
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
            logger.error(f"Error in InterfaceSettingsView GET: {e}")
            messages.error(request, _("Erreur lors du chargement des paramètres d'interface"))
            return redirect('saas_web:settings')
    
    def post(self, request):
        """Handle interface settings update"""
        try:
            # Check if it's an AJAX request
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
            # Get settings from POST data
            theme = request.POST.get('theme', 'light')
            color_scheme = request.POST.get('color_scheme', 'default')
            font_size = request.POST.get('font_size', 'medium')
            language = request.POST.get('language', 'fr')
            sidebar_collapsed = request.POST.get('sidebar_collapsed', 'false') == 'true'
            animations_enabled = request.POST.get('animations_enabled', 'true') == 'true'
            
            # Prepare settings data
            interface_settings = {
                'theme': theme,
                'color_scheme': color_scheme,
                'font_size': font_size,
                'language': language,
                'sidebar_collapsed': sidebar_collapsed,
                'animations_enabled': animations_enabled,
            }
            
            # Store in session since Profile model doesn't have interface_settings field
            session_key = f'interface_settings_{request.user.id}'
            request.session[session_key] = interface_settings
            logger.info(f"Interface settings updated for user {request.user.id} (stored in session)")
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': _("Paramètres d'interface mis à jour avec succès")
                })
            else:
                messages.success(request, _("Paramètres d'interface mis à jour avec succès"))
                return redirect('saas_web:settings')
                
        except Exception as e:
            logger.error(f"Error in InterfaceSettingsView POST: {e}")
            
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                messages.error(request, _("Erreur lors de la mise à jour des paramètres"))
                return redirect('saas_web:settings')