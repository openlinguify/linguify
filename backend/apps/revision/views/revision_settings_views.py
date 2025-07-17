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
                }
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'settings': settings
                })
            else:
                # Simplified context with proper navigation
                context = {
                    'title': _('Paramètres Révision - Linguify'),
                    'user': request.user,
                    'revision_settings': settings,
                    'active_tab': 'revision',
                    'page_title': 'Révision',
                    'page_subtitle': 'Configurez vos paramètres de révision et répétition espacée',
                    'breadcrumb_active': 'Révision',
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
                                {'id': 'revision', 'name': 'Révision', 'icon': 'bi-arrow-repeat', 'active': True},
                                {'id': 'language_ai', 'name': 'IA Linguistique', 'icon': 'bi-cpu', 'active': False}
                            ]
                        }
                    },
                    'settings_tabs': [
                        {'id': 'revision', 'name': 'Révision', 'icon': 'bi-arrow-repeat', 'active': True}
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
                
                # Add the revision settings content using your original template
                from django.template.loader import render_to_string
                
                try:
                    revision_content = render_to_string('revision/revision_content.html', {
                        'revision_settings': settings
                    }, request=request)
                    context['revision_content'] = revision_content
                except Exception as e:
                    logger.error(f"Error loading revision template: {e}")
                    context['revision_content'] = """
                    <div class="content-section">
                        <h3>Paramètres de révision</h3>
                        <p>Erreur lors du chargement du template de révision: """ + str(e) + """</p>
                    </div>
                    """
                
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
        """Handle revision settings update"""
        try:
            # Check if it's an AJAX request
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
            # Parse form data
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


