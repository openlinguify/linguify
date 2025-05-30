# authentication/supabase_views.py
from rest_framework import status, serializers
from django.http import JsonResponse
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, ProfileUpdateSerializer
import requests
import logging
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiParameter, OpenApiExample, OpenApiTypes
from rest_framework.response import Response
from django.contrib.auth import logout
from django.utils import timezone
import json

User = get_user_model()
logger = logging.getLogger(__name__)

# Serializers for Supabase API documentation
class SupabaseLoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(help_text="Adresse email de l'utilisateur")
    password = serializers.CharField(help_text="Mot de passe de l'utilisateur")

class SupabaseSignupRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(help_text="Adresse email de l'utilisateur")
    password = serializers.CharField(help_text="Mot de passe de l'utilisateur", min_length=6)
    metadata = serializers.DictField(required=False, help_text="Métadonnées utilisateur (prénom, nom, etc.)")

class SupabaseAuthResponseSerializer(serializers.Serializer):
    access_token = serializers.CharField(help_text="Token d'accès JWT")
    refresh_token = serializers.CharField(help_text="Token de rafraîchissement")
    expires_in = serializers.IntegerField(help_text="Temps d'expiration en secondes")
    user = serializers.DictField(help_text="Informations utilisateur")

class SupabaseRefreshRequestSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(required=True, help_text="Le refresh token obtenu lors du login.")

class ErrorResponseSerializer(serializers.Serializer):
    error = serializers.CharField(help_text="Message d'erreur")
    message = serializers.CharField(help_text="Détail de l'erreur", required=False)

def call_supabase_auth_api(endpoint, data=None, method='POST'):
    """Helper function to call Supabase Auth API"""
    url = f"{settings.SUPABASE_URL}/auth/v1/{endpoint}"
    headers = {
        'apikey': settings.SUPABASE_ANON_KEY,
        'Content-Type': 'application/json'
    }
    
    try:
        if method == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method == 'GET':
            response = requests.get(url, headers=headers, timeout=10)
        else:
            raise ValueError(f"Unsupported method: {method}")
            
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Supabase API call failed: {str(e)}")
        return None

@extend_schema(
    tags=["Authentication - Supabase"],
    summary="Connexion avec email/mot de passe",
    description="Authentifie un utilisateur avec son email et mot de passe via Supabase Auth",
    request=SupabaseLoginRequestSerializer,
    responses={
        200: SupabaseAuthResponseSerializer,
        400: ErrorResponseSerializer,
        401: ErrorResponseSerializer,
    },
    examples=[
        OpenApiExample(
            "Login Example",
            value={
                "email": "user@example.com",
                "password": "motdepasse123"
            },
            request_only=True,
        ),
    ]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def supabase_login(request):
    """Login user with Supabase Auth"""
    serializer = SupabaseLoginRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    password = serializer.validated_data['password']
    
    # Call Supabase Auth API
    response = call_supabase_auth_api('token?grant_type=password', {
        'email': email,
        'password': password
    })
    
    if not response:
        return Response(
            {'error': 'Service temporairement indisponible'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    if response.status_code == 200:
        auth_data = response.json()
        logger.info(f"User logged in successfully: {email}")
        return Response(auth_data, status=status.HTTP_200_OK)
    
    elif response.status_code == 400:
        error_data = response.json()
        logger.warning(f"Login failed for {email}: {error_data}")
        return Response(
            {'error': 'Email ou mot de passe incorrect', 'message': error_data.get('error_description', '')},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    else:
        logger.error(f"Supabase login error {response.status_code}: {response.text}")
        return Response(
            {'error': 'Erreur lors de la connexion'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@extend_schema(
    tags=["Authentication - Supabase"],
    summary="Inscription avec email/mot de passe",
    description="Crée un nouveau compte utilisateur via Supabase Auth",
    request=SupabaseSignupRequestSerializer,
    responses={
        200: SupabaseAuthResponseSerializer,
        400: ErrorResponseSerializer,
        422: ErrorResponseSerializer,
    },
    examples=[
        OpenApiExample(
            "Signup Example",
            value={
                "email": "newuser@example.com",
                "password": "motdepasse123",
                "metadata": {
                    "first_name": "Jean",
                    "last_name": "Dupont",
                    "username": "jeandupont"
                }
            },
            request_only=True,
        ),
    ]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def supabase_signup(request):
    """Register new user with Supabase Auth"""
    serializer = SupabaseSignupRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    password = serializer.validated_data['password']
    metadata = serializer.validated_data.get('metadata', {})
    
    # Call Supabase Auth API
    signup_data = {
        'email': email,
        'password': password
    }
    
    if metadata:
        signup_data['data'] = metadata
    
    response = call_supabase_auth_api('signup', signup_data)
    
    if not response:
        return Response(
            {'error': 'Service temporairement indisponible'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    if response.status_code == 200:
        auth_data = response.json()
        logger.info(f"User signed up successfully: {email}")
        return Response(auth_data, status=status.HTTP_200_OK)
    
    elif response.status_code == 422:
        error_data = response.json()
        logger.warning(f"Signup failed for {email}: {error_data}")
        return Response(
            {'error': 'Cet email est déjà utilisé', 'message': error_data.get('msg', '')},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    else:
        logger.error(f"Supabase signup error {response.status_code}: {response.text}")
        return Response(
            {'error': 'Erreur lors de la création du compte'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@extend_schema(
    tags=["Authentication - Supabase"],
    summary="Rafraîchir le token d'accès",
    description="Obtient un nouveau token d'accès à partir du refresh token",
    request=SupabaseRefreshRequestSerializer,
    responses={
        200: SupabaseAuthResponseSerializer,
        400: ErrorResponseSerializer,
        401: ErrorResponseSerializer,
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def supabase_refresh_token(request):
    """Refresh access token using refresh token"""
    serializer = SupabaseRefreshRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    refresh_token = serializer.validated_data['refresh_token']
    
    # Call Supabase Auth API
    response = call_supabase_auth_api('token?grant_type=refresh_token', {
        'refresh_token': refresh_token
    })
    
    if not response:
        return Response(
            {'error': 'Service temporairement indisponible'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    if response.status_code == 200:
        auth_data = response.json()
        logger.info("Token refreshed successfully")
        return Response(auth_data, status=status.HTTP_200_OK)
    
    elif response.status_code == 401:
        logger.warning("Invalid refresh token")
        return Response(
            {'error': 'Token de rafraîchissement invalide'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    else:
        logger.error(f"Supabase refresh error {response.status_code}: {response.text}")
        return Response(
            {'error': 'Erreur lors du rafraîchissement du token'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@extend_schema(
    tags=["Authentication - Supabase"],
    summary="Déconnexion utilisateur",
    description="Déconnecte l'utilisateur et invalide le token d'accès",
    responses={
        200: inline_serializer(
            name='LogoutResponse',
            fields={'message': serializers.CharField()}
        ),
        401: ErrorResponseSerializer,
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def supabase_logout(request):
    """Logout user and invalidate tokens"""
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return Response(
            {'error': 'Token d\'authentification manquant'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    token = auth_header.split(' ')[1]
    
    # Call Supabase Auth API to logout
    url = f"{settings.SUPABASE_URL}/auth/v1/logout"
    headers = {
        'apikey': settings.SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, headers=headers, timeout=10)
        
        # Logout from Django session as well
        logout(request)
        
        if response.status_code == 204:
            logger.info(f"User logged out successfully: {request.user.email}")
            return Response(
                {'message': 'Déconnexion réussie'},
                status=status.HTTP_200_OK
            )
        else:
            logger.warning(f"Supabase logout error {response.status_code}: {response.text}")
            # Still return success for the client even if Supabase logout failed
            return Response(
                {'message': 'Déconnexion réussie'},
                status=status.HTTP_200_OK
            )
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Supabase logout request failed: {str(e)}")
        # Still logout from Django
        logout(request)
        return Response(
            {'message': 'Déconnexion réussie'},
            status=status.HTTP_200_OK
        )

@extend_schema(
    tags=["Authentication - Supabase"],
    summary="Obtenir le profil utilisateur",
    description="Récupère les informations du profil de l'utilisateur connecté",
    responses={
        200: UserSerializer,
        401: ErrorResponseSerializer,
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def supabase_user_profile(request):
    """Get current user profile"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)

@extend_schema(
    tags=["Authentication - Supabase"],
    summary="Réinitialiser le mot de passe",
    description="Envoie un email de réinitialisation de mot de passe",
    request=inline_serializer(
        name='PasswordResetRequest',
        fields={'email': serializers.EmailField()}
    ),
    responses={
        200: inline_serializer(
            name='PasswordResetResponse',
            fields={'message': serializers.CharField()}
        ),
        400: ErrorResponseSerializer,
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def supabase_reset_password(request):
    """Send password reset email"""
    email = request.data.get('email')
    
    if not email:
        return Response(
            {'error': 'Email requis'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Call Supabase Auth API
    response = call_supabase_auth_api('recover', {
        'email': email
    })
    
    if not response:
        return Response(
            {'error': 'Service temporairement indisponible'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    # Always return success for security reasons (don't reveal if email exists)
    logger.info(f"Password reset requested for: {email}")
    return Response(
        {'message': 'Si cet email existe, un lien de réinitialisation a été envoyé'},
        status=status.HTTP_200_OK
    )