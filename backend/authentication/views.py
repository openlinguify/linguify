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
from django.views.decorators.csrf import csrf_exempt
from .models import CoachProfile
import datetime



logger = logging.getLogger(__name__)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def token_refresh(request):
    """
    Custom token refresh view that validates the current token 
    and returns user information along with a new token
    """
    try:
        # Get the current user
        user = request.user
        
        # Extract the current token from the Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return Response(
                {'error': 'Invalid authorization header'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        current_token = auth_header.split(' ')[1]
        
        try:
            # Decode the current token to validate it
            jwt.decode(
                current_token, 
                settings.SECRET_KEY, 
                algorithms=['HS256']
            )
        except jwt.ExpiredSignatureError:
            # Token has expired, which is expected
            pass
        except jwt.PyJWTError:
            # Other JWT validation errors
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Generate new token
        new_token = jwt.encode(
            {
                'user_id': str(user.id),
                # Add standard JWT claims like expiration
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
            }, 
            settings.SECRET_KEY, 
            algorithm='HS256'
        )
        
        # Prepare user data
        user_data = {
            'id': str(user.id),
            'email': user.email,
            'name': f"{user.first_name} {user.last_name}".strip() or user.username,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'picture': request.build_absolute_uri(user.profile_picture.url) if hasattr(user, 'profile_picture') and user.profile_picture else None,
            'language_level': user.language_level,
            'native_language': user.native_language,
            'target_language': user.target_language,
        }
        
        return Response({
            'token': new_token,
            'user': user_data
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return Response(
            {'error': 'Token refresh failed', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


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
            
            response = Response({'auth_url': auth_url})
            response["Access-Control-Allow-Origin"] = settings.FRONTEND_URL
            response["Access-Control-Allow-Credentials"] = "true"
            return response
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
        

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """User profile management"""
    logger.info(f"Processing request for user: {request.user}")
    logger.info(f"Auth header: {request.headers.get('Authorization')}")
    logger.info(f"Request method: {request.method}")
    
    if not request.user.is_authenticated:
        logger.error("User is not authenticated")
        return Response(
            {"error": "Authentication required"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    try:
        if request.method == 'GET':
            serializer = MeSerializer(request.user)
            return Response(serializer.data)
        
        elif request.method == 'PATCH':
            logger.info(f"PATCH data received: {request.data}")
            
            serializer = ProfileUpdateSerializer(
                request.user,
                data=request.data,
                partial=True
            )
            
            if not serializer.is_valid():
                logger.error(f"Validation errors: {serializer.errors}")
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer.save()
            return Response(MeSerializer(request.user).data)
            
    except Exception as e:
        logger.error(f"Profile error: {str(e)}", exc_info=True)
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_me_view(request):
    """
    Enhanced endpoint to get the current authenticated user's information.
    This is used by the frontend to get the user's info after login.
    """
    try:
        user = request.user
        logger.info(f"Retrieving profile for user: {user.email}")
        
        # Create a comprehensive response with all user information
        # that might be needed by the frontend
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
            'gender': user.gender,
            'is_coach': user.is_coach,
            'is_subscribed': user.is_subscribed,
            'is_active': user.is_active,
        }
        return Response(data)
    except AttributeError as e:
        logger.error(f"Missing user attribute: {str(e)}")
        return Response(
            {'error': 'User profile incomplete', 'detail': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error retrieving user data: {str(e)}")
        return Response(
            {'error': 'Internal server error', 'detail': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )