"""
Voice settings views
"""
from django.http import JsonResponse
from django.contrib import messages
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from rest_framework import status
from ..serializers import VoiceSettingsSerializer
import json
import logging

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class VoiceSettingsView(View):
    """Handle voice settings for the user"""
    
    def post(self, request):
        """Handle voice settings update"""
        try:
            # Check if it's an AJAX request
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
            # Parse form data for serializer
            data = {
                'speech_rate': request.POST.get('speech_rate', 'normal'),
                'voice_pitch': float(request.POST.get('voice_pitch', 1.0)),
                'mic_sensitivity': int(request.POST.get('mic_sensitivity', 70)),
                'accent': request.POST.get('accent', 'auto'),
                'noise_reduction': request.POST.get('noise_reduction') == 'on',
                'pronunciation_feedback': request.POST.get('pronunciation_feedback') == 'on',
                'continuous_conversation': request.POST.get('continuous_conversation') == 'on'
            }
            
            # Validate with serializer
            serializer = VoiceSettingsSerializer(data=data)
            if not serializer.is_valid():
                error_message = 'Erreur de validation: ' + str(serializer.errors)
                logger.error(f"Validation errors in voice settings: {serializer.errors}")
                
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'errors': serializer.errors,
                        'message': error_message
                    }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    messages.error(request, error_message)
                    return redirect('saas_web:settings')
            
            # Store validated voice settings
            validated_data = serializer.validated_data
            
            # Store voice settings in user profile
            user_profile = request.user.profile if hasattr(request.user, 'profile') else None
            if user_profile:
                user_profile.voice_settings = json.dumps(validated_data)
                user_profile.save()
                logger.info(f"Voice settings updated for user {request.user.id}")
            else:
                logger.warning(f"No user profile found for user {request.user.id}")
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': 'Paramètres vocaux mis à jour avec succès',
                    'data': validated_data
                })
            else:
                messages.success(request, 'Paramètres vocaux mis à jour avec succès')
                return redirect('saas_web:settings')
                
        except ValueError as e:
            # Handle conversion errors
            logger.error(f"Value error in voice settings: {e}")
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
            logger.error(f"Error in voice settings update: {e}")
            error_message = 'Erreur lors de la mise à jour des paramètres vocaux'
            
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': error_message
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                messages.error(request, error_message)
                return redirect('saas_web:settings')
    
    def get(self, request):
        """Get current voice settings"""
        try:
            user_profile = request.user.profile if hasattr(request.user, 'profile') else None
            
            if user_profile and user_profile.voice_settings:
                settings = json.loads(user_profile.voice_settings)
            else:
                # Return default settings
                serializer = VoiceSettingsSerializer()
                settings = {field: field_obj.default for field, field_obj in serializer.fields.items() if hasattr(field_obj, 'default')}
            
            return JsonResponse({
                'success': True,
                'settings': settings
            })
            
        except Exception as e:
            logger.error(f"Error retrieving voice settings: {e}")
            return JsonResponse({
                'success': False,
                'message': 'Erreur lors de la récupération des paramètres'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)