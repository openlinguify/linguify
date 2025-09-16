"""
Cache service for app manager.
Centralizes cache management for user apps with intelligent versioning.
"""
from django.core.cache import cache
from django.utils import timezone
import logging
import hashlib

logger = logging.getLogger(__name__)


class UserAppCacheService:
    """Service for managing user app cache with intelligent invalidation"""

    CACHE_VERSION = "v2"  # Increment when changing cache structure
    CACHE_TIMEOUT = 300   # 5 minutes default
    CACHE_TIMEOUT_LONG = 3600  # 1 hour for static data

    @staticmethod
    def get_cache_key(user_id, key_type="apps"):
        """Get cache key for user's installed apps"""
        return f"user_{key_type}_{user_id}_{UserAppCacheService.CACHE_VERSION}"

    @staticmethod
    def clear_user_apps_cache(user_id):
        """Clear the dashboard cache for a specific user"""
        cache_key = UserAppCacheService.get_cache_key(user_id)
        cache.delete(cache_key)
        logger.debug(f"Cleared user apps cache for user {user_id}")

    @staticmethod
    def clear_user_apps_cache_for_user(user):
        """Clear the dashboard cache for a user object"""
        UserAppCacheService.clear_user_apps_cache(user.id)

    @staticmethod
    def set_user_apps_cache(user_id, apps_data, timeout=None):
        """Set the dashboard cache for a user with optimized timeout"""
        if timeout is None:
            timeout = UserAppCacheService.CACHE_TIMEOUT

        cache_key = UserAppCacheService.get_cache_key(user_id)

        # Add timestamp for cache freshness validation
        cache_data = {
            'apps': apps_data,
            'cached_at': timezone.now().timestamp(),
            'app_count': len(apps_data)
        }

        cache.set(cache_key, cache_data, timeout)
        logger.debug(f"Set user apps cache for user {user_id} with {len(apps_data)} apps")

    @staticmethod
    def get_user_apps_cache(user_id):
        """Get the dashboard cache for a user with freshness validation"""
        cache_key = UserAppCacheService.get_cache_key(user_id)
        cached_data = cache.get(cache_key)

        if cached_data and isinstance(cached_data, dict):
            # Return apps from new cache format
            return cached_data.get('apps')
        elif cached_data and isinstance(cached_data, list):
            # Legacy cache format - still return it but it will be updated next time
            return cached_data

        return None

    @staticmethod
    def get_app_store_cache():
        """Cache for App Store data (changes less frequently)"""
        cache_key = f"app_store_data_{UserAppCacheService.CACHE_VERSION}"
        return cache.get(cache_key)

    @staticmethod
    def set_app_store_cache(data, timeout=None):
        """Set App Store cache with longer timeout"""
        if timeout is None:
            timeout = UserAppCacheService.CACHE_TIMEOUT_LONG

        cache_key = f"app_store_data_{UserAppCacheService.CACHE_VERSION}"
        cache.set(cache_key, data, timeout)
        logger.debug(f"Set app store cache with {len(data.get('apps', []))} apps")

    @staticmethod
    def clear_app_store_cache():
        """Clear App Store cache when apps are added/modified"""
        cache_key = f"app_store_data_{UserAppCacheService.CACHE_VERSION}"
        cache.delete(cache_key)
        logger.debug("Cleared app store cache")