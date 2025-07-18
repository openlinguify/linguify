"""
Documents App Utilities
Enhanced with comprehensive logging and error handling
"""

import logging
import json
import traceback
import functools
from datetime import datetime
from typing import Any, Dict, Optional, Union, Callable
from django.conf import settings
from django.core.exceptions import ValidationError, PermissionDenied
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response

User = get_user_model()

# Configure logger for documents app
logger = logging.getLogger('apps.documents')


class DocumentsError(Exception):
    """Base exception for documents app"""
    def __init__(self, message: str, error_code: str = None, details: Dict = None):
        self.message = message
        self.error_code = error_code or 'DOCUMENTS_ERROR'
        self.details = details or {}
        super().__init__(self.message)


class DocumentPermissionError(DocumentsError):
    """Raised when user lacks permission for document operation"""
    def __init__(self, message: str = "Permission denied", user=None, document=None):
        self.user = user
        self.document = document
        super().__init__(
            message=message,
            error_code='PERMISSION_DENIED',
            details={
                'user_id': getattr(user, 'id', None),
                'document_id': getattr(document, 'id', None)
            }
        )


class DocumentNotFoundError(DocumentsError):
    """Raised when document is not found"""
    def __init__(self, document_id: Union[int, str]):
        super().__init__(
            message=f"Document with ID {document_id} not found",
            error_code='DOCUMENT_NOT_FOUND',
            details={'document_id': document_id}
        )


class DocumentValidationError(DocumentsError):
    """Raised when document validation fails"""
    def __init__(self, message: str, field: str = None, value: Any = None):
        super().__init__(
            message=message,
            error_code='VALIDATION_ERROR',
            details={'field': field, 'value': str(value) if value else None}
        )


class DocumentLogger:
    """Enhanced logging utility for documents operations"""
    
    def __init__(self, module_name: str = None):
        self.logger = logging.getLogger(module_name or 'apps.documents')
        self.start_time = None
    
    def start_operation(self, operation_name: str, **context):
        """Start logging an operation"""
        self.start_time = timezone.now()
        self.logger.info(
            f"🚀 Starting operation: {operation_name}",
            extra={
                'operation': operation_name,
                'start_time': self.start_time.isoformat(),
                **context
            }
        )
    
    def end_operation(self, operation_name: str, success: bool = True, **context):
        """End logging an operation"""
        end_time = timezone.now()
        duration = (end_time - self.start_time).total_seconds() if self.start_time else 0
        
        status_emoji = "✅" if success else "❌"
        level = logging.INFO if success else logging.ERROR
        
        self.logger.log(
            level,
            f"{status_emoji} Operation {operation_name} {'completed' if success else 'failed'} in {duration:.2f}s",
            extra={
                'operation': operation_name,
                'success': success,
                'duration_seconds': duration,
                'end_time': end_time.isoformat(),
                **context
            }
        )
    
    def log_user_action(self, user, action: str, resource_type: str, resource_id: Union[int, str] = None, **details):
        """Log user actions for audit trail"""
        self.logger.info(
            f"👤 User {user.username} performed {action} on {resource_type}",
            extra={
                'user_id': user.id,
                'username': user.username,
                'action': action,
                'resource_type': resource_type,
                'resource_id': resource_id,
                'timestamp': timezone.now().isoformat(),
                'details': details
            }
        )
    
    def log_permission_check(self, user, resource, permission: str, granted: bool, reason: str = None):
        """Log permission checks"""
        level = logging.DEBUG if granted else logging.WARNING
        status = "✓ GRANTED" if granted else "✗ DENIED"
        
        self.logger.log(
            level,
            f"🔐 Permission {permission} {status} for user {user.username} on {type(resource).__name__}",
            extra={
                'user_id': user.id,
                'username': user.username,
                'permission': permission,
                'granted': granted,
                'reason': reason,
                'resource_type': type(resource).__name__,
                'resource_id': getattr(resource, 'id', None)
            }
        )
    
    def log_error(self, error: Exception, context: Dict = None, user=None):
        """Log errors with full context"""
        context = context or {}
        
        error_info = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'context': context,
            'timestamp': timezone.now().isoformat()
        }
        
        if user:
            error_info.update({
                'user_id': user.id,
                'username': user.username
            })
        
        if isinstance(error, DocumentsError):
            error_info.update({
                'error_code': error.error_code,
                'error_details': error.details
            })
        
        self.logger.error(
            f"💥 Error occurred: {error}",
            extra=error_info
        )
    
    def log_performance(self, operation: str, duration: float, **metrics):
        """Log performance metrics"""
        if duration > 5.0:  # Log slow operations
            level = logging.WARNING
            emoji = "🐌"
        elif duration > 1.0:
            level = logging.INFO
            emoji = "⏱️"
        else:
            level = logging.DEBUG
            emoji = "⚡"
        
        self.logger.log(
            level,
            f"{emoji} Performance: {operation} took {duration:.2f}s",
            extra={
                'operation': operation,
                'duration_seconds': duration,
                'performance_metrics': metrics
            }
        )
    
    def log_security_event(self, event_type: str, user, severity: str = 'info', **details):
        """Log security-related events"""
        severity_map = {
            'critical': logging.CRITICAL,
            'high': logging.ERROR,
            'medium': logging.WARNING,
            'low': logging.INFO,
            'info': logging.INFO
        }
        
        level = severity_map.get(severity, logging.INFO)
        
        self.logger.log(
            level,
            f"🛡️ Security event: {event_type}",
            extra={
                'event_type': event_type,
                'severity': severity,
                'user_id': getattr(user, 'id', None),
                'username': getattr(user, 'username', 'anonymous'),
                'timestamp': timezone.now().isoformat(),
                'details': details
            }
        )


# Global logger instance
doc_logger = DocumentLogger()


def log_operation(operation_name: str):
    """Decorator to log function operations"""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = DocumentLogger(func.__module__)
            logger.start_operation(
                operation_name,
                function=func.__name__,
                args_count=len(args),
                kwargs_keys=list(kwargs.keys())
            )
            
            try:
                result = func(*args, **kwargs)
                logger.end_operation(operation_name, success=True)
                return result
            except Exception as e:
                logger.end_operation(operation_name, success=False)
                logger.log_error(e, context={'function': func.__name__})
                raise
        
        return wrapper
    return decorator


def log_user_action(action: str, resource_type: str):
    """Decorator to log user actions"""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(self, request, *args, **kwargs):
            try:
                result = func(self, request, *args, **kwargs)
                
                # Extract resource ID from result or kwargs
                resource_id = None
                if hasattr(result, 'data') and isinstance(result.data, dict):
                    resource_id = result.data.get('id')
                elif 'pk' in kwargs:
                    resource_id = kwargs['pk']
                
                doc_logger.log_user_action(
                    user=request.user,
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    method=request.method,
                    path=request.path
                )
                
                return result
            except Exception as e:
                doc_logger.log_error(e, user=request.user)
                raise
        
        return wrapper
    return decorator


def handle_api_errors(func: Callable):
    """Decorator to handle API errors consistently"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DocumentPermissionError as e:
            doc_logger.log_security_event(
                'permission_denied',
                user=e.user,
                severity='medium',
                document_id=e.details.get('document_id')
            )
            return Response({
                'error': 'Permission denied',
                'code': e.error_code,
                'message': e.message,
                'details': e.details
            }, status=status.HTTP_403_FORBIDDEN)
        
        except DocumentNotFoundError as e:
            return Response({
                'error': 'Not found',
                'code': e.error_code,
                'message': e.message,
                'details': e.details
            }, status=status.HTTP_404_NOT_FOUND)
        
        except DocumentValidationError as e:
            return Response({
                'error': 'Validation error',
                'code': e.error_code,
                'message': e.message,
                'details': e.details
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except ValidationError as e:
            doc_logger.log_error(e)
            return Response({
                'error': 'Validation error',
                'code': 'DJANGO_VALIDATION_ERROR',
                'message': str(e),
                'details': e.message_dict if hasattr(e, 'message_dict') else {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except PermissionDenied as e:
            doc_logger.log_security_event(
                'django_permission_denied',
                user=getattr(args[0], 'user', None) if args else None,
                severity='medium'
            )
            return Response({
                'error': 'Permission denied',
                'code': 'DJANGO_PERMISSION_DENIED',
                'message': str(e)
            }, status=status.HTTP_403_FORBIDDEN)
        
        except Exception as e:
            doc_logger.log_error(e)
            
            # Don't expose internal errors in production
            if settings.DEBUG:
                return Response({
                    'error': 'Internal server error',
                    'code': 'INTERNAL_ERROR',
                    'message': str(e),
                    'traceback': traceback.format_exc()
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({
                    'error': 'Internal server error',
                    'code': 'INTERNAL_ERROR',
                    'message': 'An unexpected error occurred. Please try again later.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return wrapper


class PerformanceMonitor:
    """Monitor and log performance metrics"""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        self.metrics = {}
    
    def __enter__(self):
        self.start_time = timezone.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (timezone.now() - self.start_time).total_seconds()
        doc_logger.log_performance(self.operation_name, duration, **self.metrics)
    
    def add_metric(self, key: str, value: Any):
        """Add a performance metric"""
        self.metrics[key] = value
    
    def track_query_count(self, queryset):
        """Track database query count"""
        from django.db import connection
        initial_queries = len(connection.queries)
        result = list(queryset)
        query_count = len(connection.queries) - initial_queries
        self.add_metric('db_queries', query_count)
        self.add_metric('result_count', len(result))
        return result


def validate_document_permission(user, document, permission_level: str = 'view'):
    """
    Validate if user has permission for document operation
    
    Args:
        user: User instance
        document: Document instance
        permission_level: 'view', 'edit', or 'admin'
    
    Raises:
        DocumentPermissionError: If permission is denied
    """
    doc_logger.log_permission_check(user, document, permission_level, False)
    
    # Document owner has all permissions
    if document.owner == user:
        doc_logger.log_permission_check(user, document, permission_level, True, "owner")
        return True
    
    # Check shared permissions
    if hasattr(document, 'shares'):
        share = document.shares.filter(user=user).first()
        if share:
            if share.is_expired():
                doc_logger.log_permission_check(
                    user, document, permission_level, False, "share_expired"
                )
                raise DocumentPermissionError(
                    "Your access to this document has expired",
                    user=user,
                    document=document
                )
            
            # Permission hierarchy: admin > edit > view
            permission_hierarchy = {'view': 0, 'edit': 1, 'admin': 2}
            required_level = permission_hierarchy.get(permission_level, 0)
            user_level = permission_hierarchy.get(share.permission_level, 0)
            
            if user_level >= required_level:
                doc_logger.log_permission_check(
                    user, document, permission_level, True, f"share_{share.permission_level}"
                )
                return True
    
    # Check public documents for view permission
    if permission_level == 'view' and document.visibility == 'public':
        doc_logger.log_permission_check(user, document, permission_level, True, "public")
        return True
    
    doc_logger.log_permission_check(user, document, permission_level, False, "no_permission")
    raise DocumentPermissionError(
        f"You don't have {permission_level} permission for this document",
        user=user,
        document=document
    )


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    import re
    
    # Remove any non-alphanumeric characters except dots, hyphens, and underscores
    sanitized = re.sub(r'[^\w\.-]', '_', filename)
    
    # Remove multiple consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Remove leading/trailing underscores and dots
    sanitized = sanitized.strip('_.')
    
    # Ensure filename is not empty and not too long
    if not sanitized:
        sanitized = 'untitled'
    
    if len(sanitized) > 100:
        name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
        sanitized = name[:95] + ('.' + ext if ext else '')
    
    doc_logger.logger.debug(f"Sanitized filename: {filename} -> {sanitized}")
    return sanitized


def track_document_activity(document, user, activity_type: str, details: Dict = None):
    """Track document activity for analytics"""
    activity_data = {
        'document_id': document.id,
        'document_title': document.title,
        'user_id': user.id,
        'username': user.username,
        'activity_type': activity_type,
        'timestamp': timezone.now().isoformat(),
        'details': details or {}
    }
    
    doc_logger.logger.info(
        f"📊 Document activity: {activity_type}",
        extra={
            'activity_tracking': True,
            **activity_data
        }
    )
    
    # You could also store this in a separate analytics table
    # DocumentActivity.objects.create(**activity_data)


def create_audit_log(user, action: str, resource_type: str, resource_id: Union[int, str], 
                    details: Dict = None, ip_address: str = None):
    """Create audit log entry"""
    audit_data = {
        'user_id': user.id if user else None,
        'username': user.username if user else 'anonymous',
        'action': action,
        'resource_type': resource_type,
        'resource_id': str(resource_id),
        'details': details or {},
        'ip_address': ip_address,
        'timestamp': timezone.now().isoformat()
    }
    
    doc_logger.logger.info(
        f"📋 Audit log: {action} on {resource_type}",
        extra={
            'audit_log': True,
            **audit_data
        }
    )


def export_error_report(start_date: datetime = None, end_date: datetime = None) -> Dict:
    """Export error report for analysis"""
    # This would typically query your logging database or files
    # For now, we'll return a placeholder structure
    
    report = {
        'period': {
            'start': start_date.isoformat() if start_date else None,
            'end': end_date.isoformat() if end_date else None
        },
        'summary': {
            'total_errors': 0,
            'critical_errors': 0,
            'permission_errors': 0,
            'validation_errors': 0
        },
        'top_errors': [],
        'error_trends': [],
        'affected_users': [],
        'generated_at': timezone.now().isoformat()
    }
    
    doc_logger.logger.info("📊 Error report generated", extra={'report_summary': report['summary']})
    return report


# Middleware for request logging
class DocumentsLoggingMiddleware:
    """Middleware to log all requests to documents app"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.path.startswith('/documents/'):
            start_time = timezone.now()
            
            # Log request
            doc_logger.logger.debug(
                f"📥 Request: {request.method} {request.path}",
                extra={
                    'request_id': getattr(request, 'id', None),
                    'method': request.method,
                    'path': request.path,
                    'user_id': getattr(request.user, 'id', None) if hasattr(request, 'user') else None,
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    'ip_address': request.META.get('REMOTE_ADDR', ''),
                    'timestamp': start_time.isoformat()
                }
            )
            
            response = self.get_response(request)
            
            # Log response
            duration = (timezone.now() - start_time).total_seconds()
            doc_logger.logger.debug(
                f"📤 Response: {response.status_code} in {duration:.2f}s",
                extra={
                    'request_id': getattr(request, 'id', None),
                    'status_code': response.status_code,
                    'duration_seconds': duration,
                    'response_size': len(response.content) if hasattr(response, 'content') else 0
                }
            )
            
            return response
        
        return self.get_response(request)