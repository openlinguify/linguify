# backend/apps/notification/redis_utils.py
import os
import logging
import redis
from django.conf import settings

logger = logging.getLogger(__name__)

def get_redis_connection():
    """
    Get a Redis connection with proper error handling and fallbacks
    
    Returns:
        Redis connection object or None if connection fails
    """
    try:
        # Get Redis configuration from settings
        redis_host = os.environ.get('REDIS_HOST', '127.0.0.1')
        redis_port = int(os.environ.get('REDIS_PORT', 6379))
        
        # Try to connect to Redis
        connection = redis.Redis(
            host=redis_host,
            port=redis_port,
            socket_timeout=5,  # 5 second timeout
            socket_connect_timeout=5,
            retry_on_timeout=True
        )
        
        # Test the connection
        connection.ping()
        logger.info(f"Successfully connected to Redis at {redis_host}:{redis_port}")
        
        return connection
    except redis.ConnectionError as e:
        logger.error(f"Failed to connect to Redis: {e}")
        # Try alternate Redis hosts
        alternate_hosts = [
            'localhost',
            '127.0.0.1',
            'redis',
            'host.docker.internal'  # For Docker to host connections
        ]
        
        # Don't retry the already failed host
        if redis_host in alternate_hosts:
            alternate_hosts.remove(redis_host)
            
        # Try alternate hosts
        for host in alternate_hosts:
            try:
                logger.info(f"Trying alternate Redis host: {host}")
                connection = redis.Redis(
                    host=host,
                    port=redis_port,
                    socket_timeout=2,  # Shorter timeout for retries
                    socket_connect_timeout=2,
                    retry_on_timeout=False
                )
                connection.ping()
                logger.info(f"Successfully connected to Redis at {host}:{redis_port}")
                
                # Update environment variable for future connections
                os.environ['REDIS_HOST'] = host
                return connection
            except Exception as alt_error:
                logger.debug(f"Failed to connect to alternate Redis host {host}: {alt_error}")
                
        logger.error("All Redis connection attempts failed")
        return None
    except Exception as e:
        logger.error(f"Unexpected error connecting to Redis: {e}")
        return None

def check_redis_connection():
    """
    Check if Redis is available
    
    Returns:
        bool: True if Redis is available, False otherwise
    """
    try:
        connection = get_redis_connection()
        return connection is not None and connection.ping()
    except Exception:
        return False