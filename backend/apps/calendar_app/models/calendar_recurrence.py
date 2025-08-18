from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
import uuid
from datetime import datetime, timedelta, date
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY, YEARLY
from dateutil.rrule import MO, TU, WE, TH, FR, SA, SU
import pytz
import calendar as python_calendar

User = get_user_model()


class CalendarRecurrence(models.Model):
    """
    Calendar recurrence model based on Odoo's calendar.recurrence
    Manages recurring event patterns and generation
    """
    
    # Recurrence type choices
    RRULE_TYPE_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    # End type choices
    END_TYPE_CHOICES = [
        ('count', 'Number of repetitions'),
        ('end_date', 'End date'),
        ('forever', 'Forever'),
    ]
    
    # Month by choices for monthly recurrence
    MONTH_BY_CHOICES = [
        ('date', 'Date of month'),
        ('day', 'Day of month'),
    ]
    
    # Weekday choices
    WEEKDAY_CHOICES = [
        ('MO', 'Monday'),
        ('TU', 'Tuesday'), 
        ('WE', 'Wednesday'),
        ('TH', 'Thursday'),
        ('FR', 'Friday'),
        ('SA', 'Saturday'),
        ('SU', 'Sunday'),
    ]
    
    # Basic identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Recurrence information
    name = models.CharField(max_length=200, help_text="Human readable recurrence name")
    base_event_id = models.ForeignKey(
        'CalendarEvent',
        on_delete=models.CASCADE,
        related_name='base_recurrences',
        help_text="The base event for this recurrence"
    )
    
    # Recurrence pattern
    rrule_type = models.CharField(
        max_length=20,
        choices=RRULE_TYPE_CHOICES,
        default='weekly',
        help_text="Type of recurrence"
    )
    interval = models.PositiveIntegerField(
        default=1,
        help_text="Repeat every X periods"
    )
    
    # Weekly recurrence - weekdays
    monday = models.BooleanField(default=False)
    tuesday = models.BooleanField(default=False)
    wednesday = models.BooleanField(default=False)
    thursday = models.BooleanField(default=False)
    friday = models.BooleanField(default=False)
    saturday = models.BooleanField(default=False)
    sunday = models.BooleanField(default=False)
    
    # Monthly recurrence
    month_by = models.CharField(
        max_length=10,
        choices=MONTH_BY_CHOICES,
        default='date',
        help_text="Monthly recurrence pattern"
    )
    day = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Day of month (1-31)"
    )
    weekday = models.CharField(
        max_length=2,
        choices=WEEKDAY_CHOICES,
        blank=True,
        help_text="Weekday for monthly recurrence"
    )
    byday = models.CharField(
        max_length=10,
        blank=True,
        help_text="Week of month (-1 to 5)"
    )
    
    # End condition
    end_type = models.CharField(
        max_length=20,
        choices=END_TYPE_CHOICES,
        default='forever',
        help_text="How the recurrence ends"
    )
    count = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of occurrences"
    )
    until = models.DateTimeField(
        null=True,
        blank=True,
        help_text="End date for recurrence"
    )
    
    # Timezone and timing
    dtstart = models.DateTimeField(help_text="Recurrence start datetime")
    event_tz = models.CharField(
        max_length=50,
        default='UTC',
        help_text="Timezone for the events"
    )
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Calendar Recurrence'
        verbose_name_plural = 'Calendar Recurrences'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_rrule_type_display()}"
    
    def clean(self):
        """Validate recurrence data"""
        if self.end_type == 'count' and not self.count:
            raise ValidationError("Count is required when end type is 'count'")
        if self.end_type == 'end_date' and not self.until:
            raise ValidationError("End date is required when end type is 'end_date'")
        if self.rrule_type == 'monthly' and self.month_by == 'date' and not self.day:
            raise ValidationError("Day is required for monthly recurrence by date")
    
    def save(self, *args, **kwargs):
        """Override save to generate name if not provided"""
        if not self.name:
            self.name = self.generate_name()
        super().save(*args, **kwargs)
    
    def generate_name(self):
        """Generate a human-readable name for the recurrence"""
        if self.base_event_id:
            return f"Recurrence for {self.base_event_id.name}"
        return f"Recurrence - {self.get_rrule_type_display()}"
    
    @property
    def weekdays_list(self):
        """Get list of selected weekdays"""
        weekdays = []
        if self.monday: weekdays.append('MO')
        if self.tuesday: weekdays.append('TU')
        if self.wednesday: weekdays.append('WE')
        if self.thursday: weekdays.append('TH')
        if self.friday: weekdays.append('FR')
        if self.saturday: weekdays.append('SA')
        if self.sunday: weekdays.append('SU')
        return weekdays
    
    @property
    def weekdays_int_list(self):
        """Get list of weekdays as integers (0=Monday, 6=Sunday)"""
        mapping = {'MO': 0, 'TU': 1, 'WE': 2, 'TH': 3, 'FR': 4, 'SA': 5, 'SU': 6}
        return [mapping[day] for day in self.weekdays_list]
    
    def get_recurrence_description(self):
        """Get human-readable recurrence description"""
        desc_parts = []
        
        # Base frequency
        if self.interval == 1:
            desc_parts.append(f"Every {self.get_rrule_type_display().lower()}")
        else:
            desc_parts.append(f"Every {self.interval} {self.rrule_type}s")
        
        # Weekly specifics
        if self.rrule_type == 'weekly' and self.weekdays_list:
            weekday_names = [dict(self.WEEKDAY_CHOICES)[day] for day in self.weekdays_list]
            desc_parts.append(f"on {', '.join(weekday_names)}")
        
        # Monthly specifics
        if self.rrule_type == 'monthly':
            if self.month_by == 'date' and self.day:
                desc_parts.append(f"on day {self.day}")
            elif self.month_by == 'day' and self.weekday and self.byday:
                weekday_name = dict(self.WEEKDAY_CHOICES)[self.weekday]
                desc_parts.append(f"on the {self.byday} {weekday_name}")
        
        # End condition
        if self.end_type == 'count' and self.count:
            desc_parts.append(f"for {self.count} times")
        elif self.end_type == 'end_date' and self.until:
            desc_parts.append(f"until {self.until.strftime('%Y-%m-%d')}")
        
        return " ".join(desc_parts)
    
    def get_dateutil_rrule(self, dtstart=None, count_limit=None):
        """Convert to dateutil rrule for generation"""
        if dtstart is None:
            dtstart = self.dtstart
        
        # Map recurrence types
        freq_map = {
            'daily': DAILY,
            'weekly': WEEKLY,
            'monthly': MONTHLY,
            'yearly': YEARLY,
        }
        
        # Base parameters
        rrule_params = {
            'freq': freq_map[self.rrule_type],
            'interval': self.interval,
            'dtstart': dtstart,
        }
        
        # Handle end condition
        if self.end_type == 'count' and self.count:
            rrule_params['count'] = min(self.count, count_limit or 720)  # Limit to prevent infinite generation
        elif self.end_type == 'end_date' and self.until:
            rrule_params['until'] = self.until
        elif count_limit:
            rrule_params['count'] = count_limit
        
        # Handle weekly recurrence
        if self.rrule_type == 'weekly' and self.weekdays_list:
            weekday_map = {'MO': MO, 'TU': TU, 'WE': WE, 'TH': TH, 'FR': FR, 'SA': SA, 'SU': SU}
            rrule_params['byweekday'] = [weekday_map[day] for day in self.weekdays_list]
        
        # Handle monthly recurrence
        if self.rrule_type == 'monthly':
            if self.month_by == 'date' and self.day:
                rrule_params['bymonthday'] = self.day
            elif self.month_by == 'day' and self.weekday and self.byday:
                weekday_map = {'MO': MO, 'TU': TU, 'WE': WE, 'TH': TH, 'FR': FR, 'SA': SA, 'SU': SU}
                week_num = int(self.byday) if self.byday.isdigit() or self.byday.startswith('-') else 1
                rrule_params['byweekday'] = weekday_map[self.weekday](week_num)
        
        return rrule(**rrule_params)
    
    def generate_occurrences(self, start_date=None, end_date=None, count_limit=100):
        """Generate list of occurrence datetimes"""
        if start_date is None:
            start_date = self.dtstart
        
        rule = self.get_dateutil_rrule(dtstart=start_date, count_limit=count_limit)
        
        occurrences = []
        for occurrence in rule:
            # Apply end_date filter if provided
            if end_date and occurrence > end_date:
                break
            occurrences.append(occurrence)
            
            # Safety limit
            if len(occurrences) >= count_limit:
                break
        
        return occurrences
    
    def apply_recurrence(self, limit=100):
        """
        Apply recurrence rule to generate calendar events
        Based on Odoo's _apply_recurrence method
        """
        from .calendar_event import CalendarEvent
        
        if not self.base_event_id:
            return []
        
        # Get existing events for this recurrence
        existing_events = CalendarEvent.objects.filter(recurrence_id=self)
        existing_starts = set(event.start for event in existing_events)
        
        # Generate occurrences
        occurrences = self.generate_occurrences(count_limit=limit)
        
        created_events = []
        base_event = self.base_event_id
        
        for occurrence_start in occurrences:
            # Skip if event already exists for this occurrence
            if occurrence_start in existing_starts:
                continue
            
            # Calculate duration for the new event
            duration = base_event.stop - base_event.start
            occurrence_stop = occurrence_start + duration
            
            # Create new event based on base event
            new_event = base_event.copy_event(
                start_datetime=occurrence_start,
                stop=occurrence_stop,
                recurrence_id=self,
                recurrency=True
            )
            
            created_events.append(new_event)
        
        return created_events
    
    def split_from(self, date_from):
        """
        Split recurrence from a specific date
        Creates a new recurrence starting from date_from
        """
        if date_from <= self.dtstart:
            return self
        
        # Update current recurrence to end before split date
        if self.end_type == 'forever':
            self.end_type = 'end_date'
            self.until = date_from - timedelta(days=1)
        elif self.end_type == 'end_date' and self.until:
            self.until = min(self.until, date_from - timedelta(days=1))
        
        self.save()
        
        # Create new recurrence from split date
        new_recurrence = CalendarRecurrence.objects.create(
            base_event_id=self.base_event_id,
            rrule_type=self.rrule_type,
            interval=self.interval,
            monday=self.monday,
            tuesday=self.tuesday,
            wednesday=self.wednesday,
            thursday=self.thursday,
            friday=self.friday,
            saturday=self.saturday,
            sunday=self.sunday,
            month_by=self.month_by,
            day=self.day,
            weekday=self.weekday,
            byday=self.byday,
            end_type=self.end_type,
            count=self.count,
            until=self.until,
            dtstart=date_from,
            event_tz=self.event_tz,
        )
        
        return new_recurrence
    
    def stop_at(self, date_until):
        """Stop recurrence at a specific date"""
        self.end_type = 'end_date'
        self.until = date_until
        self.save()
        
        # Remove future events beyond this date
        from .calendar_event import CalendarEvent
        CalendarEvent.objects.filter(
            recurrence_id=self,
            start__gt=date_until
        ).delete()
    
    @classmethod
    def create_from_event(cls, event, **recurrence_params):
        """Create a recurrence rule from an event"""
        defaults = {
            'base_event_id': event,
            'dtstart': event.start,
            'event_tz': str(event.start.tzinfo) if event.start.tzinfo else 'UTC',
        }
        defaults.update(recurrence_params)
        
        recurrence = cls.objects.create(**defaults)
        
        # Update event to mark as recurring
        event.recurrency = True
        event.recurrence_id = recurrence
        event.save()
        
        return recurrence


class CalendarRecurrenceException(models.Model):
    """
    Exception to recurrence rules
    Handles deleted or modified occurrences
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    recurrence_id = models.ForeignKey(
        CalendarRecurrence,
        on_delete=models.CASCADE,
        related_name='exceptions'
    )
    exception_date = models.DateTimeField(help_text="Date of the exception")
    
    # Exception type
    is_deleted = models.BooleanField(
        default=False,
        help_text="Is this occurrence deleted?"
    )
    replacement_event = models.ForeignKey(
        'CalendarEvent',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Replacement event for modified occurrence"
    )
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Calendar Recurrence Exception'
        verbose_name_plural = 'Calendar Recurrence Exceptions'
        unique_together = ['recurrence_id', 'exception_date']
        ordering = ['exception_date']
    
    def __str__(self):
        status = "Deleted" if self.is_deleted else "Modified"
        return f"{status} occurrence on {self.exception_date.strftime('%Y-%m-%d')}"