"""
Notebook settings views
"""
from django.http import JsonResponse
from django.contrib import messages
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from rest_framework import status
from ..serializers import NotebookSettingsSerializer
import logging

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class NotebookSettingsView(View):
    """Handle notebook settings for the user"""
    
    def post(self, request):
        """Handle notebook settings update"""
        try:
            # Check if it's an AJAX request
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
            # Parse form data for serializer
            data = {
                'auto_save': request.POST.get('auto_save') == 'on',
                'auto_sync': request.POST.get('auto_sync') == 'on',
                'default_format': request.POST.get('default_format', 'markdown'),
                'theme': request.POST.get('theme', 'light'),
                'font_size': int(request.POST.get('font_size', 14)),
                'line_numbers': request.POST.get('line_numbers') == 'on',
                'word_wrap': request.POST.get('word_wrap') == 'on',
                'spell_check': request.POST.get('spell_check') == 'on',
                'backup_frequency': request.POST.get('backup_frequency', 'daily'),
                'export_format': request.POST.get('export_format', 'pdf'),
                'enable_collaboration': request.POST.get('enable_collaboration') == 'on',
                'privacy_mode': request.POST.get('privacy_mode', 'private'),
            }
            
            # Validate with serializer
            serializer = NotebookSettingsSerializer(data=data)
            if not serializer.is_valid():
                error_message = 'Erreur de validation: ' + str(serializer.errors)
                logger.error(f"Validation errors in notebook settings: {serializer.errors}")
                
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'errors': serializer.errors,
                        'message': error_message
                    }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    messages.error(request, error_message)
                    return redirect('saas_web:settings')
            
            # Store validated notebook settings
            validated_data = serializer.validated_data
            
            # TODO: Consider creating a dedicated NotebookUserSettings model
            # For now, store in user session since Profile model doesn't have notebook_settings field
            session_key = f'notebook_settings_{request.user.id}'
            request.session[session_key] = validated_data
            logger.info(f"Notebook settings updated for user {request.user.id} (stored in session)")
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': 'Paramètres de carnet mis à jour avec succès',
                    'data': validated_data
                })
            else:
                messages.success(request, 'Paramètres de carnet mis à jour avec succès')
                return redirect('saas_web:settings')
                
        except ValueError as e:
            # Handle conversion errors
            logger.error(f"Value error in notebook settings: {e}")
            error_message = "Valeur invalide dans les paramètres"
            
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': error_message
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                messages.error(request, error_message)
                return redirect('saas_web:settings')
                
        except Exception as e:
            logger.error(f"Error in notebook settings update: {e}")
            error_message = 'Erreur lors de la mise à jour des paramètres de carnet'
            
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': error_message
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                messages.error(request, error_message)
                return redirect('saas_web:settings')
    
    def get(self, request):
        """Display notebook settings page"""
        from django.shortcuts import render
        
        try:
            # Check if it's an AJAX request for getting settings as JSON
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
            # Get settings from session since Profile model doesn't have notebook_settings field
            session_key = f'notebook_settings_{request.user.id}'
            settings = request.session.get(session_key, {})
            
            if not settings:
                # Return default settings
                settings = {
                    'auto_save': True,
                    'auto_sync': True,
                    'default_format': 'markdown',
                    'theme': 'light',
                    'font_size': 14,
                    'line_numbers': False,
                    'word_wrap': True,
                    'spell_check': True,
                    'backup_frequency': 'daily',
                    'export_format': 'pdf',
                    'enable_collaboration': False,
                    'privacy_mode': 'private',
                }
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'settings': settings
                })
            else:
                # Complete context with full sidebar
                context = {
                    'title': 'Paramètres Carnet - Linguify',
                    'user': request.user,
                    'notebook_settings': settings,
                    'active_tab': 'notebook',
                    'page_title': 'Notes & Carnet',
                    'page_subtitle': 'Configurez votre espace de prise de notes et d\'organisation',
                    'breadcrumb_active': 'Notes & Carnet',
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
                                {'id': 'notebook', 'name': 'Notes', 'icon': 'bi-journal-text', 'active': True},
                                {'id': 'quiz', 'name': 'Quiz', 'icon': 'bi-question-circle', 'active': False},
                                {'id': 'revision', 'name': 'Révision', 'icon': 'bi-arrow-repeat', 'active': False},
                                {'id': 'language_ai', 'name': 'IA Linguistique', 'icon': 'bi-cpu', 'active': False}
                            ]
                        }
                    },
                    'settings_tabs': [
                        {'id': 'notebook', 'name': 'Notes', 'icon': 'bi-journal-text', 'active': True}
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
                
                # Add the notebook settings content
                from django.template.loader import render_to_string
                
                try:
                    notebook_content = render_to_string('notebook/notebook_content.html', {
                        'notebook_settings': settings
                    }, request=request)
                    context['notebook_content'] = notebook_content
                except Exception as e:
                    logger.error(f"Error loading notebook template: {e}")
                    context['notebook_content'] = """
                    <div class="content-section">
                        <h3>Paramètres de carnet</h3>
                        <p>Erreur lors du chargement du template: """ + str(e) + """</p>
                    </div>
                    """
                
                return render(request, 'saas_web/settings/settings.html', context)
                
        except Exception as e:
            logger.error(f"Error retrieving notebook settings: {e}")
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': 'Erreur lors de la récupération des paramètres'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                messages.error(request, "Erreur lors du chargement des paramètres de carnet")
                return redirect('saas_web:settings')