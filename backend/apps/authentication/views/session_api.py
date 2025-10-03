"""
API pour vérifier l'état de session d'un utilisateur
Utilisée par le portal pour détecter si un utilisateur est connecté
"""
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

User = get_user_model()


@csrf_exempt
@require_http_methods(["GET"])
def check_user_session(request):
    """
    Vérifie si un utilisateur est connecté à partir de sa session_key
    GET /api/auth/check-session/?session_key=xxx
    """
    session_key = request.GET.get('session_key')

    if not session_key:
        return JsonResponse({
            'authenticated': False,
            'error': 'session_key parameter required'
        }, status=400)

    try:
        # Récupérer la session
        session = Session.objects.get(
            session_key=session_key,
            expire_date__gt=timezone.now()
        )

        # Décoder la session pour récupérer l'user_id
        session_data = session.get_decoded()
        user_id = session_data.get('_auth_user_id')

        if not user_id:
            return JsonResponse({
                'authenticated': False,
                'error': 'No user in session'
            })

        # Récupérer l'utilisateur
        user = User.objects.get(id=user_id)

        # Récupérer l'URL de la photo de profil de manière sécurisée
        profile_picture = None
        if hasattr(user, 'get_profile_picture_url'):
            try:
                profile_picture = user.get_profile_picture_url()
            except:
                profile_picture = None

        return JsonResponse({
            'authenticated': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'profile_picture': profile_picture,
            }
        })

    except Session.DoesNotExist:
        return JsonResponse({
            'authenticated': False,
            'error': 'Session not found or expired'
        })
    except User.DoesNotExist:
        return JsonResponse({
            'authenticated': False,
            'error': 'User not found'
        })
    except Exception as e:
        return JsonResponse({
            'authenticated': False,
            'error': str(e)
        }, status=500)
