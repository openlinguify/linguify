"""
Views for email template management
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import json

from ..models import CalendarEmailTemplate, CalendarEmailLog, CalendarEvent, CalendarAttendee
from ..services.email_service import CalendarEmailService, EmailTemplateManager
from django.contrib.auth import get_user_model

User = get_user_model()


@login_required
def email_templates(request):
    """
    Email templates management page
    """
    return render(request, 'calendar/email_templates.html', {
        'page_title': 'Email Templates'
    })


class CalendarEmailTemplateViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Calendar Email Templates
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CalendarEmailTemplate.objects.filter(active=True).order_by('template_type', 'language')
    
    def get_serializer_class(self):
        # Simple serializer for API responses
        from rest_framework import serializers
        
        class CalendarEmailTemplateSerializer(serializers.ModelSerializer):
            created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
            template_type_display = serializers.CharField(source='get_template_type_display', read_only=True)
            language_display = serializers.CharField(source='get_language_display', read_only=True)
            
            class Meta:
                model = CalendarEmailTemplate
                fields = [
                    'id', 'name', 'template_type', 'template_type_display',
                    'language', 'language_display', 'subject_template', 
                    'body_html_template', 'body_text_template', 'active', 
                    'is_default', 'created_by_name', 'created_at', 'updated_at'
                ]
                read_only_fields = ['created_at', 'updated_at']
        
        return CalendarEmailTemplateSerializer
    
    def perform_create(self, serializer):
        """Set current user as creator"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        """
        Preview template with sample data
        """
        template = self.get_object()
        
        try:
            preview = EmailTemplateManager.preview_template(template)
            return Response({
                'success': True,
                'subject': preview['subject'],
                'body_html': preview['body_html'],
                'body_text': preview['body_text']
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def send_test(self, request):
        """
        Send test email using template
        """
        data = request.data
        template_id = data.get('template_id')
        recipient_email = data.get('recipient_email')
        recipient_name = data.get('recipient_name', '')
        
        if not template_id or not recipient_email:
            return Response({
                'success': False,
                'error': 'Template ID and recipient email are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            template = CalendarEmailTemplate.objects.get(id=template_id, active=True)
        except CalendarEmailTemplate.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Template not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            # Create sample event and attendee for testing
            sample_event = self._create_sample_event(request.user)
            sample_attendee = self._create_sample_attendee(sample_event, recipient_email, recipient_name)
            
            # Send test email
            email_service = CalendarEmailService()
            
            if template.template_type == 'invitation':
                success = email_service.send_invitation(sample_event, sample_attendee, 'en', 'This is a test email.')
            elif template.template_type == 'reminder':
                from datetime import timedelta
                success = email_service.send_reminder(sample_event, sample_attendee, timedelta(hours=1), 'en')
            elif template.template_type == 'update':
                success = email_service.send_update_notification(sample_event, [sample_attendee], ['This is a test update'], 'en')
            elif template.template_type == 'cancellation':
                success = email_service.send_cancellation_notification(sample_event, [sample_attendee], 'Test cancellation', 'en')
            else:
                # Generic test
                context = email_service._build_event_context(sample_event, sample_attendee)
                rendered = template.render_email(context)
                
                from django.core.mail import send_mail
                send_mail(
                    subject=f"[TEST] {rendered['subject']}",
                    message=rendered['body_text'],
                    from_email=email_service.from_email,
                    recipient_list=[recipient_email],
                    html_message=rendered['body_html']
                )
                success = True
            
            if success:
                return Response({
                    'success': True,
                    'message': 'Test email sent successfully'
                })
            else:
                return Response({
                    'success': False,
                    'error': 'Failed to send email'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error sending test email: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def context_variables(self, request):
        """
        Get available template context variables
        """
        variables = EmailTemplateManager.get_template_context_variables()
        return Response({
            'success': True,
            'variables': variables
        })
    
    @action(detail=False, methods=['post'])
    def validate_syntax(self, request):
        """
        Validate template syntax
        """
        subject_template = request.data.get('subject_template', '')
        body_template = request.data.get('body_html_template', '')
        
        validation = EmailTemplateManager.validate_template_syntax(subject_template, body_template)
        
        return Response({
            'valid': validation['valid'],
            'errors': validation['errors']
        })
    
    @action(detail=False, methods=['post'])
    def create_defaults(self, request):
        """
        Create default templates
        """
        try:
            templates = EmailTemplateManager.create_default_templates(request.user)
            return Response({
                'success': True,
                'created_count': len(templates),
                'message': f'Created {len(templates)} default templates'
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _create_sample_event(self, user):
        """Create sample event for testing"""
        from django.utils import timezone
        from datetime import timedelta
        
        return CalendarEvent(
            id='00000000-0000-0000-0000-000000000000',  # Dummy ID
            name='Sample Test Event',
            description='This is a sample event created for email template testing.',
            location='Sample Conference Room',
            videocall_location='https://meet.example.com/test-meeting',
            start=timezone.now() + timedelta(days=1),
            stop=timezone.now() + timedelta(days=1, hours=1),
            user_id=user,
            privacy='public',
            state='open'
        )
    
    def _create_sample_attendee(self, event, email, name):
        """Create sample attendee for testing"""
        return CalendarAttendee(
            event_id=event,
            email=email,
            common_name=name or email.split('@')[0].replace('.', ' ').title(),
            state='needsAction',
            access_token='sample-test-token'
        )


class CalendarEmailLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet for Calendar Email Logs (read-only)
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only show logs for user's events
        user_events = CalendarEvent.objects.filter(user_id=self.request.user)
        return CalendarEmailLog.objects.filter(event__in=user_events).order_by('-created_at')
    
    def get_serializer_class(self):
        from rest_framework import serializers
        
        class CalendarEmailLogSerializer(serializers.ModelSerializer):
            event_name = serializers.CharField(source='event.name', read_only=True)
            template_name = serializers.CharField(source='template.name', read_only=True)
            status_display = serializers.CharField(source='get_status_display', read_only=True)
            
            class Meta:
                model = CalendarEmailLog
                fields = [
                    'id', 'subject', 'recipient_email', 'recipient_name',
                    'event_name', 'template_name', 'status', 'status_display',
                    'sent_at', 'error_message', 'opens_count', 'clicks_count',
                    'created_at'
                ]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get email statistics
        """
        queryset = self.get_queryset()
        
        stats = {
            'total_sent': queryset.filter(status='sent').count(),
            'total_failed': queryset.filter(status='failed').count(),
            'total_pending': queryset.filter(status='pending').count(),
            'total_opens': sum(log.opens_count for log in queryset),
            'total_clicks': sum(log.clicks_count for log in queryset),
        }
        
        # Recent activity (last 30 days)
        from django.utils import timezone
        from datetime import timedelta
        
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_logs = queryset.filter(created_at__gte=thirty_days_ago)
        
        stats['recent_sent'] = recent_logs.filter(status='sent').count()
        stats['recent_failed'] = recent_logs.filter(status='failed').count()
        
        return Response({
            'success': True,
            'stats': stats
        })