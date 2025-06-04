# app_manager/admin.py
from django.contrib import admin
from .models import App, UserAppSettings

@admin.register(App)
class AppAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'code', 'is_enabled', 'order', 'created_at']
    list_filter = ['is_enabled', 'created_at']
    search_fields = ['display_name', 'code', 'description']
    ordering = ['order', 'display_name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'display_name', 'description')
        }),
        ('Appearance', {
            'fields': ('icon_name', 'color', 'route_path')
        }),
        ('Settings', {
            'fields': ('is_enabled', 'order')
        }),
    )

@admin.register(UserAppSettings)
class UserAppSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_enabled_apps_count', 'created_at']
    list_filter = ['created_at', 'enabled_apps']
    search_fields = ['user__username', 'user__email']
    filter_horizontal = ['enabled_apps']
    
    def get_enabled_apps_count(self, obj):
        return obj.enabled_apps.count()
    get_enabled_apps_count.short_description = 'Enabled Apps Count'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user').prefetch_related('enabled_apps')