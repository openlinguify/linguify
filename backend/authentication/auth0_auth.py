# authentication/auth0_auth.py
import jwt
import json
import requests
from django.conf import settings
from rest_framework import authentication, exceptions
from django.contrib.auth import get_user_model
import logging
import time
from jwt.algorithms import RSAAlgorithm
from django.core.cache import cache

logger = logging.getLogger(__name__)
User = get_user_model()

class Auth0Authentication(authentication.BaseAuthentication):
    """
    Authentication for DRF using Auth0 JWT tokens with local verification.
    """
    
    def __init__(self):
        self.jwks = None
        self.jwks_last_fetched = 0
        self.jwks_cache_time = 86400  # Cache JWKS for 24 hours

    def get_jwks(self):
        """Fetch and cache JWKS from Auth0"""
        current_time = time.time()
        
        # Check if we need to fetch new JWKS
        if not self.jwks or (current_time - self.jwks_last_fetched) > self.jwks_cache_time:
            try:
                jwks_url = f'https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json'
                logger.debug(f"Fetching JWKS from {jwks_url}")
                response = requests.get(jwks_url)
                if response.status_code == 200:
                    self.jwks = response.json()
                    self.jwks_last_fetched = current_time
                    logger.debug("JWKS fetched successfully")
                else:
                    logger.error(f"Failed to fetch JWKS: {response.status_code}")
            except Exception as e:
                logger.exception(f"Error fetching JWKS: {str(e)}")
        
        return self.jwks
    
    def verify_token(self, token):
        """Verify the JWT token using the JWKS from Auth0"""
        try:
            # Get token header data
            token_header = jwt.get_unverified_header(token)
            
            # Get JWKS
            jwks = self.get_jwks()
            if not jwks:
                logger.error("No JWKS available for token verification")
                return None
            
            # Find the right key from JWKS
            rsa_key = {}
            for key in jwks['keys']:
                if key['kid'] == token_header['kid']:
                    rsa_key = {
                        'kty': key['kty'],
                        'kid': key['kid'],
                        'use': key['use'],
                        'n': key['n'],
                        'e': key['e']
                    }
                    break
            
            if not rsa_key:
                logger.error(f"No matching key found in JWKS for kid: {token_header.get('kid')}")
                return None
            
            # Verify token
            payload = jwt.decode(
                token,
                RSAAlgorithm.from_jwk(json.dumps(rsa_key)),
                algorithms=['RS256'],
                audience=settings.AUTH0_AUDIENCE,
                issuer=f'https://{settings.AUTH0_DOMAIN}/'
            )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {str(e)}")
            return None
        except Exception as e:
            logger.exception(f"Token verification error: {str(e)}")
            return None
    
    def get_user_from_payload(self, payload):
        """Get or create user from token payload"""
        try:
            sub = payload.get('sub')
            email = payload.get('email')
            
            if not email:
                logger.error("No email in payload")
                return None
                
            # Check cache for this user
            cache_key = f"auth0_user_{email}"
            cached_user = cache.get(cache_key)
            if cached_user:
                logger.debug(f"User found in cache: {email}")
                return cached_user
            
            # Get or create user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': payload.get('nickname', email.split('@')[0]),
                    'first_name': payload.get('given_name', ''),
                    'last_name': payload.get('family_name', '')
                }
            )
            
            if created:
                logger.info(f"New user created: {user.email}")
            else:
                # Only update user if needed
                update_fields = []
                if 'nickname' in payload and user.username != payload['nickname']:
                    user.username = payload['nickname']
                    update_fields.append('username')
                if 'given_name' in payload and user.first_name != payload['given_name']:
                    user.first_name = payload['given_name']
                    update_fields.append('first_name')
                if 'family_name' in payload and user.last_name != payload['family_name']:
                    user.last_name = payload['family_name']
                    update_fields.append('last_name')
                
                if update_fields:
                    user.save(update_fields=update_fields)
            
            # Cache user for 5 minutes
            cache.set(cache_key, user, 300)
            
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
        
        # Debug the auth header
        logger.debug(f"Auth header: {auth_header[:20]}...")

        if not auth_header.startswith('Bearer '):
            logger.debug("No Bearer token found in request")
            return None

        # Extract the token
        token = auth_header.split(' ')[1]
        logger.debug(f"Token extracted: {token[:10]}...")
        
        try:
            # First try to verify token locally without calling Auth0
            payload = self.verify_token(token)
            
            if payload:
                logger.debug("Token verified successfully")
                # Get user from payload
                user = self.get_user_from_payload(payload)
                if user:
                    logger.debug(f"User authenticated: {user.email}")
                    # Store user ID on request for debugging
                    request.auth0_user_id = payload.get('sub')
                    return (user, token)
                else:
                    logger.warning("Token valid but user not found/created")
            else:
                logger.warning("Token verification failed")
                    
            # If local verification fails or no user found, try Auth0 userinfo endpoint
            # as a fallback, but only if we haven't hit rate limits
            if not payload or not user:
                logger.debug("Trying Auth0 userinfo endpoint as fallback")
                # Check if we're rate limited
                rate_limit_key = "auth0_rate_limited"
                if cache.get(rate_limit_key):
                    logger.warning("Auth0 rate limit in effect, skipping userinfo call")
                    raise exceptions.AuthenticationFailed("Authentication service temporarily unavailable")
                
                try:
                    logger.debug(f"Attempting to get user info from Auth0 with token: {token[:10]}...")
                    userinfo_response = requests.get(
                        f'https://{settings.AUTH0_DOMAIN}/userinfo',
                        headers={'Authorization': f'Bearer {token}'}
                    )
                    
                    if userinfo_response.status_code == 429:
                        # We're being rate limited, set a cache flag for 5 minutes
                        cache.set(rate_limit_key, True, 300)
                        logger.error(f"Auth0 rate limit reached: {userinfo_response.status_code}")
                        logger.error(f"Response content: {userinfo_response.text}")
                        raise exceptions.AuthenticationFailed("Authentication service temporarily unavailable")
                    
                    if not userinfo_response.ok:
                        logger.error(f"Failed to get user info: {userinfo_response.status_code}")
                        logger.error(f"Response content: {userinfo_response.text}")
                        raise exceptions.AuthenticationFailed('Failed to get user info')
                    
                    user_info = userinfo_response.json()
                    logger.debug(f"User info received from Auth0: {user_info}")
                    
                    if 'email' not in user_info:
                        logger.error("Email not found in user info")
                        raise exceptions.AuthenticationFailed('Email not found in user info')
                    
                    # Get or create the user
                    user, created = User.objects.get_or_create(
                        email=user_info['email'],
                        defaults={
                            'username': user_info.get('nickname', user_info['email'].split('@')[0]),
                            'first_name': user_info.get('given_name', ''),
                            'last_name': user_info.get('family_name', '')
                        }
                    )
                    
                    if created:
                        logger.info(f"New user created from userinfo: {user.email}")
                    
                    # Store auth user ID on request for debugging
                    request.auth0_user_id = user_info.get('sub')
                    
                    return (user, token)
                except Exception as e:
                    if isinstance(e, exceptions.AuthenticationFailed):
                        raise
                    logger.exception(f"Error in Auth0 userinfo call: {str(e)}")
                    raise exceptions.AuthenticationFailed('Authentication failed')
            
            # If we get here, authentication failed
            raise exceptions.AuthenticationFailed('Invalid authentication credentials')
        
        except jwt.ExpiredSignatureError:
            logger.error("Token has expired")
            raise exceptions.AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            logger.error("Invalid token")
            raise exceptions.AuthenticationFailed('Invalid token')
        except Exception as e:
            if isinstance(e, exceptions.AuthenticationFailed):
                raise
            logger.exception(f"Authentication failed: {str(e)}")
            raise exceptions.AuthenticationFailed(str(e))
    
    def authenticate_header(self, request):
        return 'Bearer'