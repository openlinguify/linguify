from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    CalendarEvent, CalendarEventType, CalendarAlarm, CalendarAttendee,
    CalendarRecurrence, CalendarRecurrenceException, CalendarInvitation,
    CalendarAlarmInstance, CalendarEventTypeCategory, CalendarEventTypeExtension,
    CalendarEmailTemplate, CalendarEmailLog
)


@admin.register(CalendarEventType)
class CalendarEventTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_preview', 'icon_preview', 'active', 'is_system', 'events_count']
    list_filter = ['active', 'is_system', 'color']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'active', 'is_system')
        }),
        ('Visual Settings', {
            'fields': ('color', 'icon')
        }),
        ('Default Settings', {
            'fields': ('default_duration', 'default_privacy', 'default_show_as')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def color_preview(self, obj):
        colors = [
            '#007bff', '#28a745', '#dc3545', '#ffc107',
            '#6f42c1', '#fd7e14', '#e83e8c', '#17a2b8',
            '#6610f2', '#20c997', '#343a40', '#6c757d'
        ]
        color = colors[obj.color] if 0 <= obj.color < len(colors) else colors[0]
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border-radius: 3px; display: inline-block;"></div>',
            color
        )
    color_preview.short_description = 'Color'
    
    def icon_preview(self, obj):
        if obj.icon:
            return format_html('<i class="{}"></i> {}', obj.icon, obj.icon)
        return '-'
    icon_preview.short_description = 'Icon'
    
    def events_count(self, obj):
        return obj.events.count()
    events_count.short_description = 'Events'


class CalendarAttendeeInline(admin.TabularInline):
    model = CalendarAttendee
    extra = 0
    readonly_fields = ['access_token', 'created_at']
    fields = ['email', 'common_name', 'state', 'availability', 'access_token']


class CalendarAlarmInline(admin.TabularInline):
    model = CalendarEvent.alarm_ids.through
    extra = 0
    verbose_name = 'Alarm'
    verbose_name_plural = 'Alarms'


@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'organizer', 'start', 'get_duration_display', 
        'event_type', 'privacy', 'attendees_count', 'active'
    ]
    list_filter = [
        'active', 'privacy', 'show_as', 'allday', 'recurrency',
        'event_type', 'created_at'
    ]
    search_fields = ['name', 'description', 'location', 'user_id__username', 'user_id__email']
    readonly_fields = ['duration', 'created_at', 'updated_at']
    date_hierarchy = 'start'
    
    fieldsets = (
        ('Event Information', {
            'fields': ('name', 'description', 'user_id')
        }),
        ('Timing', {
            'fields': ('start', 'stop', 'allday', 'duration')
        }),
        ('Location', {
            'fields': ('location', 'videocall_location')
        }),
        ('Settings', {
            'fields': ('event_type', 'privacy', 'show_as', 'state', 'color', 'active')
        }),
        ('Recurrence', {
            'fields': ('recurrency', 'recurrence_id'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    inlines = [CalendarAttendeeInline, CalendarAlarmInline]
    
    def organizer(self, obj):
        return obj.user_id.get_full_name() or obj.user_id.username
    organizer.short_description = 'Organizer'
    
    def attendees_count(self, obj):
        count = obj.attendee_ids.count()
        if count > 0:
            url = reverse('admin:calendar_calendarattendee_changelist')
            return format_html('<a href="{}?event_id__id__exact={}">{}</a>', url, obj.id, count)
        return count
    attendees_count.short_description = 'Attendees'


@admin.register(CalendarAttendee)
class CalendarAttendeeAdmin(admin.ModelAdmin):
    list_display = ['get_display_name', 'email', 'event_name', 'state', 'is_organizer', 'created_at']
    list_filter = ['state', 'availability', 'created_at']
    search_fields = ['email', 'common_name', 'event_id__name']
    readonly_fields = ['access_token', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Attendee Information', {
            'fields': ('event_id', 'partner_id', 'email', 'common_name')
        }),
        ('Response', {
            'fields': ('state', 'availability')
        }),
        ('Access', {
            'fields': ('access_token',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def event_name(self, obj):
        return obj.event_id.name
    event_name.short_description = 'Event'
    
    def get_display_name(self, obj):
        return obj.get_display_name()
    get_display_name.short_description = 'Name'


@admin.register(CalendarAlarm)
class CalendarAlarmAdmin(admin.ModelAdmin):
    list_display = ['name', 'alarm_type', 'get_duration_display', 'active', 'default_for_user']
    list_filter = ['alarm_type', 'duration_unit', 'active', 'default_for_user']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Alarm Information', {
            'fields': ('name', 'alarm_type', 'active', 'default_for_user')
        }),
        ('Timing', {
            'fields': ('duration', 'duration_unit')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(CalendarRecurrence)
class CalendarRecurrenceAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_event', 'rrule_type', 'interval', 'end_type', 'created_at']
    list_filter = ['rrule_type', 'end_type', 'created_at']
    search_fields = ['name', 'base_event_id__name']
    readonly_fields = ['created_at', 'updated_at', 'weekdays_list', 'get_recurrence_description']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'base_event_id')
        }),
        ('Recurrence Pattern', {
            'fields': ('rrule_type', 'interval')
        }),
        ('Weekly Settings', {
            'fields': ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'),
            'classes': ('collapse',)
        }),
        ('Monthly Settings', {
            'fields': ('month_by', 'day', 'weekday', 'byday'),
            'classes': ('collapse',)
        }),
        ('End Condition', {
            'fields': ('end_type', 'count', 'until')
        }),
        ('Timing', {
            'fields': ('dtstart', 'event_tz')
        }),
        ('Computed Values', {
            'fields': ('weekdays_list', 'get_recurrence_description'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def base_event(self, obj):
        return obj.base_event_id.name if obj.base_event_id else '-'
    base_event.short_description = 'Base Event'


@admin.register(CalendarRecurrenceException)
class CalendarRecurrenceExceptionAdmin(admin.ModelAdmin):
    list_display = ['recurrence_id', 'exception_date', 'is_deleted', 'replacement_event', 'created_at']
    list_filter = ['is_deleted', 'created_at']
    search_fields = ['recurrence_id__name']
    readonly_fields = ['created_at']


@admin.register(CalendarInvitation)
class CalendarInvitationAdmin(admin.ModelAdmin):
    list_display = ['attendee', 'event', 'status', 'sent_at', 'responded_at', 'created_at']
    list_filter = ['status', 'sent_at', 'created_at']
    search_fields = ['attendee__email', 'event__name', 'subject']
    readonly_fields = ['sent_at', 'responded_at', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Invitation Details', {
            'fields': ('attendee', 'event', 'subject', 'message')
        }),
        ('Status', {
            'fields': ('status', 'sent_at', 'error_message')
        }),
        ('Response Tracking', {
            'fields': ('responded_at', 'response_user_agent', 'response_ip')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(CalendarAlarmInstance)
class CalendarAlarmInstanceAdmin(admin.ModelAdmin):
    list_display = ['alarm', 'event', 'user', 'trigger_time', 'status', 'retry_count']
    list_filter = ['status', 'trigger_time', 'created_at']
    search_fields = ['alarm__name', 'event__name', 'user__username']
    readonly_fields = ['triggered_at', 'sent_at', 'dismissed_at', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Instance Details', {
            'fields': ('alarm', 'event', 'user', 'trigger_time')
        }),
        ('Status', {
            'fields': ('status', 'triggered_at', 'sent_at', 'dismissed_at')
        }),
        ('Error Handling', {
            'fields': ('error_message', 'retry_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(CalendarEventTypeCategory)
class CalendarEventTypeCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'order', 'active', 'created_at']
    list_filter = ['active', 'color']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['order', 'name']


@admin.register(CalendarEventTypeExtension)
class CalendarEventTypeExtensionAdmin(admin.ModelAdmin):
    list_display = ['event_type', 'category', 'is_featured', 'order_in_category']
    list_filter = ['is_featured', 'category']
    search_fields = ['event_type__name']
    ordering = ['order_in_category']


@admin.register(CalendarEmailTemplate)
class CalendarEmailTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'template_type', 'language', 'is_default', 'active', 
        'created_by', 'created_at'
    ]
    list_filter = ['template_type', 'language', 'is_default', 'active', 'created_at']
    search_fields = ['name', 'subject_template']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Template Information', {
            'fields': ('name', 'template_type', 'language', 'created_by')
        }),
        ('Email Content', {
            'fields': ('subject_template', 'body_html_template', 'body_text_template')
        }),
        ('Settings', {
            'fields': ('active', 'is_default')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')
    
    actions = ['make_default', 'make_active', 'make_inactive', 'preview_template']
    
    def make_default(self, request, queryset):
        for template in queryset:
            # Make this template default (will handle uniqueness in save method)
            template.is_default = True
            template.save()
        self.message_user(request, f"{queryset.count()} templates marked as default")
    make_default.short_description = "Mark selected templates as default"
    
    def make_active(self, request, queryset):
        queryset.update(active=True)
        self.message_user(request, f"{queryset.count()} templates activated")
    make_active.short_description = "Activate selected templates"
    
    def make_inactive(self, request, queryset):
        queryset.update(active=False)
        self.message_user(request, f"{queryset.count()} templates deactivated")
    make_inactive.short_description = "Deactivate selected templates"


@admin.register(CalendarEmailLog)
class CalendarEmailLogAdmin(admin.ModelAdmin):
    list_display = [
        'subject', 'recipient_email', 'template', 'event_name', 
        'status', 'sent_at', 'opens_count', 'clicks_count'
    ]
    list_filter = ['status', 'sent_at', 'created_at', 'template__template_type']
    search_fields = ['recipient_email', 'recipient_name', 'subject', 'event__name']
    readonly_fields = [
        'template', 'event', 'recipient_email', 'recipient_name',
        'subject', 'body_html', 'body_text', 'sent_at', 'error_message',
        'email_provider_id', 'opens_count', 'clicks_count', 'created_at', 'updated_at'
    ]
    date_hierarchy = 'sent_at'
    
    fieldsets = (
        ('Email Details', {
            'fields': ('template', 'event', 'recipient_email', 'recipient_name', 'subject')
        }),
        ('Status', {
            'fields': ('status', 'sent_at', 'error_message', 'email_provider_id')
        }),
        ('Content', {
            'fields': ('body_html', 'body_text'),
            'classes': ('collapse',)
        }),
        ('Tracking', {
            'fields': ('opens_count', 'clicks_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def event_name(self, obj):
        return obj.event.name if obj.event else '-'
    event_name.short_description = 'Event'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('template', 'event')
    
    def has_add_permission(self, request):
        # Don't allow manual creation of email logs
        return False
    
    def has_change_permission(self, request, obj=None):
        # Don't allow editing of email logs
        return False


# Custom admin site configuration
admin.site.site_header = 'Linguify Calendar Administration'
admin.site.site_title = 'Calendar Admin'
admin.site.index_title = 'Welcome to Calendar Administration'