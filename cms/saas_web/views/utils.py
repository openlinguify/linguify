"""
Utility views and functions for SaaS web app.
"""
import json
import logging
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


@require_http_methods(["GET"])
def check_username_availability(request):
    """API endpoint pour vérifier la disponibilité d'un nom d'utilisateur"""
    username = request.GET.get('username', '').strip()
    
    # Import centralized validation function
    from apps.authentication.utils.validators import is_username_available
    
    # Special case: if it's the current user's username, it's available for them
    exclude_user = request.user if request.user.is_authenticated else None
    if request.user.is_authenticated and username.lower() == request.user.username.lower():
        return JsonResponse({
            'available': True,
            'message': 'Current username.'
        })
    
    # Use centralized validation
    result = is_username_available(username, exclude_user)
    return JsonResponse(result)


@require_http_methods(["POST"])
@login_required
def save_draft_settings(request):
    """API endpoint pour sauvegarder automatiquement les brouillons de paramètres"""
    try:
        data = json.loads(request.body)
        settings_type = data.get('type', 'profile')
        settings_data = data.get('data', {})
        
        # Validate settings type
        valid_types = ['profile', 'general', 'notification', 'learning', 'privacy', 'appearance']
        if settings_type not in valid_types:
            return JsonResponse({
                'success': False,
                'error': 'Invalid settings type'
            }, status=400)
        
        # Save in user session as draft
        draft_key = f'settings_draft_{settings_type}'
        request.session[draft_key] = {
            'data': settings_data,
            'timestamp': timezone.now().isoformat()
        }
        
        logger.debug(f"Saved draft settings {settings_type} for user {request.user.id}")
        
        return JsonResponse({
            'success': True,
            'message': 'Brouillon sauvegardé.'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Error saving draft settings: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@require_http_methods(["GET"])
@login_required
def load_draft_settings(request):
    """API endpoint pour charger les brouillons de paramètres"""
    settings_type = request.GET.get('type', 'profile')
    
    # Validate settings type
    valid_types = ['profile', 'general', 'notification', 'learning', 'privacy', 'appearance']
    if settings_type not in valid_types:
        return JsonResponse({
            'success': False,
            'error': 'Invalid settings type'
        }, status=400)
    
    draft_key = f'settings_draft_{settings_type}'
    draft = request.session.get(draft_key)
    
    if draft:
        logger.debug(f"Loaded draft settings {settings_type} for user {request.user.id}")
        return JsonResponse({
            'success': True,
            'draft': draft
        })
    
    return JsonResponse({
        'success': False,
        'message': 'No draft found'
    })