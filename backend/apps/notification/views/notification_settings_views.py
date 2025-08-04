"""
Notification settings views
"""
from django.http import JsonResponse
from django.contrib import messages
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from rest_framework import status
from ..serializers import NotificationSettingsSerializer
import logging

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class NotificationSettingsView(View):
    """Handle notification settings for the user"""
    
    def post(self, request):
        """Handle notification settings update"""
        try:
            # Check if it's an AJAX request
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
            serializer = NotificationSettingsSerializer(instance=request.user, data=request.POST)
            if serializer.is_valid():
                serializer.save()
                
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'message': 'Paramètres de notification mis à jour avec succès'
                    })
                else:
                    messages.success(request, 'Paramètres de notification mis à jour avec succès')
                    return redirect('saas_web:settings')
            
            logger.error(f"Validation errors in notification settings: {serializer.errors}")
            
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                messages.error(request, 'Erreur lors de la mise à jour des paramètres de notification')
                return redirect('saas_web:settings')
                
        except Exception as e:
            logger.error(f"Error in notification settings update: {e}")
            
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': 'Erreur lors de la mise à jour des paramètres de notification'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                messages.error(request, 'Erreur lors de la mise à jour des paramètres')
                return redirect('saas_web:settings')
    
    def get(self, request):
        """Get current notification settings"""
        try:
            serializer = NotificationSettingsSerializer(instance=request.user)
            
            return JsonResponse({
                'success': True,
                'settings': serializer.data
            })
            
        except Exception as e:
            logger.error(f"Error retrieving notification settings: {e}")
            return JsonResponse({
                'success': False,
                'message': 'Erreur lors de la récupération des paramètres'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)