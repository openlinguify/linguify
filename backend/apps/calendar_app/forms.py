from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import CalendarEvent, CalendarEventType, CalendarAlarm, CalendarRecurrence

User = get_user_model()


class CalendarEventForm(forms.ModelForm):
    """
    Form for creating and editing calendar events
    """
    
    # Additional fields not in the model
    is_recurring = forms.BooleanField(
        required=False,
        initial=False,
        help_text="Make this a recurring event"
    )
    
    attendees_emails = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        help_text="JSON string of attendee emails"
    )
    
    class Meta:
        model = CalendarEvent
        fields = [
            'name', 'description', 'location', 'videocall_location',
            'start', 'stop', 'allday', 'event_type', 'privacy', 
            'show_as', 'color', 'alarm_ids'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Event title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Event description...'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Event location'
            }),
            'videocall_location': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Video call URL'
            }),
            'start': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'stop': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'allday': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'event_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'privacy': forms.Select(attrs={
                'class': 'form-select'
            }),
            'show_as': forms.Select(attrs={
                'class': 'form-select'
            }),
            'color': forms.Select(attrs={
                'class': 'form-select'
            }),
            'alarm_ids': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customize field choices
        self.fields['event_type'].queryset = CalendarEventType.objects.filter(active=True)
        self.fields['event_type'].empty_label = "Select event type"
        
        self.fields['alarm_ids'].queryset = CalendarAlarm.objects.filter(active=True)
        
        # Add color choices
        color_choices = [
            (0, 'Blue'), (1, 'Green'), (2, 'Red'), (3, 'Yellow'),
            (4, 'Purple'), (5, 'Orange'), (6, 'Pink'), (7, 'Cyan'),
            (8, 'Indigo'), (9, 'Teal'), (10, 'Dark'), (11, 'Secondary')
        ]
        self.fields['color'].choices = color_choices
        
        # Format datetime fields for HTML5 input
        if self.instance and self.instance.pk:
            if self.instance.start:
                self.fields['start'].initial = self.instance.start.strftime('%Y-%m-%dT%H:%M')
            if self.instance.stop:
                self.fields['stop'].initial = self.instance.stop.strftime('%Y-%m-%dT%H:%M')
    
    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start')
        stop = cleaned_data.get('stop')
        
        if start and stop:
            if start >= stop:
                raise forms.ValidationError("End time must be after start time.")
        
        return cleaned_data


class QuickEventForm(forms.ModelForm):
    """
    Simplified form for quick event creation
    """
    
    class Meta:
        model = CalendarEvent
        fields = ['name', 'start', 'stop', 'allday']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Event title',
                'required': True
            }),
            'start': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'required': True
            }),
            'stop': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'required': True
            }),
            'allday': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start')
        stop = cleaned_data.get('stop')
        
        if start and stop:
            if start >= stop:
                raise forms.ValidationError("End time must be after start time.")
        
        # Set default duration if stop is not provided
        if start and not stop:
            cleaned_data['stop'] = start + timedelta(hours=1)
        
        return cleaned_data


class RecurrenceForm(forms.ModelForm):
    """
    Form for configuring event recurrence
    """
    
    class Meta:
        model = CalendarRecurrence
        fields = [
            'rrule_type', 'interval', 'monday', 'tuesday', 'wednesday',
            'thursday', 'friday', 'saturday', 'sunday', 'month_by',
            'day', 'weekday', 'byday', 'end_type', 'count', 'until'
        ]
        widgets = {
            'rrule_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'interval': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'value': 1
            }),
            'monday': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'tuesday': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'wednesday': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'thursday': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'friday': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'saturday': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sunday': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'month_by': forms.Select(attrs={'class': 'form-select'}),
            'day': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 31
            }),
            'weekday': forms.Select(attrs={'class': 'form-select'}),
            'byday': forms.TextInput(attrs={'class': 'form-control'}),
            'end_type': forms.Select(attrs={'class': 'form-select'}),
            'count': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'until': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set default values
        self.fields['interval'].initial = 1
        self.fields['end_type'].initial = 'forever'
        
        # Format until field for HTML5 input
        if self.instance and self.instance.pk and self.instance.until:
            self.fields['until'].initial = self.instance.until.strftime('%Y-%m-%dT%H:%M')


class EventTypeForm(forms.ModelForm):
    """
    Form for creating and editing event types
    """
    
    class Meta:
        model = CalendarEventType
        fields = [
            'name', 'description', 'color', 'icon', 'default_duration',
            'default_privacy', 'default_show_as', 'default_alarm_ids'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Event type name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description...'
            }),
            'color': forms.Select(attrs={'class': 'form-select'}),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'bi-calendar-event'
            }),
            'default_duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'default_privacy': forms.Select(attrs={'class': 'form-select'}),
            'default_show_as': forms.Select(attrs={'class': 'form-select'}),
            'default_alarm_ids': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add color choices
        color_choices = [
            (0, 'Blue'), (1, 'Green'), (2, 'Red'), (3, 'Yellow'),
            (4, 'Purple'), (5, 'Orange'), (6, 'Pink'), (7, 'Cyan'),
            (8, 'Indigo'), (9, 'Teal'), (10, 'Dark'), (11, 'Secondary')
        ]
        self.fields['color'].choices = color_choices
        
        self.fields['default_alarm_ids'].queryset = CalendarAlarm.objects.filter(active=True)


class AlarmForm(forms.ModelForm):
    """
    Form for creating and editing alarms
    """
    
    class Meta:
        model = CalendarAlarm
        fields = ['name', 'alarm_type', 'duration', 'duration_unit']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Alarm name'
            }),
            'alarm_type': forms.Select(attrs={'class': 'form-select'}),
            'duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'duration_unit': forms.Select(attrs={'class': 'form-select'}),
        }


class CalendarSettingsForm(forms.Form):
    """
    Form for calendar user settings
    """
    
    VIEW_CHOICES = [
        ('month', 'Month'),
        ('week', 'Week'),
        ('day', 'Day'),
        ('agenda', 'Agenda'),
    ]
    
    default_view = forms.ChoiceField(
        choices=VIEW_CHOICES,
        initial='month',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    default_duration = forms.IntegerField(
        initial=60,
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 1
        }),
        help_text="Default event duration in minutes"
    )
    
    weekend_visible = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Show weekends in calendar"
    )
    
    start_of_week = forms.ChoiceField(
        choices=[
            (0, 'Monday'),
            (1, 'Tuesday'),
            (2, 'Wednesday'),
            (3, 'Thursday'),
            (4, 'Friday'),
            (5, 'Saturday'),
            (6, 'Sunday'),
        ],
        initial=0,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    time_format = forms.ChoiceField(
        choices=[
            ('12', '12 hour (AM/PM)'),
            ('24', '24 hour'),
        ],
        initial='12',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    default_privacy = forms.ChoiceField(
        choices=CalendarEvent.PRIVACY_CHOICES,
        initial='public',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    default_show_as = forms.ChoiceField(
        choices=CalendarEvent.SHOW_AS_CHOICES,
        initial='busy',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    default_alarms = forms.ModelMultipleChoiceField(
        queryset=CalendarAlarm.objects.filter(active=True),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )


class AttendeeInlineForm(forms.Form):
    """
    Form for adding attendees to events
    """
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email address'
        })
    )
    
    name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Full name (optional)'
        })
    )


# FormSet for multiple attendees
AttendeeFormSet = forms.formset_factory(
    AttendeeInlineForm,
    extra=3,
    can_delete=True
)