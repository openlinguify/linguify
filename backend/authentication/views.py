# authentication/views.py
from rest_framework import status, viewsets
from django.shortcuts import redirect
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.views import APIView

from urllib.parse import urlencode
import requests
from .models import User
import logging
import jwt
from jwt.exceptions import PyJWTError

from rest_framework.response import Response
from decimal import Decimal
from django.core.exceptions import ValidationError
from .serializers import UserSerializer, MeSerializer, ProfileUpdateSerializer


logger = logging.getLogger(__name__)

class Auth0Login(APIView):
    """Initie le flux d'authentification Auth0"""
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            params = {
                'client_id': settings.AUTH0_CLIENT_ID,
                'redirect_uri': f"{settings.BACKEND_URL}/api/auth/callback",
                'response_type': 'code',
                'scope': 'openid profile email',
                'audience': settings.AUTH0_AUDIENCE
            }
            auth_url = f'https://{settings.AUTH0_DOMAIN}/authorize?{urlencode(params)}'
            return Response({'auth_url': auth_url})
        
        except Exception as e:
            logger.error(f"Auth0 login error: {str(e)}")
            return Response({'error': 'Authentication service unavailable'}, 
                          status=status.HTTP_503_SERVICE_UNAVAILABLE)

@api_view(['GET'])
@permission_classes([AllowAny])
def auth0_callback(request):
    """Gère le callback Auth0 et crée/mets à jour l'utilisateur"""
    try:
        # Validation du code d'autorisation
        code = request.GET.get('code')
        if not code:
            return JsonResponse({'error': 'Authorization code missing'}, 
                              status=status.HTTP_400_BAD_REQUEST)

        # Configuration de la requête de token
        token_payload = {
            'grant_type': 'authorization_code',
            'client_id': settings.AUTH0_CLIENT_ID,
            'client_secret': settings.AUTH0_CLIENT_SECRET,
            'code': code,
            'redirect_uri': f"{settings.BACKEND_URL}/api/auth/callback"
        }

        # Récupération des tokens Auth0
        token_response = requests.post(
            f'https://{settings.AUTH0_DOMAIN}/oauth/token',
            data=token_payload,
            timeout=10
        )
        
        if token_response.status_code != 200:
            logger.error(f"Token error: {token_response.text}")
            return JsonResponse({'error': 'Failed to obtain tokens'}, 
                              status=status.HTTP_401_UNAUTHORIZED)

        tokens = token_response.json()

        # Validation du token JWT
        try:
            jwt_header = jwt.get_unverified_header(tokens['access_token'])
            jwks = requests.get(f'https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json').json()
            rsa_key = next(k for k in jwks['keys'] if k['kid'] == jwt_header['kid'])
            
            payload = jwt.decode(
                tokens['access_token'],
                key=rsa_key,
                algorithms=['RS256'],
                audience=settings.AUTH0_AUDIENCE,
                issuer=f'https://{settings.AUTH0_DOMAIN}/'
            )
        except PyJWTError as e:
            logger.error(f"JWT validation error: {str(e)}")
            return JsonResponse({'error': 'Invalid token'}, 
                              status=status.HTTP_401_UNAUTHORIZED)

        # Création/Mise à jour de l'utilisateur
        user, created = User.objects.update_or_create(
            email=payload['email'],
            defaults={
                'username': payload.get('nickname', payload['email']),
                'first_name': payload.get('given_name', ''),
                'last_name': payload.get('family_name', ''),
                'is_active': True
            }
        )

        return JsonResponse({
            'access_token': tokens['access_token'],
            'expires_in': tokens['expires_in'],
            'user': UserSerializer(user).data
        })

    except Exception as e:
        logger.error(f"Callback error: {str(e)}")
        return JsonResponse({'error': 'Authentication failed'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def auth0_logout(request):
    """Déconnexion de l'utilisateur"""
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

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Gestion du profil utilisateur"""
    try:
        if request.method == 'GET':
            return Response(MeSerializer(request.user).data)
        
        if request.method == 'PATCH':
            serializer = ProfileUpdateSerializer(
                request.user, 
                data=request.data, 
                partial=True
            )
            
            if serializer.is_valid():
                # Validation des langues
                if serializer.validated_data.get('native_language') == serializer.validated_data.get('target_language'):
                    return Response(
                        {'error': 'Les langues doivent être différentes'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                serializer.save()
                return Response(MeSerializer(request.user).data)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"Profile error: {str(e)}")
        return Response({'error': str(e)}, 
                      status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deactivate_account(request):
    """Deactivate user account"""
    try:
        user = request.user
        user.deactivate_user()
        return Response({"message": "Account deactivated successfully."}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Account deactivation error: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reactivate_account(request):
    """Reactivate user account"""
    try:
        user = request.user
        user.reactivate_user()
        return Response({"message": "Account reactivated successfully."}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Account reactivation error: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    permission_classes = [IsAdminUser]

    def post(self, request, coach_id):
        """Update coach commission override (admin only)"""
        try:
            coach_profile = CoachProfile.objects.get(user__id=coach_id)
            commission_override = request.data.get('commission_override')

            if commission_override is None:
                return Response(
                    {"error": "No commission override provided."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            coach_profile.commission_override = Decimal(commission_override)
            coach_profile.save()
            notify_coach_of_commission_change(coach_profile)
            
            return Response(
                {"message": "Commission override updated successfully."},
                status=status.HTTP_200_OK
            )

        except CoachProfile.DoesNotExist:
            return Response(
                {"error": "Coach profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error updating commission override: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_me_view(request):
    serializer = MeSerializer(request.user)
    return Response(serializer.data)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    serializer = ProfileUpdateSerializer(
        request.user, 
        data=request.data, 
        partial=True
    )
    if serializer.is_valid():
        serializer.save()
        return Response(MeSerializer(request.user).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)