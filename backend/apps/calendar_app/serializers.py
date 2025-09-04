from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    CalendarEvent, CalendarEventType, CalendarAlarm, 
    CalendarAttendee, CalendarRecurrence, CalendarInvitation
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Minimal user serializer for calendar context"""
    
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name']
        read_only_fields = ['id', 'username', 'email', 'full_name']


class CalendarEventTypeSerializer(serializers.ModelSerializer):
    """Serializer for Calendar Event Types"""
    
    color_class = serializers.CharField(source='get_color_class', read_only=True)
    bootstrap_color = serializers.CharField(source='get_bootstrap_color', read_only=True)
    icon_display = serializers.CharField(source='get_icon_display', read_only=True)
    events_count = serializers.IntegerField(source='get_events_count', read_only=True)
    
    class Meta:
        model = CalendarEventType
        fields = [
            'id', 'name', 'description', 'color', 'icon', 'active',
            'default_duration', 'default_privacy', 'default_show_as',
            'color_class', 'bootstrap_color', 'icon_display', 'events_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CalendarAlarmSerializer(serializers.ModelSerializer):
    """Serializer for Calendar Alarms"""
    
    duration_display = serializers.CharField(source='get_duration_display', read_only=True)
    duration_minutes = serializers.IntegerField(source='get_duration_minutes', read_only=True)
    
    class Meta:
        model = CalendarAlarm
        fields = [
            'id', 'name', 'alarm_type', 'duration', 'duration_unit',
            'active', 'duration_display', 'duration_minutes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CalendarAttendeeSerializer(serializers.ModelSerializer):
    """Serializer for Calendar Attendees"""
    
    partner = UserSerializer(source='partner_id', read_only=True)
    display_name = serializers.CharField(source='get_display_name', read_only=True)
    response_icon = serializers.CharField(source='get_response_icon', read_only=True)
    response_color = serializers.CharField(source='get_response_color', read_only=True)
    is_organizer = serializers.BooleanField(read_only=True)
    has_responded = serializers.BooleanField(read_only=True)
    is_attending = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = CalendarAttendee
        fields = [
            'id', 'email', 'common_name', 'state', 'availability',
            'partner', 'display_name', 'response_icon', 'response_color',
            'is_organizer', 'has_responded', 'is_attending',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'access_token', 'created_at', 'updated_at',
            'partner', 'display_name', 'response_icon', 'response_color',
            'is_organizer', 'has_responded', 'is_attending'
        ]


class CalendarRecurrenceSerializer(serializers.ModelSerializer):
    """Serializer for Calendar Recurrences"""
    
    weekdays_list = serializers.ListField(read_only=True)
    recurrence_description = serializers.CharField(
        source='get_recurrence_description', read_only=True
    )
    
    class Meta:
        model = CalendarRecurrence
        fields = [
            'id', 'name', 'rrule_type', 'interval', 'monday', 'tuesday',
            'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
            'month_by', 'day', 'weekday', 'byday', 'end_type', 'count',
            'until', 'dtstart', 'event_tz', 'weekdays_list',
            'recurrence_description', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'weekdays_list', 'recurrence_description',
            'created_at', 'updated_at'
        ]


class CalendarEventSerializer(serializers.ModelSerializer):
    """Serializer for Calendar Events"""
    
    organizer = UserSerializer(source='user_id', read_only=True)
    event_type_detail = CalendarEventTypeSerializer(source='event_type', read_only=True)
    attendees = CalendarAttendeeSerializer(source='attendee_ids', many=True, read_only=True)
    alarms = CalendarAlarmSerializer(source='alarm_ids', many=True, read_only=True)
    recurrence_detail = CalendarRecurrenceSerializer(source='recurrence_id', read_only=True)
    
    # Computed fields
    duration_display = serializers.CharField(source='get_duration_display', read_only=True)
    attendees_count = serializers.IntegerField(source='get_attendees_count', read_only=True)
    confirmed_attendees_count = serializers.IntegerField(
        source='get_confirmed_attendees_count', read_only=True
    )
    attendees_display = serializers.CharField(source='get_attendees_display', read_only=True)
    recurrence_display = serializers.CharField(
        source='get_recurrence_display', read_only=True
    )
    
    # Status fields
    is_past = serializers.BooleanField(read_only=True)
    is_today = serializers.BooleanField(read_only=True)
    is_upcoming = serializers.BooleanField(read_only=True)
    is_multiday = serializers.BooleanField(read_only=True)
    
    # Permission fields (computed based on request user)
    can_edit = serializers.SerializerMethodField()
    can_view = serializers.SerializerMethodField()
    is_organizer = serializers.SerializerMethodField()
    is_attendee = serializers.SerializerMethodField()
    
    class Meta:
        model = CalendarEvent
        fields = [
            'id', 'name', 'description', 'location', 'videocall_location',
            'start', 'stop', 'allday', 'duration', 'privacy', 'show_as',
            'state', 'active', 'recurrency', 'color',
            'organizer', 'event_type', 'event_type_detail', 'recurrence_id',
            'recurrence_detail', 'attendees', 'alarms',
            'duration_display', 'attendees_count', 'confirmed_attendees_count',
            'attendees_display', 'recurrence_display',
            'is_past', 'is_today', 'is_upcoming', 'is_multiday',
            'can_edit', 'can_view', 'is_organizer', 'is_attendee',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'duration', 'organizer', 'event_type_detail', 'recurrence_detail',
            'attendees', 'alarms', 'duration_display', 'attendees_count',
            'confirmed_attendees_count', 'attendees_display', 'recurrence_display',
            'is_past', 'is_today', 'is_upcoming', 'is_multiday',
            'can_edit', 'can_view', 'is_organizer', 'is_attendee',
            'created_at', 'updated_at'
        ]
    
    def get_can_edit(self, obj):
        """Check if current user can edit this event"""
        request = self.context.get('request')
        if request and request.user:
            return obj.can_edit(request.user)
        return False
    
    def get_can_view(self, obj):
        """Check if current user can view this event"""
        request = self.context.get('request')
        if request and request.user:
            return obj.can_view(request.user)
        return False
    
    def get_is_organizer(self, obj):
        """Check if current user is organizer"""
        request = self.context.get('request')
        if request and request.user:
            return obj.is_organizer(request.user)
        return False
    
    def get_is_attendee(self, obj):
        """Check if current user is attendee"""
        request = self.context.get('request')
        if request and request.user:
            return obj.is_attendee(request.user)
        return False


class CalendarEventListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for event lists"""
    
    organizer_name = serializers.CharField(source='user_id.get_full_name', read_only=True)
    event_type_name = serializers.CharField(source='event_type.name', read_only=True)
    duration_display = serializers.CharField(source='get_duration_display', read_only=True)
    attendees_count = serializers.IntegerField(source='get_attendees_count', read_only=True)
    
    class Meta:
        model = CalendarEvent
        fields = [
            'id', 'name', 'start', 'stop', 'allday', 'location',
            'privacy', 'color', 'organizer_name', 'event_type_name',
            'duration_display', 'attendees_count'
        ]


class CalendarEventCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating calendar events"""
    
    attendees_data = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
        help_text="List of attendee objects with email and optional name"
    )
    
    alarm_ids = serializers.PrimaryKeyRelatedField(
        queryset=CalendarAlarm.objects.filter(active=True),
        many=True,
        required=False
    )
    
    class Meta:
        model = CalendarEvent
        fields = [
            'name', 'description', 'location', 'videocall_location',
            'start', 'stop', 'allday', 'event_type', 'privacy',
            'show_as', 'color', 'alarm_ids', 'attendees_data'
        ]
    
    def create(self, validated_data):
        """Create event with attendees"""
        attendees_data = validated_data.pop('attendees_data', [])
        alarm_ids = validated_data.pop('alarm_ids', [])
        
        # Create event
        event = CalendarEvent.objects.create(**validated_data)
        
        # Set alarms
        event.alarm_ids.set(alarm_ids)
        
        # Create organizer as attendee
        CalendarAttendee.get_or_create_for_organizer(event)
        
        # Create attendees
        for attendee_data in attendees_data:
            if attendee_data.get('email'):
                CalendarAttendee.create_for_email(
                    event=event,
                    email=attendee_data['email'],
                    name=attendee_data.get('name')
                )
        
        return event


class CalendarInvitationSerializer(serializers.ModelSerializer):
    """Serializer for Calendar Invitations"""
    
    attendee_detail = CalendarAttendeeSerializer(source='attendee', read_only=True)
    event_detail = CalendarEventListSerializer(source='event', read_only=True)
    
    class Meta:
        model = CalendarInvitation
        fields = [
            'id', 'subject', 'message', 'status', 'sent_at',
            'error_message', 'responded_at', 'attendee_detail',
            'event_detail', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'sent_at', 'error_message', 'responded_at',
            'attendee_detail', 'event_detail', 'created_at', 'updated_at'
        ]


class CalendarStatsSerializer(serializers.Serializer):
    """Serializer for calendar statistics"""
    
    total_events = serializers.IntegerField()
    upcoming_events = serializers.IntegerField()
    events_today = serializers.IntegerField()
    events_this_week = serializers.IntegerField()
    events_this_month = serializers.IntegerField()
    pending_invitations = serializers.IntegerField()
    
    # Event type breakdown
    events_by_type = serializers.DictField()
    
    # Privacy breakdown
    events_by_privacy = serializers.DictField()
    
    # Recent activity
    recent_events = CalendarEventListSerializer(many=True)
    upcoming_events_list = CalendarEventListSerializer(many=True)