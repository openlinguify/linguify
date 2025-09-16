"""
Cache service for app manager.
Centralizes cache management for user apps.
"""
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class UserAppCacheService:
    """Service for managing user app cache"""

    @staticmethod
    def get_cache_key(user_id):
        """Get cache key for user's installed apps"""
        return f"user_installed_apps_{user_id}"

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
    def set_user_apps_cache(user_id, apps_data, timeout=300):
        """Set the dashboard cache for a user"""
        cache_key = UserAppCacheService.get_cache_key(user_id)
        cache.set(cache_key, apps_data, timeout)
        logger.debug(f"Set user apps cache for user {user_id} with {len(apps_data)} apps")

    @staticmethod
    def get_user_apps_cache(user_id):
        """Get the dashboard cache for a user"""
        cache_key = UserAppCacheService.get_cache_key(user_id)
        return cache.get(cache_key)