"""
Vue pour récupérer les paramètres utilisateur dans l'app révision
"""
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods


@login_required
@require_http_methods(["GET"])
def get_user_revision_settings(request):
    """
    Récupère les paramètres de révision de l'utilisateur pour l'app révision
    """
    try:
        # Récupérer depuis la session (comme dans Settings)
        session_key = f'revision_settings_{request.user.id}'
        settings = request.session.get(session_key, {
            'cards_per_session': 20,
            'default_session_duration': 20,
            'required_reviews_to_learn': 3,
            'default_study_mode': 'spaced',
            'default_difficulty': 'normal',
            'auto_advance': True,
        })
        
        print(f"[USER_SETTINGS] Retrieved settings for {request.user.username}: {settings}")
        
        return JsonResponse({
            'success': True,
            'settings': settings
        })
        
    except Exception as e:
        print(f"[USER_SETTINGS] Error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'settings': {
                'cards_per_session': 20,
                'default_session_duration': 20,
                'required_reviews_to_learn': 3,
                'default_study_mode': 'spaced',
                'default_difficulty': 'normal',
                'auto_advance': True,
            }
        })