"""
Documents settings views

IMPORTANT: Ce fichier illustre l'usage du système centralisé de paramètres.

AVANT LA REFACTORISATION (Juillet 2025):
Cette vue était intégrée manuellement avec du code dupliqué dans settings_views.py.
Le problème original était "très chiant à maintenir tout çà, quand je vais sur les settings 
de language_ai par exemple, je ne vois plus documents dans la sidebar".

APRÈS LA REFACTORISATION:
La vue utilise SettingsContextMixin pour une navigation cohérente. Désormais Documents
reste visible dans la sidebar peu importe la page de paramètres visitée.

SOLUTION TECHNIQUE:
- SettingsContextMixin génère la navigation depuis AppSettingsService
- Code simple, maintenir, et cohérent
- Toutes les apps restent visibles dans la navigation
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db.models import Q
from ..models import Document, Folder, DocumentShare
from app_manager.mixins import SettingsContextMixin
import json


@login_required
def documents_settings_view(request):
    """Documents settings page for main Linguify settings"""
    
    try:
        # EXEMPLE DE RÉSOLUTION DU PROBLÈME DE NAVIGATION:
        # Avant: hardcodage de la sidebar → Documents disparaissait sur d'autres pages
        # Après: mixin centralisé → Documents reste visible partout
        mixin = SettingsContextMixin()
        context = mixin.get_settings_context(
            user=request.user,
            active_tab_id='documents',  # Référence AppSettingsService.CORE_APP_SETTINGS
            page_title='Documents',
            page_subtitle='Gérez vos paramètres de collaboration et d\'édition'
        )
        
        # Add Documents-specific data
        user_documents_count = Document.objects.filter(owner=request.user).count()
        user_folders_count = Folder.objects.filter(owner=request.user).count()
        shared_with_user_count = Document.objects.filter(shares__user=request.user).count()
        shared_by_user_count = DocumentShare.objects.filter(shared_by=request.user).count()
        
        # Recent activity
        recent_activity = Document.objects.filter(
            Q(owner=request.user) | Q(shares__user=request.user)
        ).distinct().select_related(
            'owner', 'last_edited_by'
        ).order_by('-updated_at')[:5]
        
        # Storage usage (simplified calculation)
        total_content_length = Document.objects.filter(
            owner=request.user
        ).values_list('content', flat=True)
        storage_used_kb = sum(len(content.encode('utf-8')) for content in total_content_length) / 1024
        
        # Update context with Documents data
        context.update({
            'title': 'Paramètres Documents - Linguify',
            'user_documents_count': user_documents_count,
            'user_folders_count': user_folders_count,
            'shared_with_user_count': shared_with_user_count,
            'shared_by_user_count': shared_by_user_count,
            'recent_activity': recent_activity,
            'storage_used_kb': round(storage_used_kb, 2),
        })
        
        return render(request, 'saas_web/settings/settings.html', context)
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in documents_settings_view: {e}")
        messages.error(request, "Une erreur est survenue lors du chargement des paramètres Documents.")
        
        # Fallback context
        context = {
            'title': 'Paramètres Documents - Linguify',
            'user': request.user,
            'user_documents_count': 0,
            'user_folders_count': 0,
            'shared_with_user_count': 0,
            'shared_by_user_count': 0,
            'recent_activity': [],
            'storage_used_kb': 0,
        }
        return render(request, 'saas_web/settings/settings.html', context)


@login_required
@require_http_methods(["POST"])
def save_documents_settings(request):
    """Save documents settings via AJAX"""
    
    try:
        data = json.loads(request.body)
        
        # For now, we'll store settings in user session or profile
        # In a real app, you might want to create a UserDocumentsSettings model
        
        # Store in session for now
        request.session['documents_settings'] = {
            'default_content_type': data.get('defaultContentType', 'markdown'),
            'default_visibility': data.get('defaultVisibility', 'private'),
            'auto_save': data.get('autoSave', True),
            'editor_theme': data.get('editorTheme', 'light'),
            'font_size': data.get('fontSize', '14'),
            'live_preview': data.get('livePreview', True),
            'comment_notifications': data.get('commentNotifications', True),
            'share_notifications': data.get('shareNotifications', True),
            'default_permissions': data.get('defaultPermissions', 'edit'),
            'show_cursors': data.get('showCursors', True),
        }
        
        messages.success(request, 'Paramètres Documents sauvegardés avec succès!')
        
        return JsonResponse({
            'success': True,
            'message': 'Paramètres sauvegardés avec succès!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de la sauvegarde: {str(e)}'
        }, status=400)


@login_required
def get_documents_settings(request):
    """Get current documents settings"""
    
    # Get settings from session or default values
    settings = request.session.get('documents_settings', {
        'default_content_type': 'markdown',
        'default_visibility': 'private',
        'auto_save': True,
        'editor_theme': 'light',
        'font_size': '14',
        'live_preview': True,
        'comment_notifications': True,
        'share_notifications': True,
        'default_permissions': 'edit',
        'show_cursors': True,
    })
    
    return JsonResponse({
        'success': True,
        'settings': settings
    })


@login_required
@require_http_methods(["POST"])
def reset_documents_settings(request):
    """Reset documents settings to defaults"""
    
    try:
        # Remove custom settings from session
        if 'documents_settings' in request.session:
            del request.session['documents_settings']
        
        messages.info(request, 'Paramètres Documents réinitialisés aux valeurs par défaut.')
        
        return JsonResponse({
            'success': True,
            'message': 'Paramètres réinitialisés'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de la réinitialisation: {str(e)}'
        }, status=400)