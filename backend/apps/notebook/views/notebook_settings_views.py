"""
Notebook settings views
"""
from django.http import JsonResponse
from django.contrib import messages
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect, render
from rest_framework import status
from app_manager.mixins import SettingsContextMixin
from ..serializers import NotebookSettingsSerializer
import json
import logging

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class NotebookSettingsView(SettingsContextMixin, View):
    """Handle notebook settings for the user"""

    def post(self, request):
        """Handle notebook settings update"""
        try:
            # Check if it's an AJAX request
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

            # Handle JSON data (from AJAX) or form data
            if is_ajax and request.content_type == 'application/json':
                import json
                data = json.loads(request.body)
            else:
                # Parse form data for serializer
                data = {
                    'auto_save': request.POST.get('auto_save') == 'on',
                    'markdown_preview': request.POST.get('markdown_preview') == 'on',
                    'spell_check': request.POST.get('spell_check') == 'on',
                    'version_history': request.POST.get('version_history') == 'on',
                    'font_family': request.POST.get('font_family', 'system'),
                    'font_size': request.POST.get('font_size', 'medium'),
                    'auto_save_interval': int(request.POST.get('auto_save_interval', 10)),
                    'auto_categorize': request.POST.get('auto_categorize') == 'on',
                    'show_tags': request.POST.get('show_tags') == 'on',
                    'recent_notes': request.POST.get('recent_notes') == 'on',
                    'default_view': request.POST.get('default_view', 'list'),
                    'default_sort': request.POST.get('default_sort', 'modified'),
                    'notes_per_page': int(request.POST.get('notes_per_page', 20)),
                    'allow_sharing': request.POST.get('allow_sharing') == 'on',
                    'public_notes': request.POST.get('public_notes') == 'on',
                    'collaborative_editing': request.POST.get('collaborative_editing') == 'on',
                    'default_permissions': request.POST.get('default_permissions', 'private')
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

            # Store validated notebook settings in session
            validated_data = serializer.validated_data
            session_key = f'notebook_settings_{request.user.id}'
            request.session[session_key] = validated_data
            request.session.modified = True
            logger.info(f"Notebook settings updated for user {request.user.id}")

            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': 'Paramètres des notes mis à jour avec succès',
                    'data': validated_data
                })
            else:
                messages.success(request, 'Paramètres des notes mis à jour avec succès')
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
            error_message = 'Erreur lors de la mise à jour des paramètres des notes'

            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': error_message
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                messages.error(request, error_message)
                return redirect('saas_web:settings')

    def get(self, request):
        """Display notebook settings page or return JSON for AJAX"""
        try:
            # Check if it's an AJAX request
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

            # Get settings from session
            session_key = f'notebook_settings_{request.user.id}'
            settings = request.session.get(session_key)

            if not settings:
                # Return default settings
                serializer = NotebookSettingsSerializer()
                settings = {field: field_obj.default for field, field_obj in serializer.fields.items() if hasattr(field_obj, 'default')}

            if is_ajax:
                # Return JSON for AJAX requests
                return JsonResponse({
                    'success': True,
                    'settings': settings
                })
            else:
                # Return HTML page for normal requests
                context = self.get_settings_context(
                    user=request.user,
                    active_tab_id='notes',  # ID used in the template
                    page_title='Notes',
                    page_subtitle='Configurez votre espace de prise de notes et d\'organisation'
                )

                # Add notebook-specific data
                context.update({
                    'notebook_settings': settings,
                })

                return render(request, 'saas_web/settings/settings.html', context)

        except Exception as e:
            logger.error(f"Error retrieving notebook settings: {e}")

            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': 'Erreur lors de la récupération des paramètres'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                messages.error(request, "Erreur lors du chargement des paramètres de notebook")
                return redirect('saas_web:settings')