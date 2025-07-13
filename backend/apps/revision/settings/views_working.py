"""
Vue simple pour les paramètres de révision - version simplifiée
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
import json


@login_required
@csrf_exempt  
def simple_revision_config(request):
    """Endpoint simple pour les paramètres - sans base de données pour l'instant"""
    
    # Utiliser la session pour persister les données temporairement
    session_key = f'revision_settings_{request.user.id}'
    
    if request.method == 'GET':
        # Récupérer depuis la session ou valeurs par défaut
        settings = request.session.get(session_key, {
            'default_study_mode': 'spaced',
            'default_difficulty': 'normal',
            'cards_per_session': 20,
            'default_session_duration': 20,
            'required_reviews_to_learn': 3,
            'auto_advance': True,
            'spaced_repetition_enabled': True,
            'initial_interval_easy': 4,
            'initial_interval_normal': 2,
            'initial_interval_hard': 1,
            'daily_reminder_enabled': True,
            'reminder_time': '19:00',
            'notification_frequency': 'daily',
            'enable_animations': True,
            'auto_play_audio': False,
            'keyboard_shortcuts_enabled': True,
            'show_progress_stats': True,
        })
        
        print(f"[SIMPLE] Returning settings for {request.user.username}: {settings}")
        return JsonResponse(settings)
    
    elif request.method in ['POST', 'PATCH']:
        try:
            data = json.loads(request.body)
            print(f"[SIMPLE] Saving settings for {request.user.username}: {data}")
            
            # Sauvegarder dans la session
            request.session[session_key] = data
            request.session.modified = True
            
            print(f"[SIMPLE] Settings saved successfully in session")
            return JsonResponse({
                'success': True,
                'message': 'Settings saved in session'
            })
            
        except Exception as e:
            print(f"[SIMPLE] Error: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    elif request.method == 'DELETE':
        # Réinitialiser
        if session_key in request.session:
            del request.session[session_key]
        
        defaults = {
            'default_study_mode': 'spaced',
            'default_difficulty': 'normal',
            'cards_per_session': 20,
            'default_session_duration': 20,
            'required_reviews_to_learn': 3,
            'auto_advance': True,
            'spaced_repetition_enabled': True,
            'initial_interval_easy': 4,
            'initial_interval_normal': 2,
            'initial_interval_hard': 1,
            'daily_reminder_enabled': True,
            'reminder_time': '19:00',
            'notification_frequency': 'daily',
            'enable_animations': True,
            'auto_play_audio': False,
            'keyboard_shortcuts_enabled': True,
            'show_progress_stats': True,
        }
        
        return JsonResponse(defaults)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def simple_revision_stats(request):
    """Stats simples pour les vraies données"""
    try:
        from apps.revision.models import FlashcardDeck, Flashcard
        
        user = request.user
        total_decks = FlashcardDeck.objects.filter(user=user, is_active=True).count()
        total_cards = Flashcard.objects.filter(deck__user=user, deck__is_active=True).count()
        
        return JsonResponse({
            'total_decks': total_decks,
            'total_cards': total_cards,
            'cards_learned': 0,
            'cards_in_progress': total_cards,
            'daily_streak': 0,
            'success_rate': 0.0,
            'total_study_time': 0,
            'average_session_duration': 0,
        })
        
    except Exception as e:
        print(f"[SIMPLE] Stats error: {e}")
        return JsonResponse({
            'total_cards': 0,
            'cards_learned': 0,
            'cards_in_progress': 0,
            'daily_streak': 0,
            'success_rate': 0.0,
            'total_study_time': 0,
            'average_session_duration': 0,
        })