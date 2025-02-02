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

from rest_framework.response import Response
from decimal import Decimal
from django.core.exceptions import ValidationError
from .serializers import UserSerializer, MeSerializer, ProfileUpdateSerializer


logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([AllowAny])
def auth0_login(request):
    """Initiates Auth0 login flow"""
    try:
        return_to = request.GET.get('returnTo', settings.CLIENT_ORIGIN_URL)
        params = {
            'client_id': settings.AUTH0_CLIENT_ID,
            'redirect_uri': f"{request.scheme}://{request.get_host()}/api/v1/auth/callback/",
            'response_type': 'code',
            'scope': 'openid profile email',
            'audience': settings.AUTH0_AUDIENCE,
            'state': return_to
        }
        auth0_url = f'https://{settings.AUTH0_DOMAIN}/authorize?{urlencode(params)}'
        return redirect(auth0_url)
    except Exception as e:
        logger.error(f"Auth0 login error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def auth0_callback(request):
    """Handles Auth0 callback and user creation/update"""
    try:
        code = request.GET.get('code')
        state = request.GET.get('state', settings.CLIENT_ORIGIN_URL)
        
        if not code:
            return JsonResponse({'error': 'No authorization code provided'}, status=400)

        token_payload = {
            'grant_type': 'authorization_code',
            'client_id': settings.AUTH0_CLIENT_ID,
            'client_secret': settings.AUTH0_CLIENT_SECRET,
            'code': code,
            'redirect_uri': f"{request.scheme}://{request.get_host()}/api/v1/auth/callback/"
        }

        token_response = requests.post(
            f'https://{settings.AUTH0_DOMAIN}/oauth/token',
            json=token_payload
        )

        if token_response.status_code != 200:
            logger.error(f"Token error: {token_response.text}")
            return JsonResponse({'error': 'Failed to obtain tokens'}, status=400)

        tokens = token_response.json()

        # Get user info from Auth0 and create/update local user
        user_info = requests.get(
            f'https://{settings.AUTH0_DOMAIN}/userinfo',
            headers={'Authorization': f'Bearer {tokens["access_token"]}'}
        ).json()

        user, _ = User.objects.update_or_create(
            email=user_info['email'],
            defaults={
                'username': user_info.get('nickname', user_info['email']),
                'first_name': user_info.get('given_name', ''),
                'last_name': user_info.get('family_name', ''),
                'is_active': True
            }
        )

        return JsonResponse({
            'access_token': tokens['access_token'],
            'id_token': tokens['id_token'],
            'user': UserSerializer(user).data,
            'returnTo': state
        })

    except Exception as e:
        logger.error(f"Callback error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def auth0_logout(request):
    """Handles user logout"""
    try:
        return_to = request.GET.get('returnTo', settings.CLIENT_ORIGIN_URL)
        logout_url = f'https://{settings.AUTH0_DOMAIN}/v2/logout?{urlencode({
            "client_id": settings.AUTH0_CLIENT_ID,
            "returnTo": return_to
        })}'
        return JsonResponse({'logoutUrl': logout_url})
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
    
@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Handle user profile operations (get/update)"""
    try:
        if request.method == 'GET':
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
        
        elif request.method == 'PATCH':
            serializer = UserSerializer(request.user, data=request.data, partial=True)
            if serializer.is_valid():
                # Validate language selections if provided
                native_lang = request.data.get('native_language')
                target_lang = request.data.get('target_language')
                if native_lang and target_lang and native_lang == target_lang:
                    return Response(
                        {'error': 'Native and target languages must be different'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                    
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    except ValidationError as e:
        logger.error(f"Profile validation error: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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