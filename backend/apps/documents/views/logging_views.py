"""
Logging Views for Documents App
Handles JavaScript error logging and analytics
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db.models import Count, Q
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..utils import doc_logger, DocumentLogger, create_audit_log

# Configure specific logger for client-side events
client_logger = logging.getLogger('apps.documents.client')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def log_client_event(request):
    """
    Endpoint for receiving JavaScript logs from the frontend
    """
    try:
        data = request.data
        event_type = data.get('type', 'unknown')
        event_data = data.get('data', {})
        timestamp = data.get('timestamp', timezone.now().isoformat())
        
        # Enrich with server-side context
        enriched_data = {
            **event_data,
            'user_id': request.user.id,
            'username': request.user.username,
            'session_key': request.session.session_key,
            'ip_address': get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'referer': request.META.get('HTTP_REFERER', ''),
            'server_timestamp': timezone.now().isoformat(),
            'client_timestamp': timestamp
        }
        
        # Route to appropriate handler based on event type
        if event_type == 'error':
            handle_client_error(enriched_data)
        elif event_type == 'performance':
            handle_performance_metric(enriched_data)
        elif event_type == 'user_action':
            handle_user_action(enriched_data)
        elif event_type == 'heartbeat':
            handle_heartbeat(enriched_data)
        else:
            # Generic logging for unknown types
            client_logger.info(f"Client event: {event_type}", extra=enriched_data)
        
        return Response({'status': 'logged'}, status=status.HTTP_200_OK)
        
    except Exception as e:
        doc_logger.log_error(e, context={'client_logging': True}, user=request.user)
        return Response(
            {'error': 'Failed to log event'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def handle_client_error(data: Dict[str, Any]):
    """Handle JavaScript errors from the client"""
    error_type = data.get('type', 'unknown_error')
    
    # Determine severity based on error type
    severity_map = {
        'javascript_error': logging.ERROR,
        'unhandled_promise_rejection': logging.ERROR,
        'api_request_error': logging.WARNING,
        'console_error': logging.WARNING,
        'user_reported_issue': logging.INFO
    }
    
    level = severity_map.get(error_type, logging.WARNING)
    
    client_logger.log(
        level,
        f"🚨 Client Error [{error_type}]: {data.get('message', 'No message')}",
        extra={
            'client_error': True,
            'error_type': error_type,
            'error_data': data,
            'user_id': data.get('user_id'),
            'session_id': data.get('sessionId'),
            'url': data.get('url'),
            'stack': data.get('stack'),
            'browser_info': {
                'user_agent': data.get('user_agent'),
                'viewport': data.get('viewport'),
                'memory': data.get('memory')
            }
        }
    )
    
    # Track error frequency for rate limiting
    user_id = data.get('user_id')
    if user_id:
        cache_key = f"client_errors:{user_id}:count"
        error_count = cache.get(cache_key, 0) + 1
        cache.set(cache_key, error_count, 3600)  # 1 hour window
        
        # Alert on excessive errors
        if error_count > 20:  # More than 20 errors per hour
            doc_logger.log_security_event(
                'excessive_client_errors',
                user={'id': user_id},
                severity='medium',
                error_count=error_count
            )


def handle_performance_metric(data: Dict[str, Any]):
    """Handle performance metrics from the client"""
    metric_type = data.get('type', 'unknown_metric')
    duration = data.get('duration', 0)
    
    # Log performance issues
    if duration > 5000:  # > 5 seconds
        level = logging.WARNING
        emoji = "🐌"
    elif duration > 2000:  # > 2 seconds
        level = logging.INFO
        emoji = "⏱️"
    else:
        level = logging.DEBUG
        emoji = "⚡"
    
    client_logger.log(
        level,
        f"{emoji} Client Performance [{metric_type}]: {duration}ms",
        extra={
            'client_performance': True,
            'metric_type': metric_type,
            'duration_ms': duration,
            'performance_data': data,
            'user_id': data.get('user_id'),
            'session_id': data.get('sessionId'),
            'url': data.get('url')
        }
    )
    
    # Store metrics for analytics (could be sent to monitoring service)
    store_performance_metric(data)


def handle_user_action(data: Dict[str, Any]):
    """Handle user action tracking from the client"""
    action_type = data.get('type', 'unknown_action')
    
    client_logger.debug(
        f"👤 Client Action [{action_type}]: {data.get('action', 'unknown')}",
        extra={
            'client_action': True,
            'action_type': action_type,
            'action_data': data,
            'user_id': data.get('user_id'),
            'session_id': data.get('sessionId'),
            'url': data.get('url')
        }
    )
    
    # Create audit log for important actions
    important_actions = ['api_request_start', 'form_submit', 'navigation']
    if action_type in important_actions:
        create_audit_log(
            user={'id': data.get('user_id')},
            action=f"client_{action_type}",
            resource_type='frontend',
            resource_id=data.get('url', ''),
            details=data,
            ip_address=data.get('ip_address')
        )


def handle_heartbeat(data: Dict[str, Any]):
    """Handle session heartbeat from the client"""
    session_id = data.get('sessionId')
    user_id = data.get('user_id')
    
    if session_id and user_id:
        # Update session activity
        cache_key = f"session_activity:{session_id}"
        cache.set(cache_key, {
            'user_id': user_id,
            'last_seen': timezone.now().isoformat(),
            'error_count': data.get('errorCount', 0),
            'performance_metrics': data.get('performanceMetrics', 0)
        }, 300)  # 5 minutes
        
        client_logger.debug(
            f"💗 Session heartbeat from user {user_id}",
            extra={
                'heartbeat': True,
                'session_id': session_id,
                'user_id': user_id,
                'error_count': data.get('errorCount', 0)
            }
        )


def store_performance_metric(data: Dict[str, Any]):
    """Store performance metrics for analytics"""
    # In a real implementation, you might send this to a metrics service
    # like Prometheus, DataDog, or store in a time-series database
    
    metric_type = data.get('type')
    cache_key = f"performance_metrics:{metric_type}"
    
    # Get existing metrics
    metrics = cache.get(cache_key, [])
    
    # Add new metric
    metrics.append({
        'timestamp': data.get('server_timestamp'),
        'duration': data.get('duration'),
        'user_id': data.get('user_id'),
        'url': data.get('url')
    })
    
    # Keep only last 100 metrics per type
    if len(metrics) > 100:
        metrics = metrics[-100:]
    
    # Store back in cache
    cache.set(cache_key, metrics, 3600)  # 1 hour


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_client_metrics(request):
    """
    Get aggregated client-side metrics for monitoring dashboard
    """
    try:
        # Only allow staff users to access metrics
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        time_range = request.GET.get('range', '1h')  # 1h, 24h, 7d
        
        # Calculate time window
        now = timezone.now()
        if time_range == '1h':
            start_time = now - timedelta(hours=1)
        elif time_range == '24h':
            start_time = now - timedelta(hours=24)
        elif time_range == '7d':
            start_time = now - timedelta(days=7)
        else:
            start_time = now - timedelta(hours=1)
        
        # Get metrics from cache
        metrics = get_aggregated_metrics(start_time)
        
        return Response(metrics, status=status.HTTP_200_OK)
        
    except Exception as e:
        doc_logger.log_error(e, user=request.user)
        return Response(
            {'error': 'Failed to get metrics'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def get_aggregated_metrics(start_time):
    """Get aggregated metrics from cache and logs"""
    metrics = {
        'errors': {
            'total': 0,
            'by_type': {},
            'recent': []
        },
        'performance': {
            'avg_load_time': 0,
            'slow_requests': 0,
            'by_endpoint': {}
        },
        'user_activity': {
            'active_sessions': 0,
            'total_actions': 0,
            'top_pages': {}
        }
    }
    
    # Get error metrics
    error_types = ['javascript_error', 'api_request_error', 'console_error']
    for error_type in error_types:
        cache_key = f"client_errors:{error_type}:count"
        count = cache.get(cache_key, 0)
        metrics['errors']['by_type'][error_type] = count
        metrics['errors']['total'] += count
    
    # Get performance metrics
    perf_cache_key = "performance_metrics:page_load"
    perf_data = cache.get(perf_cache_key, [])
    
    if perf_data:
        recent_data = [m for m in perf_data 
                      if datetime.fromisoformat(m['timestamp'].replace('Z', '+00:00')) > start_time]
        
        if recent_data:
            avg_duration = sum(m['duration'] for m in recent_data) / len(recent_data)
            metrics['performance']['avg_load_time'] = round(avg_duration, 2)
            metrics['performance']['slow_requests'] = len([
                m for m in recent_data if m['duration'] > 3000
            ])
    
    # Get active sessions
    session_pattern = "session_activity:*"
    # Note: In production, use Redis KEYS pattern matching carefully
    active_sessions = 0  # Placeholder - implement based on your cache backend
    metrics['user_activity']['active_sessions'] = active_sessions
    
    return metrics


def get_client_ip(request):
    """Extract client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def report_bug(request):
    """
    Endpoint for users to report bugs with additional context
    """
    try:
        description = request.data.get('description', '').strip()
        category = request.data.get('category', 'general')
        steps_to_reproduce = request.data.get('steps', '')
        expected_behavior = request.data.get('expected', '')
        actual_behavior = request.data.get('actual', '')
        
        if not description:
            return Response(
                {'error': 'Description is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Log the bug report
        doc_logger.log_user_action(
            user=request.user,
            action='report_bug',
            resource_type='bug_report',
            description=description,
            category=category,
            steps_to_reproduce=steps_to_reproduce,
            expected_behavior=expected_behavior,
            actual_behavior=actual_behavior,
            url=request.data.get('url', ''),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            timestamp=timezone.now().isoformat()
        )
        
        return Response({
            'message': 'Bug report submitted successfully',
            'ticket_id': f"BUG-{timezone.now().strftime('%Y%m%d')}-{request.user.id}"
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        doc_logger.log_error(e, user=request.user)
        return Response(
            {'error': 'Failed to submit bug report'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def system_health(request):
    """
    Basic system health check endpoint
    """
    try:
        health_data = {
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'services': {
                'database': check_database_health(),
                'cache': check_cache_health(),
                'logging': check_logging_health()
            },
            'metrics': {
                'active_users': get_active_user_count(),
                'error_rate': get_recent_error_rate()
            }
        }
        
        # Overall health status
        all_services_healthy = all(
            service['status'] == 'healthy' 
            for service in health_data['services'].values()
        )
        
        if not all_services_healthy:
            health_data['status'] = 'degraded'
        
        status_code = status.HTTP_200_OK if all_services_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
        
        return Response(health_data, status=status_code)
        
    except Exception as e:
        doc_logger.log_error(e)
        return Response({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


def check_database_health():
    """Check database connectivity"""
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return {'status': 'healthy', 'latency_ms': 0}  # Could measure actual latency
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}


def check_cache_health():
    """Check cache connectivity"""
    try:
        test_key = 'health_check'
        cache.set(test_key, 'ok', 1)
        result = cache.get(test_key)
        cache.delete(test_key)
        
        if result == 'ok':
            return {'status': 'healthy'}
        else:
            return {'status': 'unhealthy', 'error': 'Cache read/write failed'}
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}


def check_logging_health():
    """Check logging system"""
    try:
        doc_logger.logger.debug("Health check log message")
        return {'status': 'healthy'}
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}


def get_active_user_count():
    """Get count of active users (last 5 minutes)"""
    try:
        # This is a simplified implementation
        # In production, you might track this differently
        return cache.get('active_user_count', 0)
    except:
        return 0


def get_recent_error_rate():
    """Get recent error rate"""
    try:
        error_count = cache.get('recent_error_count', 0)
        request_count = cache.get('recent_request_count', 1)
        return round((error_count / request_count) * 100, 2)
    except:
        return 0.0