# backend/authentication/views.py
from django.shortcuts import redirect
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from urllib.parse import urlencode
import requests
from .models import User
from .serializers import UserSerializer

@api_view(['GET'])
@permission_classes([AllowAny])
def auth0_login(request):
    """
    Redirects to Auth0 login page
    """
    try:
        # Récupérer le returnTo s'il existe
        return_to = request.GET.get('returnTo', '/')
        
        params = {
            'client_id': settings.AUTH0_CLIENT_ID,
            'redirect_uri': f"{request.scheme}://{request.get_host()}/api/v1/auth/callback/",
            'response_type': 'code',
            'scope': 'openid profile email',
            'audience': settings.AUTH0_AUDIENCE,
            'state': return_to  # Stocker l'URL de retour dans state
        }

        login_url = f'https://{settings.AUTH0_DOMAIN}/authorize?{urlencode(params)}'
        return redirect(login_url)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def auth0_callback(request):
    """
    Handles the Auth0 callback and exchanges the code for tokens
    """
    try:
        code = request.GET.get('code')
        state = request.GET.get('state', '/')  # Récupérer l'URL de retour
        
        if not code:
            return JsonResponse({'error': 'No code provided'}, status=400)

        token_payload = {
            'client_id': settings.AUTH0_CLIENT_ID,
            'client_secret': settings.AUTH0_CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': f"{request.scheme}://{request.get_host()}/api/v1/auth/callback/"
        }

        # Obtenir les tokens
        token_response = requests.post(
            f'https://{settings.AUTH0_DOMAIN}/oauth/token',
            json=token_payload
        )
        
        if token_response.status_code != 200:
            return JsonResponse({
                'error': 'Failed to obtain tokens'
            }, status=400)

        tokens = token_response.json()

        # Obtenir les infos utilisateur
        user_info = requests.get(
            f'https://{settings.AUTH0_DOMAIN}/userinfo',
            headers={'Authorization': f'Bearer {tokens["access_token"]}'}
        ).json()

        # Créer ou mettre à jour l'utilisateur en base
        user, created = User.objects.get_or_create(
            email=user_info['email'],
            defaults={
                'username': user_info.get('nickname', user_info['email']),
                'first_name': user_info.get('given_name', ''),
                'last_name': user_info.get('family_name', '')
            }
        )

        response = JsonResponse({
            'tokens': tokens,
            'user': UserSerializer(user).data,
            'returnTo': state
        })

        return response

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def auth0_logout(request):
    """
    Logs out the user from Auth0
    """
    try:
        # URL de retour par défaut
        return_to = request.GET.get('returnTo', settings.CLIENT_ORIGIN_URL)
        
        params = {
            'client_id': settings.AUTH0_CLIENT_ID,
            'returnTo': return_to
        }

        auth0_logout_url = f'https://{settings.AUTH0_DOMAIN}/v2/logout?{urlencode(params)}'
        
        # Supprimer les sessions/tokens côté backend si nécessaire
        # request.user.auth_token.delete()
        
        return JsonResponse({
            'logoutUrl': auth0_logout_url 
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_auth0_user(request):
    """
    Gets the user info from Auth0 and syncs with local database
    """
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Invalid authorization header'}, status=401)

        token = auth_header.split()[1]
        
        # Obtenir les infos utilisateur depuis Auth0
        user_response = requests.get(
            f'https://{settings.AUTH0_DOMAIN}/userinfo',
            headers={'Authorization': f'Bearer {token}'}
        )

        if user_response.status_code != 200:
            return JsonResponse({'error': 'Failed to get user info'}, status=400)

        auth0_user = user_response.json()

        # Synchroniser avec la base de données locale
        user, _ = User.objects.update_or_create(
            email=auth0_user['email'],
            defaults={
                'username': auth0_user.get('nickname', auth0_user['email']),
                'first_name': auth0_user.get('given_name', ''),
                'last_name': auth0_user.get('family_name', ''),
                'is_active': True
            }
        )

        return JsonResponse({
            'auth0': auth0_user,
            'user': UserSerializer(user).data
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@api_view(['GET'])
def auth_status(request):
    """
    Check authentication status and sync user data
    """
    try:
        if not request.user.is_authenticated:
            return JsonResponse({
                'isAuthenticated': False,
                'user': None
            })

        # Sync user data if authenticated
        user = request.user
        user_data = UserSerializer(user).data

        return JsonResponse({
            'isAuthenticated': True,
            'user': user_data
        })

    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'isAuthenticated': False,
            'user': None
        }, status=500)