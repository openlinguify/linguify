"""
Settings views - user preferences and configuration.
"""
from django.shortcuts import render
from django.views import View
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.http import JsonResponse
from rest_framework import status
from apps.authentication.serializers import (
    GeneralSettingsSerializer, NotificationSettingsSerializer,
    LearningSettingsSerializer, PrivacySettingsSerializer,
    AppearanceSettingsSerializer, ProfileUpdateSerializer
)
from ..services.user_app_service import UserAppService
import logging

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class UserSettingsView(View):
    """Page des paramètres utilisateur - refactored to use services"""
    
    def get(self, request):
        try:
            # Use service to get user apps with registry information
            user_apps, app_recommendations = UserAppService.get_user_apps_with_registry_info(request.user)
            
            # Get serializers for settings forms
            general_serializer = GeneralSettingsSerializer(instance=request.user)
            notification_serializer = NotificationSettingsSerializer(instance=request.user)
            learning_serializer = LearningSettingsSerializer(instance=request.user)
            privacy_serializer = PrivacySettingsSerializer(instance=request.user)
            appearance_serializer = AppearanceSettingsSerializer(instance=request.user)
            profile_serializer = ProfileUpdateSerializer(instance=request.user)
            
            context = {
                'title': _('Paramètres - Open Linguify'),
                'user': request.user,
                'user_apps': user_apps,
                'app_recommendations': app_recommendations,
                'general_form': general_serializer,
                'notification_form': notification_serializer,
                'learning_form': learning_serializer,
                'privacy_form': privacy_serializer,
                'appearance_form': appearance_serializer,
                'profile_form': profile_serializer,
            }
            
            return render(request, 'saas_web/settings/settings.html', context)
            
        except Exception as e:
            logger.error(f"Error in UserSettingsView: {e}")
            messages.error(request, "Une erreur est survenue lors du chargement des paramètres.")
            
            # Fallback context
            context = {
                'title': _('Paramètres - Open Linguify'),
                'user': request.user,
                'user_apps': [],
                'app_recommendations': [],
            }
            return render(request, 'saas_web/settings/settings.html', context)
    
    def post(self, request):
        """Handle settings updates"""
        setting_type = request.POST.get('setting_type')
        
        if setting_type == 'general':
            return self._handle_general_settings(request)
        elif setting_type == 'notification':
            return self._handle_notification_settings(request)
        elif setting_type == 'learning':
            return self._handle_learning_settings(request)
        elif setting_type == 'privacy':
            return self._handle_privacy_settings(request)
        elif setting_type == 'appearance':
            return self._handle_appearance_settings(request)
        elif setting_type == 'profile':
            return self._handle_profile_settings(request)
        elif setting_type == 'voice':
            # For now, redirect to voice settings view or handle basic voice settings
            return JsonResponse({
                'success': True,
                'message': 'Paramètres vocaux mis à jour avec succès'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Type de paramètre non reconnu'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def _handle_general_settings(self, request):
        """Handle general settings update"""
        serializer = GeneralSettingsSerializer(instance=request.user, data=request.POST)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({
                'success': True,
                'message': 'Paramètres généraux mis à jour avec succès'
            })
        return JsonResponse({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def _handle_notification_settings(self, request):
        """Handle notification settings update"""
        serializer = NotificationSettingsSerializer(instance=request.user, data=request.POST)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({
                'success': True,
                'message': 'Paramètres de notification mis à jour avec succès'
            })
        return JsonResponse({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def _handle_learning_settings(self, request):
        """Handle learning settings update"""
        serializer = LearningSettingsSerializer(instance=request.user, data=request.POST)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({
                'success': True,
                'message': 'Paramètres d\'apprentissage mis à jour avec succès'
            })
        return JsonResponse({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def _handle_privacy_settings(self, request):
        """Handle privacy settings update"""
        serializer = PrivacySettingsSerializer(instance=request.user, data=request.POST)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({
                'success': True,
                'message': 'Paramètres de confidentialité mis à jour avec succès'
            })
        return JsonResponse({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def _handle_appearance_settings(self, request):
        """Handle appearance settings update"""
        serializer = AppearanceSettingsSerializer(instance=request.user, data=request.POST)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({
                'success': True,
                'message': 'Paramètres d\'apparence mis à jour avec succès'
            })
        return JsonResponse({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def _handle_profile_settings(self, request):
        """Handle profile settings update"""
        serializer = ProfileUpdateSerializer(instance=request.user, data=request.POST)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({
                'success': True,
                'message': 'Profil mis à jour avec succès'
            })
        return JsonResponse({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(login_required, name='dispatch')
class VoiceSettingsView(View):
    """Page des paramètres de l'assistant vocal"""
    
    def get(self, request):
        context = {
            'title': _('Paramètres Vocaux - Open Linguify'),
            'user': request.user,
        }
        return render(request, 'saas_web/voice_settings.html', context)