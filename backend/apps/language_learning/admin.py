from django.contrib import admin
from .models import LanguagelearningItem


@admin.register(LanguagelearningItem)
class LanguagelearningItemAdmin(admin.ModelAdmin):
    """Administration des items Language Learning"""
    
    list_display = ['title', 'user', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    list_per_page = 25
    
    fieldsets = (
        (None, {
            'fields': ('user', 'title', 'description', 'is_active')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
