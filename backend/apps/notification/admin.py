# backend/apps/notification/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Q

from .models import Notification, NotificationSetting, NotificationDevice

class ExpirationFilter(admin.SimpleListFilter):
    """
    Filter for notification expiration status
    """
    title = 'Expiration'
    parameter_name = 'expiration'
    
    def lookups(self, request, model_admin):
        return (
            ('expired', 'Expired'),
            ('active', 'Active'),
            ('none', 'No expiration'),
        )
    
    def queryset(self, request, queryset):
        now = timezone.now()
        
        if self.value() == 'expired':
            return queryset.filter(expires_at__lt=now)
        elif self.value() == 'active':
            return queryset.filter(Q(expires_at__gt=now) | Q(expires_at__isnull=False))
        elif self.value() == 'none':
            return queryset.filter(expires_at__isnull=True)

class NotificationTypeFilter(admin.SimpleListFilter):
    """
    Filter for notification types
    """
    title = 'Type'
    parameter_name = 'type'
    
    def lookups(self, request, model_admin):
        from .models import NotificationType
        return NotificationType.choices
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(type=self.value())

class NotificationPriorityFilter(admin.SimpleListFilter):
    """
    Filter for notification priorities
    """
    title = 'Priority'
    parameter_name = 'priority'
    
    def lookups(self, request, model_admin):
        from .models import NotificationPriority
        return NotificationPriority.choices
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(priority=self.value())

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Admin configuration for Notification model
    """
    list_display = ('id', 'colored_type', 'user_display', 'title', 'priority_display', 
                    'is_read', 'created_at', 'expiration_status')
    list_filter = ('is_read', NotificationTypeFilter, NotificationPriorityFilter, 
                   ExpirationFilter, 'created_at')
    search_fields = ('title', 'message', 'user__username', 'user__email')
    readonly_fields = ('id', 'created_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'type', 'priority', 'is_read')
        }),
        ('Content', {
            'fields': ('title', 'message', 'data')
        }),
        ('Timing', {
            'fields': ('created_at', 'expires_at')
        })
    )
    actions = ['mark_as_read', 'mark_as_unread']
    
    def user_display(self, obj):
        """
        Display user with email
        """
        return f"{obj.user.username} ({obj.user.email})"
    user_display.short_description = 'User'
    
    def colored_type(self, obj):
        """
        Color-code notification types
        """
        colors = {
            'info': 'blue',
            'success': 'green',
            'warning': 'orange',
            'error': 'red',
            'lesson_reminder': 'purple',
            'flashcard': 'teal',
            'streak': 'gold',
            'achievement': 'indigo',
            'system': 'gray',
            'progress': 'lime',
        }
        
        color = colors.get(obj.type, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_type_display()
        )
    colored_type.short_description = 'Type'
    
    def priority_display(self, obj):
        """
        Display priority with colors
        """
        colors = {
            'low': 'gray',
            'medium': 'blue',
            'high': 'red',
        }
        
        color = colors.get(obj.priority, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_priority_display()
        )
    priority_display.short_description = 'Priority'
    
    def expiration_status(self, obj):
        """
        Show expiration status
        """
        if not obj.expires_at:
            return format_html('<span style="color: gray;">No expiration</span>')
        
        now = timezone.now()
        if obj.expires_at < now:
            return format_html('<span style="color: red;">Expired</span>')
        
        days_left = (obj.expires_at - now).days
        if days_left < 1:
            hours_left = int(((obj.expires_at - now).seconds) / 3600)
            return format_html(
                '<span style="color: orange;">Expires in {} hours</span>',
                hours_left
            )
        return format_html(
            '<span style="color: green;">Expires in {} days</span>',
            days_left
        )
    expiration_status.short_description = 'Expiration'
    
    def mark_as_read(self, request, queryset):
        """
        Mark selected notifications as read
        """
        count = queryset.update(is_read=True)
        self.message_user(
            request, 
            f"{count} notification{'s' if count != 1 else ''} marked as read."
        )
    mark_as_read.short_description = "Mark selected notifications as read"
    
    def mark_as_unread(self, request, queryset):
        """
        Mark selected notifications as unread
        """
        count = queryset.update(is_read=False)
        self.message_user(
            request, 
            f"{count} notification{'s' if count != 1 else ''} marked as unread."
        )
    mark_as_unread.short_description = "Mark selected notifications as unread"

@admin.register(NotificationSetting)
class NotificationSettingAdmin(admin.ModelAdmin):
    """
    Admin configuration for NotificationSetting model
    """
    list_display = ('user', 'email_enabled', 'push_enabled', 'web_enabled',
                    'quiet_hours_enabled', 'quiet_hours_display')
    list_filter = ('email_enabled', 'push_enabled', 'web_enabled',
                   'lesson_reminders', 'flashcard_reminders',
                   'achievement_notifications', 'streak_notifications',
                   'system_notifications', 'quiet_hours_enabled')
    search_fields = ('user__username', 'user__email')
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Channel Settings', {
            'fields': ('email_enabled', 'email_frequency', 'push_enabled', 'web_enabled')
        }),
        ('Notification Types', {
            'fields': ('lesson_reminders', 'flashcard_reminders',
                      'achievement_notifications', 'streak_notifications',
                      'system_notifications')
        }),
        ('Quiet Hours', {
            'fields': ('quiet_hours_enabled', 'quiet_hours_start', 'quiet_hours_end')
        })
    )
    
    def quiet_hours_display(self, obj):
        """
        Display quiet hours
        """
        if not obj.quiet_hours_enabled:
            return format_html('<span style="color: gray;">Disabled</span>')
        
        return format_html(
            '<span style="color: blue;">{} to {}</span>',
            obj.quiet_hours_start.strftime('%H:%M'),
            obj.quiet_hours_end.strftime('%H:%M')
        )
    quiet_hours_display.short_description = 'Quiet Hours'

@admin.register(NotificationDevice)
class NotificationDeviceAdmin(admin.ModelAdmin):
    """
    Admin configuration for NotificationDevice model
    """
    list_display = ('id', 'user', 'device_type', 'device_name', 'is_active',
                    'created_at', 'last_used')
    list_filter = ('device_type', 'is_active', 'created_at', 'last_used')
    search_fields = ('user__username', 'user__email', 'device_name')
    readonly_fields = ('created_at', 'last_used')
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'device_type', 'device_name', 'is_active')
        }),
        ('Technical Details', {
            'fields': ('device_token',)
        }),
        ('Timing', {
            'fields': ('created_at', 'last_used')
        })
    )
    actions = ['activate_devices', 'deactivate_devices']
    
    def activate_devices(self, request, queryset):
        """
        Activate selected devices
        """
        count = queryset.update(is_active=True)
        self.message_user(
            request, 
            f"{count} device{'s' if count != 1 else ''} activated."
        )
    activate_devices.short_description = "Activate selected devices"
    
    def deactivate_devices(self, request, queryset):
        """
        Deactivate selected devices
        """
        count = queryset.update(is_active=False)
        self.message_user(
            request, 
            f"{count} device{'s' if count != 1 else ''} deactivated."
        )
    deactivate_devices.short_description = "Deactivate selected devices"