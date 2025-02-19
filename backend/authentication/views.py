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
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            params = {
                'client_id': settings.AUTH0_CLIENT_ID,
                'redirect_uri': settings.FRONTEND_CALLBACK_URL,
                'response_type': 'code',
                'scope': 'openid profile email',
                'audience': settings.AUTH0_AUDIENCE
            }
            
            auth_url = f'https://{settings.AUTH0_DOMAIN}/authorize?{urlencode(params)}'
            logger.debug(f"Generated Auth0 URL: {auth_url}")
            
            return Response({'auth_url': auth_url})
        except Exception as e:
            logger.error(f"Auth0 login error: {str(e)}")
            return Response({
                'error': 'Authentication service unavailable',
                'details': str(e)
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET'])
@permission_classes([AllowAny])
def auth0_callback(request):
    try:
        code = request.GET.get('code')
        logger.debug(f"Received code: {code}")

        if not code:
            logger.error("No authorization code provided")
            return JsonResponse(
                {'error': 'Authorization code missing'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        token_payload = {
            'grant_type': 'authorization_code',
            'client_id': settings.AUTH0_CLIENT_ID,
            'client_secret': settings.AUTH0_CLIENT_SECRET,
            'code': code,
            'redirect_uri': f"{settings.FRONTEND_URL}/callback"  # URL frontend
        }

        logger.debug(f"Token request payload: {token_payload}")

        token_response = requests.post(
            f'https://{settings.AUTH0_DOMAIN}/oauth/token',
            data=token_payload,
            timeout=10
        )
        
        logger.debug(f"Token response status: {token_response.status_code}")
        logger.debug(f"Token response: {token_response.text}")

        if token_response.status_code != 200:
            return JsonResponse(
                {'error': 'Failed to obtain token', 'details': token_response.text}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

        tokens = token_response.json()
        return JsonResponse({
            'access_token': tokens['access_token'],
            'expires_in': tokens['expires_in']
        })

    except Exception as e:
        logger.exception("Callback processing failed")
        return JsonResponse(
            {'error': 'Authentication failed', 'details': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


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
    user = request.user
    data = {
        'id': str(user.id),
        'email': user.email,
        'name': user.get_full_name() or user.username,
        'picture': user.profile_picture_url if hasattr(user, 'profile_picture_url') else None,
        'language_level': user.language_level,
        'native_language': user.native_language,
        'target_language': user.target_language,
    }
    return Response(data)











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