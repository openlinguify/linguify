"""
Views for calendar provider management
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
import logging

from ..models import CalendarProvider, CalendarProviderSync
from ..services.provider_service import ProviderService
from ..services.sync_service import SyncService, SyncScheduler

logger = logging.getLogger(__name__)


@login_required
def providers(request):
    """
    Calendar providers management page
    """
    return render(request, 'calendar/providers.html', {
        'page_title': 'Calendar Providers'
    })


class CalendarProviderViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Calendar Providers
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CalendarProvider.objects.filter(user=self.request.user).order_by('name')
    
    def get_serializer_class(self):
        from rest_framework import serializers
        
        class CalendarProviderSerializer(serializers.ModelSerializer):
            provider_type_display = serializers.CharField(source='get_provider_type_display', read_only=True)
            sync_direction_display = serializers.CharField(source='get_sync_direction_display', read_only=True)
            sync_frequency_display = serializers.CharField(source='get_sync_frequency_display', read_only=True)
            status_display = serializers.CharField(source='get_status_display', read_only=True)
            
            # Write-only fields for sensitive data
            client_secret = serializers.CharField(write_only=True, required=False)
            password = serializers.CharField(write_only=True, required=False)
            
            class Meta:
                model = CalendarProvider
                fields = [
                    'id', 'name', 'provider_type', 'provider_type_display',
                    'sync_direction', 'sync_direction_display',
                    'sync_frequency', 'sync_frequency_display',
                    'auto_sync_enabled', 'active', 'connection_verified',
                    'last_sync_at', 'last_sync_status', 'last_sync_error',
                    'sync_count', 'status_display', 'created_at', 'updated_at',
                    # Configuration fields
                    'client_id', 'server_url', 'username', 'external_calendar_id',
                    'external_calendar_name', 'sync_past_days', 'sync_future_days',
                    'sync_only_busy', 'exclude_all_day_events',
                    # Write-only fields
                    'client_secret', 'password'
                ]
                read_only_fields = [
                    'connection_verified', 'last_sync_at', 'last_sync_status', 
                    'last_sync_error', 'sync_count', 'created_at', 'updated_at'
                ]
        
        return CalendarProviderSerializer
    
    def perform_create(self, serializer):
        """Create provider with current user and handle credentials"""
        # Extract sensitive data
        client_secret = serializer.validated_data.pop('client_secret', '')
        password = serializer.validated_data.pop('password', '')
        
        # Create provider
        provider = serializer.save(user=self.request.user)
        
        # Store credentials securely
        credentials = {}
        if client_secret:
            credentials['client_secret'] = client_secret
        if password:
            credentials['password'] = password
            
        if credentials:
            provider.credentials = credentials
            provider.save()
    
    def perform_update(self, serializer):
        """Update provider and handle credentials"""
        # Extract sensitive data
        client_secret = serializer.validated_data.pop('client_secret', None)
        password = serializer.validated_data.pop('password', None)
        
        # Update provider
        provider = serializer.save()
        
        # Update credentials if provided
        credentials = provider.credentials
        if client_secret is not None:
            credentials['client_secret'] = client_secret
        if password is not None:
            credentials['password'] = password
            
        provider.credentials = credentials
        provider.save()
    
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """
        Test connection to provider
        """
        provider = self.get_object()
        
        try:
            result = provider.test_connection()
            return Response({
                'success': result['success'],
                'message': result.get('message', ''),
                'error': result.get('error', '')
            })
        except Exception as e:
            logger.error(f"Error testing provider {provider.name}: {str(e)}")
            return Response({
                'success': False,
                'error': f'Test failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """
        Trigger immediate synchronization
        """
        provider = self.get_object()
        
        try:
            result = provider.sync_now(force=request.data.get('force', False))
            return Response({
                'success': result['success'],
                'message': result.get('message', 'Sync completed'),
                'error': result.get('error', ''),
                'details': result.get('details', {})
            })
        except Exception as e:
            logger.error(f"Error syncing provider {provider.name}: {str(e)}")
            return Response({
                'success': False,
                'error': f'Sync failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def calendars(self, request, pk=None):
        """
        Get list of available calendars from provider
        """
        provider = self.get_object()
        
        try:
            service = ProviderService.get_service(provider)
            calendars = service.get_calendars()
            
            return Response({
                'success': True,
                'calendars': calendars
            })
        except Exception as e:
            logger.error(f"Error getting calendars for provider {provider.name}: {str(e)}")
            return Response({
                'success': False,
                'error': f'Failed to get calendars: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def select_calendar(self, request, pk=None):
        """
        Select specific calendar for synchronization
        """
        provider = self.get_object()
        calendar_id = request.data.get('calendar_id')
        calendar_name = request.data.get('calendar_name', '')
        
        if not calendar_id:
            return Response({
                'success': False,
                'error': 'Calendar ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            provider.external_calendar_id = calendar_id
            provider.external_calendar_name = calendar_name
            provider.save(update_fields=['external_calendar_id', 'external_calendar_name'])
            
            return Response({
                'success': True,
                'message': f'Selected calendar: {calendar_name or calendar_id}'
            })
        except Exception as e:
            logger.error(f"Error selecting calendar for provider {provider.name}: {str(e)}")
            return Response({
                'success': False,
                'error': f'Failed to select calendar: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def sync_all(self, request):
        """
        Sync all active providers for current user
        """
        try:
            user_providers = self.get_queryset().filter(
                active=True,
                connection_verified=True
            )
            
            results = {
                'total_providers': user_providers.count(),
                'successful_syncs': 0,
                'failed_syncs': 0,
                'sync_results': {}
            }
            
            for provider in user_providers:
                try:
                    sync_result = provider.sync_now()
                    
                    if sync_result['success']:
                        results['successful_syncs'] += 1
                    else:
                        results['failed_syncs'] += 1
                    
                    results['sync_results'][provider.name] = sync_result
                    
                except Exception as e:
                    results['failed_syncs'] += 1
                    results['sync_results'][provider.name] = {
                        'success': False,
                        'error': str(e)
                    }
            
            return Response({
                'success': True,
                'message': f'Sync completed for {user_providers.count()} providers',
                **results
            })
            
        except Exception as e:
            logger.error(f"Error syncing all providers for user {request.user.username}: {str(e)}")
            return Response({
                'success': False,
                'error': f'Failed to sync providers: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def supported_types(self, request):
        """
        Get list of supported provider types
        """
        return Response({
            'success': True,
            'provider_types': CalendarProvider.get_supported_providers()
        })
    
    @action(detail=True, methods=['post'])
    def enable(self, request, pk=None):
        """
        Enable provider
        """
        provider = self.get_object()
        provider.enable()
        
        return Response({
            'success': True,
            'message': f'Provider {provider.name} enabled'
        })
    
    @action(detail=True, methods=['post'])
    def disable(self, request, pk=None):
        """
        Disable provider
        """
        provider = self.get_object()
        reason = request.data.get('reason', 'Disabled by user')
        provider.disable(reason)
        
        return Response({
            'success': True,
            'message': f'Provider {provider.name} disabled'
        })


class CalendarProviderSyncViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet for Calendar Provider Sync History (read-only)
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only show sync history for user's providers
        user_providers = CalendarProvider.objects.filter(user=self.request.user)
        return CalendarProviderSync.objects.filter(
            provider__in=user_providers
        ).order_by('-started_at')
    
    def get_serializer_class(self):
        from rest_framework import serializers
        
        class CalendarProviderSyncSerializer(serializers.ModelSerializer):
            provider_name = serializers.CharField(source='provider.name', read_only=True)
            sync_type_display = serializers.CharField(source='get_sync_type_display', read_only=True)
            duration_display = serializers.SerializerMethodField()
            
            class Meta:
                model = CalendarProviderSync
                fields = [
                    'id', 'provider_name', 'sync_type', 'sync_type_display',
                    'started_at', 'completed_at', 'duration_seconds', 'duration_display',
                    'success', 'error_message', 'events_imported', 'events_exported',
                    'events_updated', 'events_deleted', 'events_skipped', 'sync_details'
                ]
            
            def get_duration_display(self, obj):
                if obj.duration_seconds:
                    if obj.duration_seconds < 60:
                        return f"{obj.duration_seconds:.1f}s"
                    else:
                        minutes = obj.duration_seconds // 60
                        seconds = obj.duration_seconds % 60
                        return f"{int(minutes)}m {int(seconds)}s"
                return "N/A"
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get sync statistics for user's providers
        """
        queryset = self.get_queryset()
        
        # Recent stats (last 30 days)
        from datetime import timedelta
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_syncs = queryset.filter(started_at__gte=thirty_days_ago)
        
        stats = {
            'total_syncs': queryset.count(),
            'recent_syncs': recent_syncs.count(),
            'successful_syncs': queryset.filter(success=True).count(),
            'failed_syncs': queryset.filter(success=False).count(),
            'recent_successful': recent_syncs.filter(success=True).count(),
            'recent_failed': recent_syncs.filter(success=False).count(),
            'total_events_imported': sum(sync.events_imported for sync in queryset),
            'total_events_exported': sum(sync.events_exported for sync in queryset),
            'total_events_updated': sum(sync.events_updated for sync in queryset),
        }
        
        # Success rate
        if stats['total_syncs'] > 0:
            stats['success_rate'] = round((stats['successful_syncs'] / stats['total_syncs']) * 100, 1)
        else:
            stats['success_rate'] = 0
        
        return Response({
            'success': True,
            'stats': stats
        })