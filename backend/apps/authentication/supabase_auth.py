# authentication/supabase_auth.py
import jwt
import json
import requests
from django.conf import settings
from rest_framework import authentication, exceptions
from django.contrib.auth import get_user_model
import logging
import time
from django.core.cache import cache
from uuid import uuid4
import os

logger = logging.getLogger(__name__)
User = get_user_model()

class SupabaseAuthentication(authentication.BaseAuthentication):
    """
    Authentication for DRF using Supabase JWT tokens.
    """
    
    def __init__(self):
        self.jwt_secret = settings.SUPABASE_JWT_SECRET
        self.project_url = settings.SUPABASE_URL
        self.service_role_key = settings.SUPABASE_SERVICE_ROLE_KEY

    def verify_token(self, token):
        """Verify the JWT token using Supabase JWT secret"""
        try:
            # Check cache first
            token_hash = hash(token)
            token_cache_key = f"supabase_token_{token_hash}"
            cached_result = cache.get(token_cache_key)
            
            if cached_result:
                logger.debug("Using cached token verification result")
                return cached_result
                
            try:
                # Verify token with Supabase JWT secret
                payload = jwt.decode(
                    token,
                    self.jwt_secret,
                    algorithms=['HS256'],
                    audience='authenticated',
                    issuer=f'{self.project_url}/auth/v1',
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
                    leeway=30  # 30 seconds tolerance for clock skew
                )
                
                # Cache successful verification result
                if payload:
                    # Cache until token expiration or max 1 hour
                    exp = payload.get('exp', 0)
                    current_time = int(time.time())
                    cache_time = min(exp - current_time, 3600) if exp > current_time else 3600
                    if cache_time > 0:
                        cache.set(token_cache_key, payload, cache_time)
                        logger.debug(f"Token verification result cached for {cache_time} seconds")
                
                return payload
                
            except jwt.InvalidTokenError as e:
                logger.error(f"Invalid token: {str(e)}")
                return None
                
        except Exception as e:
            logger.exception(f"Token verification error: {str(e)}")
            return None
    
    def get_user_info_from_supabase(self, user_id):
        """Get user info from Supabase using the service role key"""
        
        # Check cache for this user's info
        userinfo_cache_key = f"supabase_userinfo_{user_id}"
        cached_userinfo = cache.get(userinfo_cache_key)
        
        if cached_userinfo:
            logger.debug("Using cached user info")
            return cached_userinfo, False
        
        try:
            user_info_url = f'{self.project_url}/auth/v1/admin/users/{user_id}'
            logger.debug(f"Getting user info from {user_info_url}")
            
            response = requests.get(
                user_info_url,
                headers={
                    'Authorization': f'Bearer {self.service_role_key}',
                    'apikey': self.service_role_key
                },
                timeout=5
            )
            
            if response.status_code == 200:
                user_info = response.json()
                # Cache userinfo for 15 minutes
                cache.set(userinfo_cache_key, user_info, 900)
                return user_info, False
            
            logger.error(f"Failed to get user info: {response.status_code}")
            return None, False
            
        except Exception as e:
            logger.exception(f"Error getting user info: {str(e)}")
            return None, False
    
    def get_user_from_payload(self, payload, token=None):
        """Get or create user from token payload"""
        try:
            sub = payload.get('sub')  # Supabase user ID
            email = payload.get('email')
            
            if not sub:
                logger.error("No sub (user ID) found in payload")
                return None
            
            # Check cache for this user by sub
            user_cache_key = f"supabase_user_sub_{sub}"
            cached_user = cache.get(user_cache_key)
            if cached_user:
                logger.debug(f"User found in cache by sub: {sub}")
                return cached_user
            
            # If email is missing from payload, try to get user info from Supabase
            if not email:
                user_info, error = self.get_user_info_from_supabase(sub)
                if user_info and user_info.get('email'):
                    email = user_info.get('email')
                    # Update payload with additional info if available
                    if 'user_metadata' in user_info:
                        metadata = user_info['user_metadata']
                        payload.update({
                            'given_name': metadata.get('first_name', ''),
                            'family_name': metadata.get('last_name', ''),
                            'nickname': metadata.get('username', email.split('@')[0] if email else '')
                        })
            
            if not email:
                logger.error(f"No email found for user {sub}")
                return None
            
            # Check cache for this user by email
            user_cache_key_email = f"supabase_user_email_{email}"
            cached_user = cache.get(user_cache_key_email)
            if cached_user:
                logger.debug(f"User found in cache by email: {email}")
                # Also cache by sub
                cache.set(user_cache_key, cached_user, 1800)
                return cached_user
            
            # Get or create user
            try:
                user = User.objects.get(email=email)
                logger.debug(f"Found existing user for email: {email}")
                
                # Update user if needed
                update_fields = []
                
                # Update username if we have nickname and it's different
                if 'nickname' in payload and payload['nickname'] and user.username != payload['nickname'][:30]:
                    user.username = payload['nickname'][:30]
                    update_fields.append('username')
                if 'given_name' in payload and payload['given_name'] and user.first_name != payload['given_name'][:30]:
                    user.first_name = payload['given_name'][:30]
                    update_fields.append('first_name')
                if 'family_name' in payload and payload['family_name'] and user.last_name != payload['family_name'][:30]:
                    user.last_name = payload['family_name'][:30]
                    update_fields.append('last_name')
                
                if update_fields:
                    user.save(update_fields=update_fields)
                    logger.info(f"Updated user {email} fields: {update_fields}")
                    
            except User.DoesNotExist:
                # Create new user
                username = (payload.get('nickname') or email.split('@')[0])[:30]
                first_name = (payload.get('given_name') or '')[:30]
                last_name = (payload.get('family_name') or '')[:30]
                
                user = User.objects.create(
                    email=email,
                    username=username or email.split('@')[0],
                    first_name=first_name or '',
                    last_name=last_name or '',
                    password=uuid4().hex  # Random password for OAuth users
                )
                logger.info(f"Created new user: {email}")
            
            # Cache user for 30 minutes
            cache.set(user_cache_key, user, 1800)
            cache.set(user_cache_key_email, user, 1800)
            
            return user
            
        except Exception as e:
            logger.exception(f"Error getting user from payload: {str(e)}")
            return None
    
    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token).
        """
        # Get the auth header
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return None

        # Extract the token
        token = auth_header.split(' ')[1]
        
        # Look for user in request for optimized reuse
        if hasattr(request, '_supabase_user') and hasattr(request, '_supabase_token') and request._supabase_token == token:
            return (request._supabase_user, token)
        
        try:
            # First check for existing authentication in the session
            session_key = f"supabase_session_{hash(token)}"
            cached_user_id = request.session.get(session_key)
            
            if cached_user_id:
                try:
                    user = User.objects.get(id=cached_user_id)
                    logger.debug(f"User authenticated from session: {user.email}")
                    
                    # Store for reuse within request
                    request._supabase_user = user
                    request._supabase_token = token
                    
                    # Also attach supabase_user attribute for middleware
                    request.supabase_user = user
                    
                    return (user, token)
                except User.DoesNotExist:
                    # Session refers to user that no longer exists
                    del request.session[session_key]
            
            # Verify token locally
            payload = self.verify_token(token)
            
            if payload:
                # Get user from payload
                user = self.get_user_from_payload(payload, token)
                if user:
                    logger.debug(f"User authenticated: {user.email}")
                    
                    # Store auth details in session for future requests
                    request.session[session_key] = user.id
                    
                    # Store for reuse within request
                    request._supabase_user = user
                    request._supabase_token = token
                    
                    # Also attach supabase_user attribute for middleware
                    request.supabase_user = user
                    
                    return (user, token)
                else:
                    logger.warning("Token valid but user not found/created")
            else:
                logger.warning("Token verification failed")
            
            # Authentication failed
            raise exceptions.AuthenticationFailed('Invalid authentication credentials')
        
        except Exception as jwt_error:
            # Handle JWT-related errors
            error_msg = str(jwt_error)
            if 'expired' in error_msg.lower():
                logger.error("Token has expired")
                raise exceptions.AuthenticationFailed('Token has expired')
            elif any(term in error_msg.lower() for term in ['invalid', 'signature', 'token']):
                logger.error(f"Invalid token: {error_msg}")
                raise exceptions.AuthenticationFailed('Invalid token')
            else:
                logger.error(f"JWT error: {error_msg}")
                raise exceptions.AuthenticationFailed('Authentication failed')
        except Exception as e:
            if isinstance(e, exceptions.AuthenticationFailed):
                raise
            logger.exception(f"Authentication failed: {str(e)}")
            raise exceptions.AuthenticationFailed(str(e))
    
    def authenticate_header(self, request):
        return 'Bearer'