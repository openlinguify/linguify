from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta
import json

from ..models import (
    CalendarEvent, CalendarEventType, CalendarAlarm, 
    CalendarAttendee, CalendarRecurrence
)
from ..serializers import (
    CalendarEventSerializer, CalendarEventTypeSerializer,
    CalendarAlarmSerializer, CalendarAttendeeSerializer,
    CalendarRecurrenceSerializer
)


class CalendarEventViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Calendar Events
    Provides CRUD operations and calendar-specific actions
    """
    serializer_class = CalendarEventSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter events user can access"""
        return CalendarEvent.objects.filter(
            Q(user_id=self.request.user) | Q(attendee_ids__partner_id=self.request.user)
        ).distinct().select_related('user_id', 'event_type').prefetch_related('attendee_ids')
    
    def perform_create(self, serializer):
        """Set current user as organizer"""
        serializer.save(user_id=self.request.user)
    
    @action(detail=False, methods=['get'])
    def calendar_feed(self, request):
        """
        Get events for calendar display (FullCalendar format)
        """
        # Get date range from query params
        start_str = request.query_params.get('start')
        end_str = request.query_params.get('end')
        
        if not start_str or not end_str:
            return Response({'error': 'Missing start or end date'}, status=400)
        
        try:
            start_date = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
        except ValueError:
            return Response({'error': 'Invalid date format'}, status=400)
        
        # Get events in range
        events = self.get_queryset().filter(
            start__gte=start_date,
            start__lt=end_date,
            active=True
        )
        
        # Convert to FullCalendar format
        calendar_events = []
        for event in events:
            calendar_event = {
                'id': str(event.id),
                'title': event.name,
                'start': event.start.isoformat(),
                'end': event.stop.isoformat(),
                'allDay': event.allday,
                'backgroundColor': self.get_event_color(event),
                'borderColor': self.get_event_color(event),
                'textColor': '#ffffff',
                'extendedProps': {
                    'description': event.description,
                    'location': event.location,
                    'privacy': event.privacy,
                    'organizer': event.user_id.get_full_name() or event.user_id.username,
                    'attendees_count': event.get_attendees_count(),
                    'type': event.event_type.name if event.event_type else None,
                    'can_edit': event.can_edit(request.user),
                }
            }
            calendar_events.append(calendar_event)
        
        return Response(calendar_events)
    
    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None):
        """
        Respond to an event invitation
        """
        event = self.get_object()
        response_type = request.data.get('response')
        
        if response_type not in ['accept', 'decline', 'tentative']:
            return Response({'error': 'Invalid response type'}, status=400)
        
        try:
            attendee = event.attendee_ids.get(partner_id=request.user)
        except CalendarAttendee.DoesNotExist:
            return Response({'error': 'You are not invited to this event'}, status=403)
        
        # Update response
        if response_type == 'accept':
            attendee.do_accept()
        elif response_type == 'decline':
            attendee.do_decline()
        elif response_type == 'tentative':
            attendee.do_tentative()
        
        return Response({
            'status': attendee.state,
            'status_display': attendee.get_state_display()
        })
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """
        Duplicate an event
        """
        event = self.get_object()
        
        # Get new date/time if provided
        new_start = request.data.get('start')
        if new_start:
            try:
                new_start = datetime.fromisoformat(new_start)
            except ValueError:
                return Response({'error': 'Invalid start date format'}, status=400)
        
        # Create duplicate
        new_event = event.copy_event(start_datetime=new_start)
        
        serializer = self.get_serializer(new_event)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def quick_create(self, request):
        """
        Quick event creation
        """
        data = request.data.copy()
        data['user_id'] = request.user.id
        
        # Set default duration if not provided
        if 'stop' not in data and 'start' in data:
            try:
                start = datetime.fromisoformat(data['start'])
                stop = start + timedelta(hours=1)
                data['stop'] = stop.isoformat()
            except ValueError:
                pass
        
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            event = serializer.save()
            
            # Create organizer as attendee
            CalendarAttendee.get_or_create_for_organizer(event)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """
        Get upcoming events for the user
        """
        limit = int(request.query_params.get('limit', 10))
        
        events = self.get_queryset().filter(
            start__gte=timezone.now(),
            active=True
        ).order_by('start')[:limit]
        
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)
    
    def get_event_color(self, event):
        """Get color for an event"""
        colors = [
            '#007bff', '#28a745', '#dc3545', '#ffc107',
            '#6f42c1', '#fd7e14', '#e83e8c', '#17a2b8',
            '#6610f2', '#20c997', '#343a40', '#6c757d'
        ]
        
        if event.event_type:
            color_index = event.event_type.color
        else:
            color_index = event.color
        
        if 0 <= color_index < len(colors):
            return colors[color_index]
        
        return colors[0]


class CalendarEventTypeViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Calendar Event Types
    """
    serializer_class = CalendarEventTypeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CalendarEventType.objects.filter(active=True).order_by('name')
    
    @action(detail=False, methods=['get'])
    def defaults(self, request):
        """Get default event types"""
        default_types = CalendarEventType.get_default_types()
        serializer = self.get_serializer(default_types, many=True)
        return Response(serializer.data)


class CalendarAlarmViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Calendar Alarms
    """
    serializer_class = CalendarAlarmSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CalendarAlarm.objects.filter(active=True).order_by('duration', 'duration_unit')
    
    @action(detail=False, methods=['get'])
    def defaults(self, request):
        """Get default alarms"""
        default_alarms = CalendarAlarm.get_default_alarms()
        serializer = self.get_serializer(default_alarms, many=True)
        return Response(serializer.data)


class CalendarAttendeeViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Calendar Attendees
    """
    serializer_class = CalendarAttendeeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only show attendees for events the user can access
        user_events = CalendarEvent.objects.filter(
            Q(user_id=self.request.user) | Q(attendee_ids__partner_id=self.request.user)
        ).distinct()
        
        return CalendarAttendee.objects.filter(
            event_id__in=user_events
        ).select_related('partner_id', 'event_id')


class CalendarRecurrenceViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Calendar Recurrences
    """
    serializer_class = CalendarRecurrenceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only show recurrences for events the user can access
        user_events = CalendarEvent.objects.filter(
            Q(user_id=self.request.user) | Q(attendee_ids__partner_id=self.request.user)
        ).distinct()
        
        return CalendarRecurrence.objects.filter(
            base_event_id__in=user_events
        ).select_related('base_event_id')
    
    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        """
        Apply recurrence rule to generate events
        """
        recurrence = self.get_object()
        limit = int(request.data.get('limit', 50))
        
        created_events = recurrence.apply_recurrence(limit=limit)
        
        return Response({
            'created_count': len(created_events),
            'events': [str(event.id) for event in created_events]
        })
    
    @action(detail=True, methods=['post'])
    def split(self, request, pk=None):
        """
        Split recurrence from a specific date
        """
        recurrence = self.get_object()
        split_date_str = request.data.get('split_date')
        
        if not split_date_str:
            return Response({'error': 'split_date is required'}, status=400)
        
        try:
            split_date = datetime.fromisoformat(split_date_str)
        except ValueError:
            return Response({'error': 'Invalid date format'}, status=400)
        
        new_recurrence = recurrence.split_from(split_date)
        serializer = self.get_serializer(new_recurrence)
        
        return Response(serializer.data)