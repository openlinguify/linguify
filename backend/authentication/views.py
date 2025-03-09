# authentication/views.py
from rest_framework import status
from django.http import JsonResponse
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
import requests
from urllib.parse import urlencode
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([AllowAny])
def auth0_login(request):
    """Generates the Auth0 login URL"""
    try:
        params = {
            'client_id': settings.AUTH0_CLIENT_ID,
            'redirect_uri': settings.FRONTEND_CALLBACK_URL,
            'response_type': 'code',
            'scope': 'openid profile email',
            'audience': settings.AUTH0_AUDIENCE
        }
        
        auth_url = f'https://{settings.AUTH0_DOMAIN}/authorize?{urlencode(params)}'
        return JsonResponse({'auth_url': auth_url})
    except Exception as e:
        logger.error(f"Auth0 login error: {str(e)}")
        return JsonResponse({'error': 'Authentication service unavailable'}, 
                          status=status.HTTP_503_SERVICE_UNAVAILABLE)

@api_view(['GET'])
@permission_classes([AllowAny])
def auth0_callback(request):
    """Handles the Auth0 callback and exchanges code for tokens"""
    try:
        code = request.GET.get('code')
        
        if not code:
            return JsonResponse({'error': 'Authorization code missing'}, 
                             status=status.HTTP_400_BAD_REQUEST)

        token_payload = {
            'grant_type': 'authorization_code',
            'client_id': settings.AUTH0_CLIENT_ID,
            'client_secret': settings.AUTH0_CLIENT_SECRET,
            'code': code,
            'redirect_uri': settings.FRONTEND_CALLBACK_URL
        }

        token_response = requests.post(
            f'https://{settings.AUTH0_DOMAIN}/oauth/token',
            data=token_payload,
            timeout=10
        )
        
        if token_response.status_code != 200:
            return JsonResponse({'error': 'Failed to obtain token'}, 
                             status=status.HTTP_401_UNAUTHORIZED)

        tokens = token_response.json()
        return JsonResponse({
            'access_token': tokens['access_token'],
            'id_token': tokens.get('id_token'),
            'expires_in': tokens['expires_in']
        })

    except Exception as e:
        logger.exception("Callback processing failed")
        return JsonResponse({'error': 'Authentication failed'}, 
                         status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def auth0_logout(request):
    """Handles user logout"""
    try:
        logout_url = f'https://{settings.AUTH0_DOMAIN}/v2/logout'
        params = {
            'client_id': settings.AUTH0_CLIENT_ID,
            'returnTo': settings.FRONTEND_LOGOUT_REDIRECT
        }
        return JsonResponse({'logout_url': f'{logout_url}?{urlencode(params)}'})
    
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return JsonResponse({'error': 'Logout failed'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])  # Changer IsAuthenticated en AllowAny
def get_me(request):
    """Returns the current authenticated user's information"""
    try:
        # Vérifiez si l'utilisateur est authentifié
        if not request.user.is_authenticated:
            # Retournez une réponse 200 avec des informations minimales ou null
            return JsonResponse({
                'authenticated': False,
                'message': 'No authenticated user',
                # Vous pouvez éventuellement retourner des données minimales par défaut
            })
        
        user = request.user
        
        # Create a comprehensive response with user information
        data = {
            'id': str(user.id),
            'public_id': str(user.public_id) if hasattr(user, 'public_id') else None,
            'email': user.email,
            'name': f"{user.first_name} {user.last_name}".strip() or user.username,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'picture': request.build_absolute_uri(user.profile_picture.url) if hasattr(user, 'profile_picture') and user.profile_picture else None,
            'language_level': user.language_level,
            'native_language': user.native_language,
            'target_language': user.target_language,
            'objectives': user.objectives,
            'bio': user.bio,
            'is_coach': user.is_coach,
            'is_subscribed': user.is_subscribed,
            'is_active': user.is_active,
            'authenticated': True
        }
        return JsonResponse(data)
    except Exception as e:
        logger.error(f"Error retrieving user data: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def token_refresh(request):
    """Refresh a JWT token"""
    try:
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return JsonResponse({'error': 'Refresh token is required'}, status=400)
            
        payload = {
            'grant_type': 'refresh_token',
            'client_id': settings.AUTH0_CLIENT_ID,
            'client_secret': settings.AUTH0_CLIENT_SECRET,
            'refresh_token': refresh_token
        }
        
        response = requests.post(
            f'https://{settings.AUTH0_DOMAIN}/oauth/token',
            json=payload
        )
        
        if response.status_code != 200:
            return JsonResponse({'error': 'Failed to refresh token'}, status=401)
            
        return JsonResponse(response.json())
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)