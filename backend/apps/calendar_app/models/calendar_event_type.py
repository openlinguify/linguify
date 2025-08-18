from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()


class CalendarEventType(models.Model):
    """
    Calendar event type model based on Open Linguify's calendar.event.type
    Defines categories and visual styling for calendar events
    """
    
    # Basic identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Event type information
    name = models.CharField(max_length=100, unique=True, help_text="Event type name")
    description = models.TextField(blank=True, help_text="Description of this event type")
    
    # Visual customization
    color = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(11)],
        help_text="Color index for calendar display (0-11)"
    )
    
    # Icon support (using Bootstrap Icons or custom icons)
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Icon class (e.g., 'bi-calendar-event', 'bi-briefcase')"
    )
    
    # Configuration
    active = models.BooleanField(default=True)
    is_system = models.BooleanField(
        default=False,
        help_text="Is this a system-defined event type?"
    )
    
    # Default settings for events of this type
    default_duration = models.PositiveIntegerField(
        default=60,
        help_text="Default duration in minutes for events of this type"
    )
    default_privacy = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public'),
            ('private', 'Private'),
            ('confidential', 'Confidential'),
        ],
        default='public',
        help_text="Default privacy setting for events of this type"
    )
    default_show_as = models.CharField(
        max_length=10,
        choices=[
            ('free', 'Free'),
            ('busy', 'Busy'),
        ],
        default='busy',
        help_text="Default availability setting for events of this type"
    )
    
    # Default alarms for this event type
    default_alarm_ids = models.ManyToManyField(
        'CalendarAlarm',
        blank=True,
        related_name='default_for_event_types',
        help_text="Default alarms for events of this type"
    )
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Calendar Event Type'
        verbose_name_plural = 'Calendar Event Types'
        ordering = ['name']
        indexes = [
            models.Index(fields=['active']),
            models.Index(fields=['is_system']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_color_class(self):
        """Get CSS class for the color"""
        # Map color indices to CSS classes
        color_classes = [
            'event-color-0',   # Default blue
            'event-color-1',   # Green
            'event-color-2',   # Red
            'event-color-3',   # Yellow
            'event-color-4',   # Purple
            'event-color-5',   # Orange
            'event-color-6',   # Pink
            'event-color-7',   # Cyan
            'event-color-8',   # Indigo
            'event-color-9',   # Teal
            'event-color-10',  # Dark
            'event-color-11',  # Secondary
        ]
        return color_classes[self.color] if 0 <= self.color < len(color_classes) else color_classes[0]
    
    def get_bootstrap_color(self):
        """Get Bootstrap color variant"""
        bootstrap_colors = [
            'primary',    # 0 - Blue
            'success',    # 1 - Green
            'danger',     # 2 - Red
            'warning',    # 3 - Yellow
            'info',       # 4 - Light blue
            'secondary',  # 5 - Gray
            'dark',       # 6 - Dark
            'light',      # 7 - Light
            'primary',    # 8 - Blue variant
            'success',    # 9 - Green variant
            'danger',     # 10 - Red variant
            'warning',    # 11 - Yellow variant
        ]
        return bootstrap_colors[self.color] if 0 <= self.color < len(bootstrap_colors) else bootstrap_colors[0]
    
    def get_icon_display(self):
        """Get icon with fallback"""
        return self.icon or 'bi-calendar-event'
    
    def get_events_count(self):
        """Get number of events using this type"""
        return self.events.count()
    
    def get_active_events_count(self):
        """Get number of active events using this type"""
        return self.events.filter(active=True).count()
    
    @classmethod
    def get_default_types(cls):
        """Create and return default event types"""
        default_types = [
            {
                'name': 'Meeting',
                'description': 'Business meetings and conferences',
                'color': 0,  # Primary blue
                'icon': 'bi-people',
                'default_duration': 60,
                'is_system': True,
            },
            {
                'name': 'Appointment',
                'description': 'Personal appointments',
                'color': 1,  # Success green
                'icon': 'bi-person-check',
                'default_duration': 30,
                'is_system': True,
            },
            {
                'name': 'Reminder',
                'description': 'Personal reminders and tasks',
                'color': 3,  # Warning yellow
                'icon': 'bi-bell',
                'default_duration': 15,
                'default_show_as': 'free',
                'is_system': True,
            },
            {
                'name': 'Event',
                'description': 'Special events and celebrations',
                'color': 4,  # Info light blue
                'icon': 'bi-calendar-event',
                'default_duration': 120,
                'is_system': True,
            },
            {
                'name': 'Travel',
                'description': 'Travel and transportation',
                'color': 5,  # Secondary gray
                'icon': 'bi-airplane',
                'default_duration': 240,
                'is_system': True,
            },
            {
                'name': 'Holiday',
                'description': 'Holidays and time off',
                'color': 2,  # Danger red
                'icon': 'bi-calendar-x',
                'default_duration': 1440,  # Full day
                'default_show_as': 'free',
                'is_system': True,
            },
        ]
        
        created_types = []
        for type_data in default_types:
            event_type, created = cls.objects.get_or_create(
                name=type_data['name'],
                defaults=type_data
            )
            created_types.append(event_type)
        
        return created_types
    
    @classmethod
    def get_user_types(cls, user=None):
        """Get event types available to a user"""
        # For now, return all active types
        # In the future, this could be filtered by user permissions
        return cls.objects.filter(active=True).order_by('name')
    
    @classmethod
    def create_custom_type(cls, name, user=None, **kwargs):
        """Create a custom event type"""
        defaults = {
            'description': f'Custom event type: {name}',
            'color': 0,
            'icon': 'bi-calendar-event',
            'is_system': False,
        }
        defaults.update(kwargs)
        
        return cls.objects.create(name=name, **defaults)


class CalendarEventTypeCategory(models.Model):
    """
    Categories for organizing event types
    Allows grouping event types into logical categories
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Category information
    name = models.CharField(max_length=100, unique=True, help_text="Category name")
    description = models.TextField(blank=True, help_text="Category description")
    
    # Visual
    color = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(11)],
        help_text="Color index for category display"
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Icon class for category"
    )
    
    # Order and visibility
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    active = models.BooleanField(default=True)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Calendar Event Type Category'
        verbose_name_plural = 'Calendar Event Type Categories'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def get_event_types(self):
        """Get event types in this category"""
        return self.event_types.filter(active=True).order_by('name')
    
    @classmethod
    def get_default_categories(cls):
        """Create and return default categories"""
        default_categories = [
            {
                'name': 'Business',
                'description': 'Work-related events and meetings',
                'color': 0,
                'icon': 'bi-briefcase',
                'order': 1,
            },
            {
                'name': 'Personal',
                'description': 'Personal appointments and events',
                'color': 1,
                'icon': 'bi-person',
                'order': 2,
            },
            {
                'name': 'Social',
                'description': 'Social events and gatherings',
                'color': 4,
                'icon': 'bi-people',
                'order': 3,
            },
            {
                'name': 'Travel',
                'description': 'Travel and transportation',
                'color': 5,
                'icon': 'bi-airplane',
                'order': 4,
            },
        ]
        
        created_categories = []
        for cat_data in default_categories:
            category, created = cls.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            created_categories.append(category)
        
        return created_categories


# Add category relationship to CalendarEventType
# This would be added to the CalendarEventType model if we were modifying it
class CalendarEventTypeExtension(models.Model):
    """
    Extension to add category relationship to CalendarEventType
    This is a separate model to avoid circular imports
    """
    
    event_type = models.OneToOneField(
        CalendarEventType,
        on_delete=models.CASCADE,
        related_name='extension'
    )
    category = models.ForeignKey(
        CalendarEventTypeCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='event_types'
    )
    
    # Additional settings that might be category-specific
    is_featured = models.BooleanField(default=False)
    order_in_category = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Calendar Event Type Extension'
        verbose_name_plural = 'Calendar Event Type Extensions'
        ordering = ['order_in_category']