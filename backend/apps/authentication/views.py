# authentication/views.py
from rest_framework import status, serializers
from django.http import JsonResponse
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from django.contrib.auth import get_user_model
from .serializers import (
    UserSerializer, ProfileUpdateSerializer, 
    CookieConsentCreateSerializer, CookieConsentSerializer,
    CookieConsentLogSerializer, CookieConsentStatsSerializer
)
import os
import datetime
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from rest_framework.response import Response
import requests
from urllib.parse import urlencode
import logging
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiParameter, OpenApiExample, OpenApiTypes
from drf_spectacular.types import OpenApiTypes
from django.contrib.auth import logout
from django.utils import timezone

User = get_user_model()
logger = logging.getLogger(__name__)

class LoginResponseSerializer(serializers.Serializer):
    auth_url = serializers.URLField(help_text="URL d'authentification Auth0")

class LogoutResponseSerializer(serializers.Serializer):
    logout_url = serializers.URLField(help_text="URL de déconnexion Auth0")

class ErrorResponseSerializer(serializers.Serializer):
    error = serializers.CharField(help_text="Message d'erreur")

class TokenResponseSerializer(serializers.Serializer):
    access_token = serializers.CharField(help_text="Token d'accès JWT")
    id_token = serializers.CharField(help_text="Token d'identité JWT", required=False)
    expires_in = serializers.IntegerField(help_text="Temps d'expiration en secondes")

class RefreshTokenRequestSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(required=True, help_text="Le refresh token obtenu lors du login.")

@extend_schema(
    tags=["Authentication - Auth0 Flow"],
    summary="Générer l'URL de connexion Auth0",
    description="Crée une URL pour rediriger l'utilisateur vers la page de connexion Auth0",
    responses={
        200: LoginResponseSerializer,
        503: ErrorResponseSerializer
    }
)
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

@extend_schema(
    tags=["Authentication - Auth0 Flow"],
    summary="Gérer le callback Auth0",
    description="Reçoit le code d'autorisation d'Auth0 et l'échange contre des tokens (access token, id token). Ne pas appeler directement, c'est une redirection.",
    parameters=[
        OpenApiParameter(name='code', description='Code d\'autorisation fourni par Auth0.', required=True, type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
        OpenApiParameter(name='state', description='Valeur state optionnelle si utilisée lors de la redirection initiale.', required=False, type=OpenApiTypes.STR, location=OpenApiParameter.QUERY)
    ],
    responses={
        200: TokenResponseSerializer,
        400: ErrorResponseSerializer,
        401: ErrorResponseSerializer, 
        500: ErrorResponseSerializer
    }
)
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
            logger.error(f"Auth0 token exchange failed: {token_response.status_code} - {token_response.text}")
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

@extend_schema(
    tags=["Authentication - Auth0 Flow"],
    summary="Gérer la déconnexion Auth0",
    description="Génère l'URL pour déconnecter l'utilisateur d'Auth0 et le rediriger vers l'application frontend.",
    request=None, # Pas de corps de requête
    responses={
        200: LogoutResponseSerializer,
        500: ErrorResponseSerializer
    }
)
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

@extend_schema(
    tags=["User Profile"],
    summary="Obtenir ou mettre à jour le profil de l'utilisateur authentifié",
    description="GET: Retourne les informations de l'utilisateur actuellement authentifié.\nPATCH: Met à jour les informations de l'utilisateur actuellement authentifié.",
    responses={
        200: UserSerializer, # UserSerializer est utilisé pour la réponse GET et PATCH réussie
        400: ErrorResponseSerializer, # Pour les erreurs de validation du PATCH
        500: ErrorResponseSerializer
    },
    request={ # Spécifier le corps de la requête pour PATCH
        'application/json': ProfileUpdateSerializer,
    }
)
@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def get_me(request):
    """
    GET: Returns the current authenticated user's information
    PATCH: Updates the current authenticated user's information
    """
    try:
        user = request.user
        
        if request.method == 'GET':
            # Log profile picture URLs for debugging
            logger.debug(f"User {user.id} profile picture data - URL: {user.profile_picture_url}, Django file: {user.profile_picture}")
            
            # Create a comprehensive response with user information
            data = {
                'id': str(user.id),
                'public_id': str(user.public_id) if hasattr(user, 'public_id') else None,
                'email': user.email,
                'name': f"{user.first_name} {user.last_name}".strip() or user.username,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'picture': user.profile_picture_url or (user.get_profile_picture_absolute_url(request) if user.profile_picture else None),
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
        
        elif request.method == 'PATCH':
            # Update user information
            data = request.data
            
            # Update basic info
            if 'username' in data:
                user.username = data['username']
            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']
            if 'bio' in data:
                user.bio = data['bio']
            
            # Update language settings
            if 'native_language' in data:
                user.native_language = data['native_language']
            if 'target_language' in data:
                user.target_language = data['target_language']
            if 'language_level' in data:
                user.language_level = data['language_level']
            if 'objectives' in data:
                user.objectives = data['objectives']
            
            # Gender and birthday
            if 'gender' in data:
                user.gender = data['gender']
            if 'birthday' in data:
                user.birthday = data['birthday']
            
            user.save()
            
            # Return updated user info
            return JsonResponse({
                'id': str(user.id),
                'email': user.email,
                'name': f"{user.first_name} {user.last_name}".strip() or user.username,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'picture': user.profile_picture_url or (user.get_profile_picture_absolute_url(request) if user.profile_picture else None),
                'language_level': user.language_level,
                'native_language': user.native_language,
                'target_language': user.target_language,
                'objectives': user.objectives,
                'bio': user.bio,
                'gender': user.gender,
                'birthday': user.birthday,
                'is_coach': user.is_coach,
                'is_subscribed': user.is_subscribed,
                'authenticated': True
            })
            
    except Exception as e:
        logger.error(f"Error processing user data: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, 
                         status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(
    tags=["Auth: User Settings"],
    summary="Retrieve or update user settings",
    description="GET: Retrieve all user settings\nPOST: Update user settings",
    responses={
        200: inline_serializer(
            name="UserSettingsResponse",
            fields={
                "email_notifications": serializers.BooleanField(),
                "push_notifications": serializers.BooleanField(),
                # Add other settings fields
            }
        ),
        500: ErrorResponseSerializer
    }
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def user_settings(request):
    """
    GET: Retrieve user settings
    POST: Save user settings
    """
    user = request.user
    
    if request.method == 'GET':
        # Get settings from user profile or defaults
        settings = {
            # Account settings
            'email_notifications': getattr(user, 'email_notifications', True),
            'push_notifications': getattr(user, 'push_notifications', True),
            'interface_language': getattr(user, 'interface_language', 'en'),
            
            # Learning settings
            'daily_goal': getattr(user, 'daily_goal', 15),
            'weekday_reminders': getattr(user, 'weekday_reminders', True),
            'weekend_reminders': getattr(user, 'weekend_reminders', False),
            'reminder_time': getattr(user, 'reminder_time', '18:00'),
            'speaking_exercises': getattr(user, 'speaking_exercises', True),
            'listening_exercises': getattr(user, 'listening_exercises', True),
            'reading_exercises': getattr(user, 'reading_exercises', True),
            'writing_exercises': getattr(user, 'writing_exercises', True),
            
            # Language settings
            'native_language': user.native_language,
            'target_language': user.target_language,
            'language_level': user.language_level,
            'objectives': user.objectives,
            
            # Privacy settings
            'public_profile': getattr(user, 'public_profile', True),
            'share_progress': getattr(user, 'share_progress', True),
            'share_activity': getattr(user, 'share_activity', False),
        }
        
        return Response(settings)
    
    elif request.method == 'POST':
        settings_data = request.data
        
        # Update language settings on the user model
        if 'native_language' in settings_data:
            user.native_language = settings_data['native_language']
            
        if 'target_language' in settings_data:
            user.target_language = settings_data['target_language']
            
        if 'language_level' in settings_data:
            user.language_level = settings_data['language_level']
            
        if 'objectives' in settings_data:
            user.objectives = settings_data['objectives']
            
        # For other settings, we'll store them as model attributes 
        # (They'll be saved even if not in the model fields explicitly)
        for key, value in settings_data.items():
            if key not in ['native_language', 'target_language', 'language_level', 'objectives']:
                setattr(user, key, value)
                
        user.save()
        
        return Response({
            'message': 'Settings saved successfully',
            'settings': settings_data
        })




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

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
def user_profile(request):
    """
    GET: Retrieve current user profile
    PATCH: Update current user profile
    """
    user = request.user
    
    if request.method == 'GET':
        try:
            # Vérifier si le profile_picture existe avant de l'utiliser
            if hasattr(user, 'profile_picture') and user.profile_picture:
                try:
                    # Vérifier si le fichier existe physiquement
                    if not os.path.exists(user.profile_picture.path):
                        # Le fichier n'existe plus, effacer la référence
                        logger.warning(f"Profile picture file not found: {user.profile_picture.path}")
                        user.profile_picture = None
                        user.save()  # Removed update_fields
                except Exception as e:
                    logger.warning(f"Error checking profile picture: {str(e)}")
                    user.profile_picture = None
                    user.save()  # Removed update_fields
            
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except Exception as e:
            logger.exception(f"Error serializing user profile: {str(e)}")
            return Response(
                {'error': 'Failed to retrieve user profile', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    elif request.method == 'PATCH':
        try:
            logger.info(f"Updating profile for user {user.email}")
            logger.debug(f"Update data: {request.data}")
            
            # Vérifier l'existence du fichier de profile picture
            if hasattr(user, 'profile_picture') and user.profile_picture:
                try:
                    if not os.path.exists(user.profile_picture.path):
                        logger.warning("Profile picture file doesn't exist, resetting reference")
                        user.profile_picture = None
                        user.save()  # Removed update_fields
                except Exception as e:
                    logger.warning(f"Error checking profile picture: {str(e)}")
                    user.profile_picture = None
                    user.save()  # Removed update_fields
            
            serializer = ProfileUpdateSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                try:
                    # We're not using fields_to_update anymore
                    serializer.save()
                    logger.info(f"Profile updated successfully for {user.email}")
                    return Response(serializer.data)
                except Exception as e:
                    logger.exception(f"Error saving user profile: {str(e)}")
                    return Response(
                        {'error': f'Failed to save profile: {str(e)}'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            
            logger.error(f"Profile update validation errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Error updating user profile: {str(e)}")
            return Response(
                {'error': f'Failed to update profile: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

def optimize_image(image_file, max_size=(800, 800), quality=85):
    """Resize and optimize image for web display"""
    img = Image.open(image_file)
    
    # Convert RGBA to RGB if needed
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    
    # Resize if larger than max_size
    if img.width > max_size[0] or img.height > max_size[1]:
        img.thumbnail(max_size, Image.LANCZOS)
    
    # Save optimized image
    output = BytesIO()
    img.save(output, format='JPEG', quality=quality, optimize=True)
    output.seek(0)
    
    # Return content file with original name but jpg extension
    original_name = os.path.splitext(image_file.name)[0]
    return ContentFile(output.read(), name=f"{original_name}.jpg")

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def update_profile_picture(request):
    """
    Update user profile picture using Supabase Storage
    """
    user = request.user
    
    if 'profile_picture' not in request.FILES:
        return Response({'error': 'No profile picture provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Add validation for file type
    uploaded_file = request.FILES['profile_picture']
    if not uploaded_file.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        return Response({'error': 'Invalid file type. Please upload a PNG, JPG, JPEG or GIF'}, 
                        status=status.HTTP_400_BAD_REQUEST)
    
    # Add validation for file size (5MB limit)
    if uploaded_file.size > 5 * 1024 * 1024:
        return Response({'error': 'File too large. Maximum size is 5MB'}, 
                        status=status.HTTP_400_BAD_REQUEST)
    
    try:
        from .supabase_storage import supabase_storage
        logger.info("Supabase storage service imported successfully")
        
        # Delete existing profile picture from Supabase if any
        if user.profile_picture_filename:
            try:
                supabase_storage.delete_profile_picture(user.profile_picture_filename)
            except Exception as e:
                logger.warning(f"Failed to delete old profile picture from Supabase: {str(e)}")
        
        # Upload to Supabase Storage
        upload_result = supabase_storage.upload_profile_picture(
            user_id=str(user.id),
            file=uploaded_file,
            original_filename=uploaded_file.name
        )
        
        if not upload_result.get('success'):
            return Response(
                {'error': upload_result.get('error', 'Failed to upload image to Supabase')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Update user with Supabase URL and filename
        user.profile_picture_url = upload_result['public_url']
        user.profile_picture_filename = upload_result['filename']
        
        # Clear the old Django storage profile picture if it exists
        if user.profile_picture:
            logger.info(f"Clearing old Django profile picture for user {user.id}")
            user.profile_picture = None
            
        user.save(update_fields=['profile_picture_url', 'profile_picture_filename', 'profile_picture'])
        
        # Refresh user from database to ensure we have the latest data
        user.refresh_from_db()
        
        # Log the updated values
        logger.info(f"User {user.id} profile picture updated - URL: {user.profile_picture_url}, Filename: {user.profile_picture_filename}")
        
        # Create response
        response = Response({
            'message': 'Profile picture updated successfully',
            'picture': upload_result['public_url'],
            'urls': upload_result.get('urls', {}),
            'filename': upload_result['filename'],
            'profile_picture_url': user.profile_picture_url  # Add this for debugging
        })
        
        logger.info(f"Profile picture uploaded to Supabase for user {user.id}: {upload_result['filename']}")
        
        # Add cache control header for better performance
        response['Cache-Control'] = 'public, max-age=86400'  # Cache for 24 hours
        return response
        
    except Exception as e:
        logger.exception(f"Error updating profile picture: {str(e)}")
        return Response(
            {'error': f'Failed to update profile picture: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )  

@extend_schema(
    tags=["User Account"],
    summary="Delete user account",
    description="Delete the authenticated user's account. By default, the account will be scheduled for deletion after 30 days.",
    request=inline_serializer(
        name="DeleteAccountRequest", 
        fields={
            "deletion_type": serializers.ChoiceField(
                choices=["temporary", "permanent"], 
                help_text="Whether to delete the account immediately or after 30 days"
            ),
            "anonymize": serializers.BooleanField(
                help_text="Whether to anonymize personal data (GDPR compliance)", 
                default=True
            ),
        }
    ),
    responses={
        200: inline_serializer(
            name="DeleteAccountResponse",
            fields={
                "success": serializers.BooleanField(),
                "message": serializers.CharField(),
                "deletion_type": serializers.CharField(),
                "scheduled_at": serializers.DateTimeField(required=False),
                "deletion_date": serializers.DateTimeField(required=False),
                "days_remaining": serializers.IntegerField(required=False),
            }
        ),
        500: ErrorResponseSerializer
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    """
    Delete the authenticated user's account with option for immediate or delayed deletion.
    """
    try:
        user = request.user
        logger.info(f"Account deletion requested by user: {user.email}")
        
        # Get deletion preferences
        deletion_type = request.data.get('deletion_type', 'temporary')
        anonymize = request.data.get('anonymize', True)
        immediate = deletion_type == 'permanent'
        
        # Process the deletion based on type
        if immediate:
            # Execute immediate account deletion with anonymization
            user.delete_user_account(anonymize=anonymize, immediate=True)
            
            # Logout the user from the current session
            logout(request)
            
            return Response({
                'success': True,
                'message': 'Your account has been permanently deleted.',
                'deletion_type': 'permanent'
            })
        else:
            # Schedule the account for deletion after 30 days
            result = user.delete_user_account(anonymize=anonymize, immediate=False)
            
            # Logout the user from the current session
            logout(request)
            
            # Format dates for response
            scheduled_at = result['scheduled_at'].isoformat() if result['scheduled_at'] else None
            deletion_date = result['deletion_date'].isoformat() if result['deletion_date'] else None
            
            # Calculate days remaining
            days_remaining = user.days_until_deletion()
            
            return Response({
                'success': True,
                'message': 'Your account has been scheduled for deletion. It will be permanently deleted in 30 days.',
                'deletion_type': 'temporary',
                'scheduled_at': scheduled_at,
                'deletion_date': deletion_date,
                'days_remaining': days_remaining
            })
        
    except Exception as e:
        logger.exception(f"Account deletion failed: {str(e)}")
        
        # Fallback approach - try to deactivate the account directly
        try:
            user.is_active = False
            user.save()
            logger.info(f"Fallback: Successfully deactivated user {user.email}")
            
            # Try to set deletion flags directly without update_fields
            user.is_pending_deletion = True
            user.deletion_scheduled_at = timezone.now()
            user.deletion_date = timezone.now() + datetime.timedelta(days=30)
            user.save()
            
            return Response(
                {
                    'success': True,
                    'message': 'Your account has been scheduled for deletion using fallback method.',
                    'deletion_type': 'temporary',
                    'scheduled_at': user.deletion_scheduled_at.isoformat() if user.deletion_scheduled_at else None,
                    'deletion_date': user.deletion_date.isoformat() if user.deletion_date else None,
                },
                status=status.HTTP_200_OK
            )
        except Exception as fallback_error:
            logger.exception(f"Account deletion fallback also failed: {str(fallback_error)}")
            return Response(
                {
                    'success': False,
                    'error': 'Failed to delete account',
                    'message': str(e),
                    'fallback_error': str(fallback_error)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

@extend_schema(
    tags=["User Account"],
    summary="Cancel account deletion",
    description="Cancel a scheduled account deletion and reactivate the account.",
    responses={
        200: inline_serializer(
            name="CancelDeletionResponse",
            fields={
                "success": serializers.BooleanField(),
                "message": serializers.CharField(),
            }
        ),
        400: inline_serializer(
            name="CancelDeletionError",
            fields={
                "success": serializers.BooleanField(),
                "message": serializers.CharField(),
            }
        ),
        500: ErrorResponseSerializer
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_account_deletion(request):
    """
    Cancel a scheduled account deletion and reactivate the account.
    """
    try:
        user = request.user
        logger.info(f"Account deletion cancellation requested by user: {user.email}")
        
        if not user.is_pending_deletion:
            return Response({
                'success': False,
                'message': 'Your account is not scheduled for deletion.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Cancel the scheduled deletion
        user.cancel_account_deletion()
        
        return Response({
            'success': True,
            'message': 'Account deletion has been cancelled. Your account is now active again.'
        })
        
    except Exception as e:
        logger.exception(f"Cancelling account deletion failed: {str(e)}")
        return Response(
            {
                'success': False,
                'error': 'Failed to cancel account deletion',
                'message': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def debug_profile_endpoint(request):
    """
    Debug endpoint to trace profile API issues
    """
    import sys
    import traceback
    
    try:
        # Get basic request info
        request_info = {
            'method': request.method,
            'path': request.path,
            'auth': request.auth is not None,
            'user': str(request.user),
            'is_authenticated': request.user.is_authenticated,
            'headers': dict(request.headers),
        }
        
        # Try to access user data safely
        user_data = None
        if request.user.is_authenticated:
            try:
                user = request.user
                user_data = {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_active': user.is_active,
                }
            except Exception as e:
                user_data = {'error': str(e)}
        
        # Try actual profile serialization
        serializer_data = None
        if request.user.is_authenticated:
            try:
                from .serializers import UserSerializer
                serializer = UserSerializer(request.user)
                serializer_data = serializer.data
            except Exception as e:
                serializer_data = {'error': str(e), 'traceback': traceback.format_exc()}
        
        return Response({
            'request_info': request_info,
            'user_data': user_data,
            'serializer_data': serializer_data,
            'python_version': sys.version,
            'success': True
        })
    except Exception as e:
        # Capture full error info
        return Response({
            'error': str(e),
            'traceback': traceback.format_exc(),
            'success': False
        }, status=500)


# ============================================================================
# Cookie Consent Management Views
# ============================================================================

from .models import CookieConsent, CookieConsentLog
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie, csrf_protect
from django.db import models


@extend_schema(
    tags=["Cookie Consent"],
    summary="Create cookie consent",
    description="Record user's cookie consent preferences",
    request=CookieConsentCreateSerializer,
    responses={
        201: CookieConsentSerializer,
        400: ErrorResponseSerializer
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def create_cookie_consent(request):
    """Create a new cookie consent record"""
    serializer = CookieConsentCreateSerializer(
        data=request.data, 
        context={'request': request}
    )
    
    if serializer.is_valid():
        try:
            consent = serializer.save()
            response_serializer = CookieConsentSerializer(consent)
            
            return Response(
                response_serializer.data, 
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(f"Error creating cookie consent: {str(e)}")
            return Response(
                {'error': 'Failed to create consent record'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Cookie Consent"],
    summary="Get user's cookie consent",
    description="Retrieve the latest cookie consent for authenticated user or session",
    responses={
        200: CookieConsentSerializer,
        404: ErrorResponseSerializer
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_cookie_consent(request):
    """Get the latest cookie consent for user/session"""
    user = request.user if request.user.is_authenticated else None
    session_id = request.session.session_key
    
    # Get IP address
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR')
    
    consent = CookieConsent.objects.get_latest_consent(
        user=user,
        session_id=session_id,
        ip_address=ip_address
    )
    
    if consent and not consent.is_revoked:
        serializer = CookieConsentSerializer(consent)
        return Response(serializer.data)
    
    return Response(
        {'error': 'No valid consent found'}, 
        status=status.HTTP_404_NOT_FOUND
    )


@extend_schema(
    tags=["Cookie Consent"],
    summary="Revoke cookie consent",
    description="Revoke user's cookie consent",
    request=inline_serializer(
        name='RevokeConsentRequest',
        fields={'reason': serializers.CharField(required=False, default='user_request')}
    ),
    responses={
        200: inline_serializer(
            name='RevokeConsentResponse',
            fields={'message': serializers.CharField(), 'revoked_at': serializers.DateTimeField()}
        ),
        404: ErrorResponseSerializer
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def revoke_cookie_consent(request):
    """Revoke the latest cookie consent"""
    user = request.user if request.user.is_authenticated else None
    session_id = request.session.session_key
    
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR')
    
    consent = CookieConsent.objects.get_latest_consent(
        user=user,
        session_id=session_id,
        ip_address=ip_address
    )
    
    if consent and not consent.is_revoked:
        reason = request.data.get('reason', 'user_request')
        old_values = consent.to_dict()
        
        consent.revoke(reason=reason)
        
        # Log the revocation
        CookieConsentLog.objects.create(
            consent=consent,
            action='revoked',
            old_values=old_values,
            new_values={'is_revoked': True, 'revocation_reason': reason},
            ip_address=ip_address,
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({
            'message': 'Consent revoked successfully',
            'revoked_at': consent.revoked_at.isoformat()
        })
    
    return Response(
        {'error': 'No active consent found to revoke'}, 
        status=status.HTTP_404_NOT_FOUND
    )


@extend_schema(
    tags=["Cookie Consent - Admin"],
    summary="Get cookie consent statistics",
    description="Get statistics about cookie consents (admin only)",
    parameters=[
        OpenApiParameter(
            name='days',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Number of days to analyze (default: 30)',
            default=30
        )
    ],
    responses={
        200: CookieConsentStatsSerializer,
        403: ErrorResponseSerializer
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cookie_consent_stats(request):
    """Get cookie consent statistics - admin only"""
    if not request.user.is_staff:
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    days = int(request.GET.get('days', 30))
    stats = CookieConsent.objects.get_analytics_data(days=days)
    
    serializer = CookieConsentStatsSerializer(stats)
    return Response(serializer.data)


@extend_schema(
    tags=["Cookie Consent - Admin"],
    summary="Get consent logs",
    description="Get audit logs for cookie consents (admin only)",
    parameters=[
        OpenApiParameter(
            name='consent_id',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Filter by specific consent ID'
        ),
        OpenApiParameter(
            name='action',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Filter by action type'
        ),
        OpenApiParameter(
            name='limit',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Number of results to return (default: 100)',
            default=100
        )
    ],
    responses={
        200: CookieConsentLogSerializer(many=True),
        403: ErrorResponseSerializer
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cookie_consent_logs(request):
    """Get cookie consent audit logs - admin only"""
    if not request.user.is_staff:
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    queryset = CookieConsentLog.objects.all()
    
    # Apply filters
    consent_id = request.GET.get('consent_id')
    if consent_id:
        queryset = queryset.filter(consent__id=consent_id)
    
    action = request.GET.get('action')
    if action:
        queryset = queryset.filter(action=action)
    
    # Limit results
    limit = int(request.GET.get('limit', 100))
    queryset = queryset[:limit]
    
    serializer = CookieConsentLogSerializer(queryset, many=True)
    return Response(serializer.data)


@extend_schema(
    tags=["Cookie Consent"],
    summary="Check consent validity",
    description="Check if current user/session has valid consent for specific cookie category",
    parameters=[
        OpenApiParameter(
            name='category',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Cookie category to check (analytics, functionality, performance)',
            required=True,
            enum=['analytics', 'functionality', 'performance']
        ),
        OpenApiParameter(
            name='version',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Consent version to check against (default: 1.0)',
            default='1.0'
        )
    ],
    responses={
        200: inline_serializer(
            name='ConsentValidityResponse',
            fields={
                'has_consent': serializers.BooleanField(),
                'category': serializers.CharField(),
                'version': serializers.CharField(),
                'consent_date': serializers.DateTimeField(required=False)
            }
        ),
        400: ErrorResponseSerializer
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def check_consent_validity(request):
    """Check if user has valid consent for specific category"""
    category = request.GET.get('category')
    version = request.GET.get('version', '1.0')
    
    if not category or category not in ['analytics', 'functionality', 'performance']:
        return Response(
            {'error': 'Invalid category. Must be: analytics, functionality, or performance'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = request.user if request.user.is_authenticated else None
    session_id = request.session.session_key
    
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR')
    
    consent = CookieConsent.objects.get_latest_consent(
        user=user,
        session_id=session_id,
        ip_address=ip_address
    )
    
    has_consent = False
    consent_date = None
    
    if consent and not consent.is_revoked and consent.version == version:
        has_consent = getattr(consent, category, False)
        consent_date = consent.created_at
    
    return Response({
        'has_consent': has_consent,
        'category': category,
        'version': version,
        'consent_date': consent_date.isoformat() if consent_date else None
    })


@extend_schema(
    tags=["Cookie Consent - Debug"],
    summary="Debug cookie consent status",
    description="Get detailed information about current cookie consent for debugging",
    responses={
        200: inline_serializer(
            name='DebugConsentResponse',
            fields={
                'local_consent': serializers.CharField(),
                'backend_consent': CookieConsentSerializer(required=False),
                'session_info': serializers.DictField(),
                'headers': serializers.DictField(),
            }
        )
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def debug_cookie_consent(request):
    """Debug endpoint to check cookie consent status"""
    
    # Only allow in DEBUG mode
    if not settings.DEBUG:
        return Response({'error': 'Debug endpoint only available in DEBUG mode'}, status=404)
    
    user = request.user if request.user.is_authenticated else None
    session_id = request.session.session_key
    
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR')
    
    # Get backend consent
    consent = CookieConsent.objects.get_latest_consent(
        user=user,
        session_id=session_id,
        ip_address=ip_address
    )
    
    # Get all consents for this user/session
    all_consents = CookieConsent.objects.filter(
        models.Q(user=user) if user else models.Q(session_id=session_id) | models.Q(ip_address=ip_address)
    ).order_by('-created_at')
    
    return Response({
        'session_info': {
            'user_id': user.id if user else None,
            'session_id': session_id,
            'ip_address': ip_address,
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:100] + '...' if len(request.META.get('HTTP_USER_AGENT', '')) > 100 else request.META.get('HTTP_USER_AGENT', '')
        },
        'latest_consent': CookieConsentSerializer(consent).data if consent else None,
        'all_consents_count': all_consents.count(),
        'all_consents': CookieConsentSerializer(all_consents[:5], many=True).data,  # Only first 5
        'cookies_in_request': dict(request.COOKIES),
        'relevant_headers': {
            'X-Cookie-Consent-Status': request.META.get('HTTP_X_COOKIE_CONSENT_STATUS'),
            'User-Agent': request.META.get('HTTP_USER_AGENT', '')[:50] + '...' if len(request.META.get('HTTP_USER_AGENT', '')) > 50 else request.META.get('HTTP_USER_AGENT', ''),
            'Referer': request.META.get('HTTP_REFERER'),
        }
    })


# === SETTINGS VIEWS ===

from django.contrib.auth import update_session_auth_hash
from django.db.models import Avg, Count
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required as django_login_required




@django_login_required
def settings_stats(request):
    """Get settings statistics"""
    try:
        total_users = User.objects.count()
        notification_enabled = User.objects.filter(email_notifications=True).count()
        public_profiles = User.objects.filter(public_profile=True).count()
        
        avg_daily_goal = User.objects.aggregate(
            avg_goal=Avg('daily_goal')
        )['avg_goal'] or 0
        
        # Most common languages and levels
        most_common_native = User.objects.values('native_language').annotate(
            count=Count('native_language')
        ).order_by('-count').first()
        
        most_common_target = User.objects.values('target_language').annotate(
            count=Count('target_language')
        ).order_by('-count').first()
        
        most_common_level = User.objects.values('language_level').annotate(
            count=Count('language_level')
        ).order_by('-count').first()
        
        stats_data = {
            'total_users': total_users,
            'notification_enabled_users': notification_enabled,
            'public_profile_users': public_profiles,
            'daily_goal_average': round(avg_daily_goal, 1),
            'most_common_native_language': most_common_native['native_language'] if most_common_native else 'EN',
            'most_common_target_language': most_common_target['target_language'] if most_common_target else 'FR',
            'most_common_level': most_common_level['language_level'] if most_common_level else 'A1'
        }
        
        return JsonResponse(stats_data)
        
    except Exception as e:
        return JsonResponse(
            {'error': 'Failed to fetch statistics'},
            status=500
        )


# === DJANGO PROFILE PICTURE VIEWS ===

@csrf_protect
@django_login_required  
@require_http_methods(["POST", "DELETE"])
def manage_profile_picture(request):
    """Upload or delete profile picture"""
    user = request.user
    
    if request.method == 'POST':
        # Upload new profile picture
        if 'profile_picture' not in request.FILES:
            return JsonResponse({'success': False, 'error': 'No profile picture provided'}, status=400)
        
        uploaded_file = request.FILES['profile_picture']
        
        # Validate file type
        if not uploaded_file.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
            return JsonResponse({'success': False, 'error': 'Invalid file type. Please upload PNG, JPG, JPEG, GIF or WEBP'}, status=400)
        
        # Validate file size (5MB limit)
        if uploaded_file.size > 5 * 1024 * 1024:
            return JsonResponse({'success': False, 'error': 'File too large. Maximum size is 5MB'}, status=400)
        
        try:
            from .supabase_storage import SupabaseStorageService
            storage_service = SupabaseStorageService()
            
            # Delete existing profile picture from Supabase if any
            if user.profile_picture_filename:
                try:
                    storage_service.delete_profile_picture(user.profile_picture_filename)
                except Exception as e:
                    logger.warning(f"Failed to delete old profile picture: {str(e)}")
            
            # Upload to Supabase Storage
            upload_result = storage_service.upload_profile_picture(
                user_id=str(user.id),
                file=uploaded_file,
                original_filename=uploaded_file.name
            )
            
            if not upload_result.get('success'):
                return JsonResponse({
                    'success': False, 
                    'error': upload_result.get('error', 'Failed to upload image')
                }, status=500)
            
            # Update user with Supabase URL and filename
            user.profile_picture_url = upload_result['public_url']
            user.profile_picture_filename = upload_result['filename']
            
            # Clear old Django storage if exists
            if user.profile_picture:
                user.profile_picture = None
            
            user.save(update_fields=['profile_picture_url', 'profile_picture_filename', 'profile_picture'])
            
            return JsonResponse({
                'success': True,
                'message': 'Profile picture updated successfully',
                'picture_url': upload_result['public_url']
            })
            
        except Exception as e:
            logger.error(f"Error uploading profile picture: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Failed to upload profile picture: {str(e)}'
            }, status=500)
    
    elif request.method == 'DELETE':
        # Delete profile picture
        try:
            if user.profile_picture_filename:
                from .supabase_storage import SupabaseStorageService
                storage_service = SupabaseStorageService()
                storage_service.delete_profile_picture(user.profile_picture_filename)
            
            # Clear profile picture fields
            user.profile_picture_url = None
            user.profile_picture_filename = None
            if user.profile_picture:
                user.profile_picture = None
            
            user.save(update_fields=['profile_picture_url', 'profile_picture_filename', 'profile_picture'])
            
            return JsonResponse({
                'success': True,
                'message': 'Profile picture deleted successfully'
            })
            
        except Exception as e:
            logger.error(f"Error deleting profile picture: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Failed to delete profile picture: {str(e)}'
            }, status=500)


# === DJANGO SETTINGS VIEWS ===

@csrf_protect
@django_login_required
@require_http_methods(["PATCH"])
def update_user_profile(request):
    """Update user profile settings"""
    try:
        import json
        data = json.loads(request.body)
        
        user = request.user
        
        # Update allowed fields
        allowed_fields = ['first_name', 'last_name', 'username', 'bio']
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
        
        user.save()
        
        return JsonResponse({
            'success': True,
            'data': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'bio': getattr(user, 'bio', ''),
            }
        })
        
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@csrf_protect
@django_login_required
@require_http_methods(["PATCH"])
def update_learning_settings(request):
    """Update learning settings"""
    try:
        import json
        data = json.loads(request.body)
        
        user = request.user
        
        # Update learning settings
        allowed_fields = ['native_language', 'target_language', 'language_level', 'daily_goal', 'reminder_time']
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
        
        # Validate languages
        if hasattr(user, 'native_language') and hasattr(user, 'target_language'):
            if user.native_language == user.target_language:
                return JsonResponse({
                    'success': False,
                    'error': 'Native and target languages cannot be the same'
                }, status=400)
        
        user.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Learning settings updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error updating learning settings: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@csrf_protect
@django_login_required
@require_http_methods(["POST"])
def change_user_password(request):
    """Change user password"""
    try:
        import json
        data = json.loads(request.body)
        
        user = request.user
        
        # Check old password
        if not user.check_password(data.get('old_password', '')):
            return JsonResponse({
                'success': False,
                'error': 'Current password is incorrect'
            }, status=400)
        
        # Validate new password
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')
        
        if new_password != confirm_password:
            return JsonResponse({
                'success': False,
                'error': 'New passwords do not match'
            }, status=400)
        
        if len(new_password) < 8:
            return JsonResponse({
                'success': False,
                'error': 'Password must be at least 8 characters long'
            }, status=400)
        
        # Set new password
        user.set_password(new_password)
        user.save()
        
        # Update session
        update_session_auth_hash(request, user)
        
        return JsonResponse({
            'success': True,
            'message': 'Password changed successfully'
        })
        
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


# === ADDITIONAL SETTINGS ENDPOINTS ===

@django_login_required
@require_http_methods(["GET"])
def export_user_data(request):
    """Export user data for download"""
    try:
        user = request.user
        
        # Collect user data
        user_data = {
            'profile': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'bio': getattr(user, 'bio', ''),
                'date_joined': user.date_joined.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'native_language': getattr(user, 'native_language', ''),
                'target_language': getattr(user, 'target_language', ''),
                'language_level': getattr(user, 'language_level', ''),
                'daily_goal': getattr(user, 'daily_goal', 0),
                'theme': getattr(user, 'theme', 'light'),
            },
            'settings': {
                'email_notifications': getattr(user, 'email_notifications', True),
                'push_notifications': getattr(user, 'push_notifications', False),
                'public_profile': getattr(user, 'public_profile', False),
                'reminder_time': getattr(user, 'reminder_time', None),
            },
            'exported_at': timezone.now().isoformat(),
            'export_version': '1.0',
        }
        
        # Return as downloadable JSON
        response = JsonResponse(user_data, json_dumps_params={'indent': 2})
        response['Content-Disposition'] = 'attachment; filename="mes-donnees-linguify.json"'
        return response
        
    except Exception as e:
        logger.error(f"Error exporting user data: {str(e)}")
        return JsonResponse(
            {'error': 'Failed to export data'},
            status=500
        )


@csrf_protect
@django_login_required
@require_http_methods(["POST"])
def logout_all_devices(request):
    """Logout user from all devices"""
    try:
        user = request.user
        
        # Clear all sessions for this user
        from django.contrib.sessions.models import Session
        from django.contrib.auth.models import User as AuthUser
        
        # Get all sessions and clear those belonging to this user
        sessions = Session.objects.all()
        user_sessions = []
        
        for session in sessions:
            session_data = session.get_decoded()
            if session_data.get('_auth_user_id') == str(user.id):
                user_sessions.append(session)
        
        # Delete user sessions
        for session in user_sessions:
            session.delete()
        
        # Also logout current session
        logout(request)
        
        return JsonResponse({
            'message': f'Successfully logged out from {len(user_sessions)} devices'
        })
        
    except Exception as e:
        logger.error(f"Error logging out all devices: {str(e)}")
        return JsonResponse(
            {'error': 'Failed to logout from all devices'},
            status=500
        )