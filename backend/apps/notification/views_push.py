# backend/apps/notification/views_push.py
import json
import logging
from typing import Dict, Any, Optional

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .models.notification_models import NotificationDevice

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_push_subscription(request: Request) -> Response:
    """
    Register a push notification subscription for the current user
    
    Expected payload:
    {
        "subscription_json": "...",  # JSON string of the push subscription
        "device_type": "web",
        "device_name": "Chrome on Windows"  # Optional
    }
    """
    try:
        # Extract subscription data
        subscription_json = request.data.get('subscription_json')
        device_type = request.data.get('device_type', 'web')
        device_name = request.data.get('device_name')
        
        # Validate required fields
        if not subscription_json:
            return Response({'error': 'subscription_json is required'}, status=400)
            
        # Parse subscription JSON to validate it
        try:
            subscription_data = json.loads(subscription_json)
            if not subscription_data.get('endpoint'):
                return Response({'error': 'Invalid subscription format, missing endpoint'}, status=400)
        except json.JSONDecodeError:
            return Response({'error': 'Invalid JSON in subscription_json'}, status=400)
            
        # Get the endpoint to use as unique identifier
        endpoint = subscription_data.get('endpoint')
        
        # Check if this subscription already exists
        existing_device = NotificationDevice.objects.filter(
            device_token=subscription_json
        ).first()
        
        if existing_device:
            # If it exists but belongs to a different user, update the user
            if existing_device.user != request.user:
                existing_device.user = request.user
                
            # Update device details and mark as active
            existing_device.device_type = device_type
            if device_name:
                existing_device.device_name = device_name
            existing_device.is_active = True
            existing_device.save()
            
            return Response({
                'success': True,
                'message': 'Subscription updated successfully',
                'device_id': existing_device.id
            })
        else:
            # Create a new device record
            device = NotificationDevice.objects.create(
                user=request.user,
                device_token=subscription_json,
                device_type=device_type,
                device_name=device_name
            )
            
            return Response({
                'success': True,
                'message': 'Subscription registered successfully',
                'device_id': device.id
            })
    except Exception as e:
        logger.error(f"Error registering push subscription: {str(e)}")
        return Response({'error': 'Internal server error'}, status=500)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def unregister_push_subscription(request: Request) -> Response:
    """
    Unregister a push notification subscription
    
    Expected payload:
    {
        "endpoint": "..."  # The subscription endpoint to unregister
    }
    """
    try:
        # Extract subscription endpoint
        endpoint = request.data.get('endpoint')
        
        # Validate required field
        if not endpoint:
            return Response({'error': 'endpoint is required'}, status=400)
            
        # Find devices with this endpoint in their device_token
        devices = NotificationDevice.objects.filter(
            user=request.user,
            device_token__contains=endpoint
        )
        
        if not devices.exists():
            return Response({'error': 'Subscription not found'}, status=404)
            
        # Deactivate matching devices
        count = devices.update(is_active=False)
        
        return Response({
            'success': True,
            'message': f'Unregistered {count} subscription(s)'
        })
    except Exception as e:
        logger.error(f"Error unregistering push subscription: {str(e)}")
        return Response({'error': 'Internal server error'}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_push_subscriptions(request: Request) -> Response:
    """
    Get all active push notification subscriptions for the current user
    """
    try:
        # Get all active devices for this user
        devices = NotificationDevice.objects.filter(
            user=request.user,
            is_active=True
        )
        
        # Format response
        result = []
        for device in devices:
            try:
                # Try to extract endpoint from subscription JSON
                subscription_data = json.loads(device.device_token)
                endpoint = subscription_data.get('endpoint', 'Unknown endpoint')
                
                # Add device info
                result.append({
                    'id': device.id,
                    'device_type': device.device_type,
                    'device_name': device.device_name or 'Unknown device',
                    'endpoint': endpoint,
                    'created_at': device.created_at.isoformat(),
                    'last_used': device.last_used.isoformat() if device.last_used else None
                })
            except (json.JSONDecodeError, KeyError):
                # Skip invalid subscription data
                continue
        
        return Response({
            'success': True,
            'count': len(result),
            'subscriptions': result
        })
    except Exception as e:
        logger.error(f"Error getting push subscriptions: {str(e)}")
        return Response({'error': 'Internal server error'}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_test_notification(request: Request) -> Response:
    """
    Send a test notification to the user's push subscriptions
    """
    try:
        from .services import NotificationDeliveryService
        from .models.notification_models import NotificationType, NotificationPriority
        
        # Create and deliver a test notification
        notification = NotificationDeliveryService.create_and_deliver(
            user=request.user,
            title="Test Notification",
            message="This is a test notification from Linguify",
            notification_type=NotificationType.SYSTEM,
            priority=NotificationPriority.MEDIUM,
            data={
                "test": True,
                "timestamp": request.data.get('timestamp', None)
            },
            delivery_channels=['websocket', 'push']
        )
        
        if notification:
            return Response({
                'success': True,
                'message': 'Test notification sent',
                'notification_id': str(notification.id)
            })
        else:
            return Response({
                'success': False,
                'message': 'Failed to send test notification, you may have notifications disabled'
            }, status=400)
    except Exception as e:
        logger.error(f"Error sending test notification: {str(e)}")
        return Response({'error': 'Internal server error'}, status=500)