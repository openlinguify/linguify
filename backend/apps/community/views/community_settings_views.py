"""
Community settings views

IMPORTANT: Ce fichier illustre l'usage du système centralisé de paramètres.

AVANT LA REFACTORISATION (Juillet 2025):
Cette vue hardcodait 60+ lignes de navigation sidebar, dupliquées dans toutes les autres
vues de paramètres. Naviguer vers Language AI faisait disparaître Documents de la sidebar.

APRÈS LA REFACTORISATION:
La vue utilise SettingsContextMixin qui génère automatiquement une navigation cohérente
depuis AppSettingsService. Code réduit de 60+ à 10 lignes, maintenance centralisée.

PATTERN À SUIVRE pour toute nouvelle vue de paramètres:
1. Importer SettingsContextMixin
2. Utiliser mixin.get_settings_context() au lieu de hardcoder le contexte
3. Ajouter seulement les données spécifiques à votre app
"""
from django.http import JsonResponse
from django.contrib import messages
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from rest_framework import status
from ..serializers import CommunitySettingsSerializer
from app_manager.mixins import SettingsContextMixin
import json
import logging

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class CommunitySettingsView(View):
    """Handle community settings for the user"""
    
    def post(self, request):
        """Handle community settings update"""
        try:
            # Check if it's an AJAX request
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
            # Parse form data for serializer
            data = {
                'community_notifications': request.POST.get('community_notifications') == 'on',
                'mention_notifications': request.POST.get('mention_notifications') == 'on',
                'follow_notifications': request.POST.get('follow_notifications') == 'on',
                'post_reactions': request.POST.get('post_reactions') == 'on',
                'post_visibility': request.POST.get('post_visibility', 'public'),
                'content_moderation': request.POST.get('content_moderation', 'moderate'),
                'auto_follow_back': request.POST.get('auto_follow_back') == 'on',
                'show_activity_status': request.POST.get('show_activity_status') == 'on',
                'share_learning_progress': request.POST.get('share_learning_progress') == 'on',
                'allow_study_groups': request.POST.get('allow_study_groups') == 'on',
                'digest_frequency': request.POST.get('digest_frequency', 'weekly')
            }
            
            # Validate with serializer
            serializer = CommunitySettingsSerializer(data=data)
            if not serializer.is_valid():
                error_message = 'Erreur de validation: ' + str(serializer.errors)
                logger.error(f"Validation errors in community settings: {serializer.errors}")
                
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'errors': serializer.errors,
                        'message': error_message
                    }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    messages.error(request, error_message)
                    return redirect('saas_web:settings')
            
            # Store validated community settings
            validated_data = serializer.validated_data
            
            # TODO: Consider creating a dedicated CommunityUserSettings model
            # For now, store in user session since Profile model doesn't have community_settings field
            session_key = f'community_settings_{request.user.id}'
            request.session[session_key] = validated_data
            logger.info(f"Community settings updated for user {request.user.id} (stored in session)")
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': 'Paramètres de communauté mis à jour avec succès',
                    'data': validated_data
                })
            else:
                messages.success(request, 'Paramètres de communauté mis à jour avec succès')
                return redirect('saas_web:settings')
                
        except ValueError as e:
            # Handle conversion errors
            logger.error(f"Value error in community settings: {e}")
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
            logger.error(f"Error in community settings update: {e}")
            error_message = 'Erreur lors de la mise à jour des paramètres de communauté'
            
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': error_message
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                messages.error(request, error_message)
                return redirect('saas_web:settings')
    
    def get(self, request):
        """Display community settings page"""
        from django.shortcuts import render
        from app_manager.services import UserAppService, AppSettingsService
        
        try:
            # Check if it's an AJAX request for getting settings as JSON
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
            # Get settings from session since Profile model doesn't have community_settings field
            session_key = f'community_settings_{request.user.id}'
            settings = request.session.get(session_key, {})
            
            if not settings:
                # Return default settings
                serializer = CommunitySettingsSerializer()
                settings = {field: field_obj.default for field, field_obj in serializer.fields.items() if hasattr(field_obj, 'default')}
            
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
                    active_tab_id='community',
                    page_title='Communauté',
                    page_subtitle='Gérez vos paramètres de partage et d\'interaction communautaire'
                )
                
                # Add Community specific data
                context.update({
                    'title': 'Paramètres Communauté - Linguify',
                    'community_settings': settings,
                })
                
                return render(request, 'saas_web/settings/settings.html', context)
                
        except Exception as e:
            logger.error(f"Error retrieving community settings: {e}")
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': 'Erreur lors de la récupération des paramètres'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                messages.error(request, "Erreur lors du chargement des paramètres de communauté")
                return redirect('saas_web:settings')