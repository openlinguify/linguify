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
    Authentication for DRF using Auth0 JWT tokens with enhanced caching.
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
            jwks_cache_key = f"auth0_jwks_{settings.AUTH0_DOMAIN}"
            cached_jwks = cache.get(jwks_cache_key)
            
            if cached_jwks:
                logger.debug("Using cached JWKS")
                self.jwks = cached_jwks
                self.jwks_last_fetched = current_time
                return self.jwks
            
            try:
                jwks_url = f'https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json'
                logger.debug(f"Fetching JWKS from {jwks_url}")
                response = requests.get(jwks_url, timeout=5)
                if response.status_code == 200:
                    self.jwks = response.json()
                    self.jwks_last_fetched = current_time
                    # Cache JWKS
                    cache.set(jwks_cache_key, self.jwks, 3600)  # Cache for 1 hour
                    logger.debug("JWKS fetched successfully")
                else:
                    logger.error(f"Failed to fetch JWKS: {response.status_code}")
            except Exception as e:
                logger.exception(f"Error fetching JWKS: {str(e)}")
        
        return self.jwks
    
    def verify_token(self, token):
        """Verify the JWT token using the JWKS from Auth0 with enhanced caching"""
        try:
            # Check if we already have token verification results in cache
            token_hash = hash(token)
            token_cache_key = f"auth0_token_{token_hash}"
            cached_result = cache.get(token_cache_key)
            
            if cached_result:
                logger.debug("Using cached token verification result")
                return cached_result
                
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
            
            # If verification succeeds, cache the result
            if payload:
                # Get token expiration time
                exp = payload.get('exp', 0)
                current_time = int(time.time())
                # Cache until token expiration or max 1 hour, whichever is shorter
                cache_time = min(exp - current_time, 3600) if exp > current_time else 3600
                if cache_time > 0:
                    cache.set(token_cache_key, payload, cache_time)
                    logger.debug(f"Token verification result cached for {cache_time} seconds")

            # Log token without email claim
            if payload and 'sub' in payload and 'email' not in payload:
                logger.warning(f"Token for {payload['sub']} has no email claim. Check Auth0 configuration.")
            
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
    
    def get_user_info_from_auth0(self, token):
        """Get user info from Auth0 userinfo endpoint with rate limit handling"""
        
        # Check if rate limited
        rate_limit_key = "auth0_rate_limited"
        if cache.get(rate_limit_key):
            logger.warning("Auth0 rate limit active, skipping userinfo call")
            return None, True
        
        try:
            user_info_url = f'https://{settings.AUTH0_DOMAIN}/userinfo'
            logger.debug(f"Getting user info from {user_info_url}")
            
            response = requests.get(
                user_info_url,
                headers={'Authorization': f'Bearer {token}'},
                timeout=5
            )
            
            # Check for rate limit
            if response.status_code == 429:
                # Set rate limit flag for 5 minutes
                cache.set(rate_limit_key, True, 300)
                logger.error(f"Auth0 rate limit reached: {response.status_code}")
                logger.error(f"Response content: {response.text}")
                return None, True
            
            if response.status_code == 200:
                user_info = response.json()
                return user_info, False
            
            logger.error(f"Failed to get user info: {response.status_code}")
            return None, False
            
        except Exception as e:
            logger.exception(f"Error getting user info: {str(e)}")
            return None, False
    
    def get_user_from_payload(self, payload, token=None):
        """Get or create user from token payload with enhanced caching"""
        try:
            sub = payload.get('sub')
            email = payload.get('email')
            
            # If email is missing from payload but we have a token, try userinfo
            if not email and token:
                # Check cache for this user by sub
                user_cache_key = f"auth0_user_sub_{sub}"
                cached_user = cache.get(user_cache_key)
                if cached_user:
                    logger.debug(f"User found in cache by sub: {sub}")
                    return cached_user
                
                # Try to get user info from Auth0
                user_info, rate_limited = self.get_user_info_from_auth0(token)
                
                if rate_limited:
                    # Try to find existing user by sub or use fallback
                    try:
                        # Look for user with matching sub in username (common pattern)
                        if sub:
                            # Extract the ID part from the sub claim (after the |)
                            sub_id = sub.split('|')[-1]
                            existing_user = User.objects.filter(username__icontains=sub_id[:8]).first()
                            if existing_user:
                                logger.info(f"Found existing user {existing_user.username} for sub {sub}")
                                return existing_user
                        
                        # Fall back to most recent user as last resort
                        fallback_user = User.objects.latest('created_at')
                        logger.warning(f"Using fallback user due to Auth0 rate limits: {fallback_user.username}")
                        return fallback_user
                    except User.DoesNotExist:
                        logger.error("No fallback user available")
                        return None
                
                if user_info and user_info.get('email'):
                    email = user_info.get('email')
                    # Continue with user creation/update below
                else:
                    logger.error(f"No email in payload or user info for {sub}")
                    return None
            
            if not email:
                logger.error(f"No email found in payload and no token provided")
                return None
                
            # Check cache for this user by email
            user_cache_key = f"auth0_user_email_{email}"
            cached_user = cache.get(user_cache_key)
            if cached_user:
                logger.debug(f"User found in cache by email: {email}")
                return cached_user
            
            # Get or create user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': (payload.get('nickname') or email.split('@')[0])[:30],  # Ensure username length limit
                    'first_name': (payload.get('given_name') or '')[:30],
                    'last_name': (payload.get('family_name') or '')[:30]
                }
            )
            
            if created:
                logger.info(f"New user created: {user.email}")
            else:
                # Only update user if needed
                update_fields = []
                if 'nickname' in payload and user.username != payload['nickname'][:30]:
                    user.username = payload['nickname'][:30]
                    update_fields.append('username')
                if 'given_name' in payload and user.first_name != payload['given_name'][:30]:
                    user.first_name = payload['given_name'][:30]
                    update_fields.append('first_name')
                if 'family_name' in payload and user.last_name != payload['family_name'][:30]:
                    user.last_name = payload['family_name'][:30]
                    update_fields.append('last_name')
                
                if update_fields:
                    user.save(update_fields=update_fields)
            
            # Cache user for 2 hours
            cache.set(user_cache_key, user, 7200)
            
            # Also cache by sub if available
            if sub:
                cache.set(f"auth0_user_sub_{sub}", user, 7200)
            
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
        if hasattr(request, '_auth0_user') and hasattr(request, '_auth0_token') and request._auth0_token == token:
            return (request._auth0_user, token)
        
        try:
            # First check for existing authentication in the session
            session_key = f"auth0_session_{hash(token)}"
            cached_user_id = request.session.get(session_key)
            
            if cached_user_id:
                try:
                    user = User.objects.get(id=cached_user_id)
                    logger.debug(f"User authenticated from session: {user.email}")
                    
                    # Store for reuse within request
                    request._auth0_user = user
                    request._auth0_token = token
                    
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
                    request._auth0_user = user
                    request._auth0_token = token
                    
                    return (user, token)
                else:
                    logger.warning("Token valid but user not found/created")
            else:
                logger.warning("Token verification failed")
            
            # Authentication failed
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