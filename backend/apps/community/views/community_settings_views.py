"""
Community settings views
"""
from django.http import JsonResponse
from django.contrib import messages
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from rest_framework import status
from ..serializers import CommunitySettingsSerializer
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
            # For now, store in user profile
            user_profile = request.user.profile if hasattr(request.user, 'profile') else None
            if user_profile:
                user_profile.community_settings = json.dumps(validated_data)
                user_profile.save()
                logger.info(f"Community settings updated for user {request.user.id}")
            else:
                logger.warning(f"No user profile found for user {request.user.id}")
            
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
        """Get current community settings"""
        try:
            user_profile = request.user.profile if hasattr(request.user, 'profile') else None
            
            if user_profile and user_profile.community_settings:
                settings = json.loads(user_profile.community_settings)
            else:
                # Return default settings
                serializer = CommunitySettingsSerializer()
                settings = {field: field_obj.default for field, field_obj in serializer.fields.items() if hasattr(field_obj, 'default')}
            
            return JsonResponse({
                'success': True,
                'settings': settings
            })
            
        except Exception as e:
            logger.error(f"Error retrieving community settings: {e}")
            return JsonResponse({
                'success': False,
                'message': 'Erreur lors de la récupération des paramètres'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)