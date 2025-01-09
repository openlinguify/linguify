# backend/authentication/views.py
from django.shortcuts import redirect
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from urllib.parse import urlencode
import requests

@api_view(['GET'])
@permission_classes([AllowAny])
def auth0_login(request):
    """
    Redirects to Auth0 login page
    """
    params = {
        'client_id': settings.AUTH0_CLIENT_ID,
        'redirect_uri': f"{request.scheme}://{request.get_host()}/api/v1/auth/callback/",
        'response_type': 'code',
        'scope': 'openid profile email',
        'audience': settings.AUTH0_AUDIENCE
    }

    return redirect(f'https://{settings.AUTH0_DOMAIN}/authorize?{urlencode(params)}')

@api_view(['GET'])
@permission_classes([AllowAny])
def auth0_callback(request):
    """
    Handles the Auth0 callback and exchanges the code for tokens
    """
    code = request.GET.get('code')
    if not code:
        return JsonResponse({'error': 'No code provided'}, status=400)

    token_payload = {
        'client_id': settings.AUTH0_CLIENT_ID,
        'client_secret': settings.AUTH0_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': f"{request.scheme}://{request.get_host()}/api/v1/auth/callback/"
    }

    token_response = requests.post(
        f'https://{settings.AUTH0_DOMAIN}/oauth/token',
        json=token_payload
    )

    return JsonResponse(token_response.json())

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def auth0_logout(request):
    """
    Logs out the user from Auth0
    """
    params = {
        'client_id': settings.AUTH0_CLIENT_ID,
        'returnTo': f"{request.scheme}://{request.get_host()}/"
    }

    return redirect(f'https://{settings.AUTH0_DOMAIN}/v2/logout?{urlencode(params)}')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_auth0_user(request):
    """
    Gets the user info from Auth0
    """
    token = request.headers.get('Authorization').split()[1]
    user_response = requests.get(
        f'https://{settings.AUTH0_DOMAIN}/userinfo',
        headers={'Authorization': f'Bearer {token}'}
    )

    return JsonResponse(user_response.json())