from django.http import JsonResponse
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
import logging

logger = logging.getLogger(__name__)

@api_view(['GET', 'OPTIONS'])
@permission_classes([AllowAny])
def cors_debug(request):
    """
    Vue de diagnostic pour les problèmes CORS.
    À utiliser uniquement en développement.
    """
    if not settings.DEBUG:
        return JsonResponse({'error': 'Debug endpoint disabled in production'}, status=403)

    # Log detailed information about the request
    logger.debug("=== CORS Debug Information ===")
    logger.debug(f"Request Method: {request.method}")
    logger.debug(f"Request Path: {request.path}")
    
    logger.debug("\nRequest Headers:")
    for header, value in request.headers.items():
        logger.debug(f"{header}: {value}")

    logger.debug("\nCORS Settings:")
    logger.debug(f"CORS_ALLOWED_ORIGINS: {settings.CORS_ALLOWED_ORIGINS}")
    logger.debug(f"CORS_ALLOW_CREDENTIALS: {settings.CORS_ALLOW_CREDENTIALS}")
    logger.debug(f"CORS_ALLOW_HEADERS: {settings.CORS_ALLOW_HEADERS}")

    # Return detailed debug information
    return JsonResponse({
        'cors_debug': {
            'request': {
                'method': request.method,
                'path': request.path,
                'headers': dict(request.headers),
                'origin': request.headers.get('origin'),
            },
            'cors_settings': {
                'allowed_origins': settings.CORS_ALLOWED_ORIGINS,
                'allow_credentials': settings.CORS_ALLOW_CREDENTIALS,
                'allow_headers': settings.CORS_ALLOW_HEADERS,
            },
            'meta': {
                key: str(value)
                for key, value in request.META.items()
                if key.startswith('HTTP_') or key in ['REMOTE_ADDR', 'SERVER_NAME']
            }
        }
    })

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def debug_supabase_config(request):
    """Endpoint pour déboguer la configuration Supabase"""
    if not settings.DEBUG:
        return JsonResponse({'error': 'Debug endpoint disabled in production'}, status=403)
    
    config_info = {
        'supabase_url': getattr(settings, 'SUPABASE_URL', 'NOT_SET'),
        'has_jwt_secret': bool(getattr(settings, 'SUPABASE_JWT_SECRET', '')),
        'jwt_secret_length': len(getattr(settings, 'SUPABASE_JWT_SECRET', '')),
        'has_service_key': bool(getattr(settings, 'SUPABASE_SERVICE_ROLE_KEY', '')),
        'use_supabase_db': getattr(settings, 'USE_SUPABASE_DB', None),
        'debug': settings.DEBUG,
    }
    
    return JsonResponse({
        'status': 'ok',
        'config': config_info
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def test_token_verification(request):
    """Endpoint pour tester la vérification d'un token"""
    if not settings.DEBUG:
        return JsonResponse({'error': 'Debug endpoint disabled in production'}, status=403)
        
    try:
        import json
        
        # Get token from request body
        body = json.loads(request.body)
        token = body.get('token')
        
        if not token:
            return JsonResponse({
                'status': 'error',
                'message': 'Token required'
            })
        
        # Manual JWT verification with detailed error reporting
        import jwt
        
        jwt_secret = getattr(settings, 'SUPABASE_JWT_SECRET', '')
        supabase_url = getattr(settings, 'SUPABASE_URL', '')
        
        debug_info = {
            'has_jwt_secret': bool(jwt_secret),
            'jwt_secret_length': len(jwt_secret),
            'supabase_url': supabase_url,
            'expected_issuer': f'{supabase_url}/auth/v1',
        }
        
        if not jwt_secret:
            return JsonResponse({
                'status': 'error',
                'message': 'No JWT secret configured',
                'debug_info': debug_info
            })
        
        try:
            # Try to decode without verification first to see the payload
            unverified_payload = jwt.decode(token, options={"verify_signature": False})
            debug_info['token_payload'] = {
                'iss': unverified_payload.get('iss'),
                'aud': unverified_payload.get('aud'),
                'sub': unverified_payload.get('sub'),
                'email': unverified_payload.get('email'),
                'exp': unverified_payload.get('exp'),
                'iat': unverified_payload.get('iat')
            }
            
            # Now try to verify with our secret
            payload = jwt.decode(
                token,
                jwt_secret,
                algorithms=['HS256'],
                audience='authenticated',
                issuer=f'{supabase_url}/auth/v1',
                options={
                    'verify_signature': True,
                    'verify_exp': True,
                    'verify_nbf': True,
                    'verify_iat': True,
                    'verify_aud': True,
                    'verify_iss': True,
                    'require_exp': True,
                    'require_iat': True,
                    'require_nbf': False
                },
                leeway=30
            )
            
            return JsonResponse({
                'status': 'success',
                'message': 'Token is valid',
                'payload': {
                    'sub': payload.get('sub'),
                    'email': payload.get('email'),
                    'aud': payload.get('aud'),
                    'iss': payload.get('iss'),
                    'exp': payload.get('exp'),
                    'iat': payload.get('iat')
                },
                'debug_info': debug_info
            })
            
        except jwt.InvalidSignatureError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid signature - JWT secret mismatch',
                'debug_info': debug_info
            })
        except jwt.ExpiredSignatureError:
            return JsonResponse({
                'status': 'error',
                'message': 'Token has expired',
                'debug_info': debug_info
            })
        except jwt.InvalidAudienceError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid audience',
                'debug_info': debug_info
            })
        except jwt.InvalidIssuerError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid issuer',
                'debug_info': debug_info
            })
        except Exception as jwt_error:
            return JsonResponse({
                'status': 'error',
                'message': f'JWT verification failed: {str(jwt_error)}',
                'debug_info': debug_info
            })
            
    except Exception as e:
        logger.exception(f"Error in token verification test: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

@api_view(['GET'])
@permission_classes([AllowAny])
def debug_auth_headers(request):
    """Endpoint pour déboguer les headers d'authentification"""
    if not settings.DEBUG:
        return JsonResponse({'error': 'Debug endpoint disabled in production'}, status=403)
    
    auth_header = request.headers.get('Authorization', '')
    
    info = {
        'has_auth_header': bool(auth_header),
        'auth_header_starts_with_bearer': auth_header.startswith('Bearer '),
        'auth_header_length': len(auth_header),
    }
    
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        info['token_length'] = len(token)
        info['token_preview'] = token[:20] + '...' if len(token) > 20 else token
    
    return JsonResponse({
        'status': 'ok',
        'auth_info': info,
        'all_headers': dict(request.headers)
    })

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def test_token(request):
    """Test endpoint to verify if authentication is working"""
    try:
        user = request.user
        
        # Get the authorization header
        auth_header = request.headers.get('Authorization', '')
        token = None
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        # Try to decode the token for debugging
        token_info = None
        if token and settings.DEBUG:
            try:
                import jwt
                # Decode without verification for debugging
                token_info = jwt.decode(
                    token,
                    options={"verify_signature": False},
                    algorithms=["HS256"]
                )
            except Exception as e:
                logger.error(f"Error decoding token for debug: {e}")
        
        response_data = {
            'message': 'Authentication successful',
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_authenticated': user.is_authenticated,
                'date_joined': user.date_joined.isoformat() if hasattr(user, 'date_joined') else None,
            },
            'token_preview': f"{token[:20]}..." if token else None,
        }
        
        # Add token info in debug mode
        if settings.DEBUG and token_info:
            response_data['token_debug'] = {
                'iss': token_info.get('iss'),
                'aud': token_info.get('aud'),
                'role': token_info.get('role'),
                'sub': token_info.get('sub'),
                'exp': token_info.get('exp'),
                'iat': token_info.get('iat'),
            }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error in test_token view: {e}")
        return JsonResponse({
            'error': 'Internal server error',
            'detail': str(e) if settings.DEBUG else 'Authentication test failed'
        }, status=500)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def debug_apps_system(request):
    """Endpoint pour déboguer le système d'apps"""
    if not settings.DEBUG:
        return JsonResponse({'error': 'Debug endpoint disabled in production'}, status=403)
    
    try:
        from app_manager.models import App, UserAppSettings
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # Vérifier les apps définies
        apps = App.objects.all()
        apps_data = [
            {
                'code': app.code,
                'display_name': app.display_name,
                'is_enabled': app.is_enabled,
                'order': app.order
            }
            for app in apps
        ]
        
        # Si POST, essayer de créer les apps par défaut
        if request.method == 'POST':
            default_apps = [
                {
                    'code': 'learning',
                    'display_name': 'Learning',
                    'description': 'Interactive language lessons and exercises',
                    'icon_name': 'BookOpen',
                    'color': '#8B5CF6',
                    'route_path': '/learning',
                    'is_enabled': True,
                    'order': 1
                },
                {
                    'code': 'memory',
                    'display_name': 'Memory',
                    'description': 'Memory training with spaced repetition (Flashcards)',
                    'icon_name': 'Brain',
                    'color': '#EF4444',
                    'route_path': '/flashcard',
                    'is_enabled': True,
                    'order': 2
                },
                {
                    'code': 'notes',
                    'display_name': 'Notes',
                    'description': 'Take notes and organize vocabulary',
                    'icon_name': 'NotebookPen',
                    'color': '#06B6D4',
                    'route_path': '/notebook',
                    'is_enabled': True,
                    'order': 3
                },
                {
                    'code': 'conversation_ai',
                    'display_name': 'Conversation AI',
                    'description': 'Practice conversations with AI',
                    'icon_name': 'MessageSquare',
                    'color': '#F59E0B',
                    'route_path': '/language_ai',
                    'is_enabled': True,
                    'order': 4
                }
            ]
            
            created_count = 0
            for app_data in default_apps:
                app, created = App.objects.get_or_create(
                    code=app_data['code'],
                    defaults=app_data
                )
                if created:
                    created_count += 1
            
            # Re-get apps after creation
            apps = App.objects.all()
            apps_data = [
                {
                    'code': app.code,
                    'display_name': app.display_name,
                    'is_enabled': app.is_enabled,
                    'order': app.order
                }
                for app in apps
            ]
        
        # Vérifier l'utilisateur actuel (si authentifié)
        user_info = None
        user_settings_info = None
        
        if hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
            user_info = {
                'id': user.id,
                'email': user.email,
                'username': getattr(user, 'username', 'N/A')
            }
            
            user_settings = UserAppSettings.objects.filter(user=user).first()
            if user_settings:
                user_settings_info = {
                    'enabled_apps': user_settings.enabled_apps,
                    'preferences': user_settings.user_preferences
                }
            else:
                # Créer des settings par défaut si l'utilisateur est authentifié
                enabled_apps = [app.code for app in apps if app.is_enabled]
                if enabled_apps:
                    UserAppSettings.objects.create(
                        user=user,
                        enabled_apps=enabled_apps
                    )
                    user_settings_info = {
                        'enabled_apps': enabled_apps,
                        'preferences': {},
                        'created': True
                    }
        
        return JsonResponse({
            'status': 'success',
            'apps_count': len(apps_data),
            'apps': apps_data,
            'user_info': user_info,
            'user_settings': user_settings_info,
            'method': request.method
        })
        
    except Exception as e:
        logger.exception(f"Error in debug_apps_system: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        })