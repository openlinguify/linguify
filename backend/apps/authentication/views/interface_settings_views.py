# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib import messages
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from rest_framework import status
from app_manager.mixins import SettingsContextMixin
import json
import logging

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class InterfaceSettingsView(View):
    """Handle interface and theme settings"""
    
    def get(self, request):
        """Display interface settings page"""
        
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
                # Use standardized context mixin
                mixin = SettingsContextMixin()
                context = mixin.get_settings_context(
                    user=request.user,
                    active_tab_id='interface',
                    page_title='Thème & Apparence',
                    page_subtitle='Personnalisez l\'apparence et l\'interface de Linguify'
                )
                
                # Add Interface specific data
                context.update({
                    'title': _('Interface & Thème - Linguify'),
                    'interface_settings': interface_settings,
                })
                
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