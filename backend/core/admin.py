# -*- coding: utf-8 -*-
# Part of Open Linguify. See LICENSE file for full copyright and licensing details.

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models.tags import Tag, TagRelation


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin interface for the global Tag model"""
    
    list_display = [
        'name', 'colored_name', 'user', 'usage_count_total',
        'usage_count_notebook', 'usage_count_todo', 'usage_count_calendar',
        'is_active', 'is_favorite', 'created_at'
    ]
    
    list_filter = [
        'is_active', 'is_favorite', 'created_at', 'updated_at'
    ]
    
    search_fields = [
        'name', 'user__username', 'user__email', 'description'
    ]
    
    ordering = ['user__username', 'name']
    
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'usage_count_total',
        'usage_count_notebook', 'usage_count_todo', 'usage_count_calendar',
        'usage_count_revision', 'usage_count_documents', 'usage_count_community'
    ]
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['user', 'name', 'description', 'color']
        }),
        ('Settings', {
            'fields': ['is_active', 'is_favorite']
        }),
        ('Usage Statistics', {
            'fields': [
                'usage_count_total', 'usage_count_notebook', 'usage_count_todo',
                'usage_count_calendar', 'usage_count_revision', 
                'usage_count_documents', 'usage_count_community'
            ],
            'classes': ['collapse']
        }),
        ('Metadata', {
            'fields': ['id', 'created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    
    actions = [
        'make_active', 'make_inactive', 'make_favorite', 'remove_favorite',
        'recalculate_usage_counts'
    ]
    
    def colored_name(self, obj):
        """Display tag name with its color"""
        return format_html(
            '<span style="display: inline-block; width: 12px; height: 12px; '
            'background-color: {}; border-radius: 50%; margin-right: 8px;"></span>{}',
            obj.color, obj.name
        )
    colored_name.short_description = 'Tag (colored)'
    colored_name.admin_order_field = 'name'
    
    def get_queryset(self, request):
        """Optimize queryset with related data"""
        return super().get_queryset(request).select_related('user').annotate(
            relations_count=Count('relations')
        )
    
    def make_active(self, request, queryset):
        """Mark selected tags as active"""
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} tags marked as active.')
    make_active.short_description = 'Mark selected tags as active'
    
    def make_inactive(self, request, queryset):
        """Mark selected tags as inactive"""
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} tags marked as inactive.')
    make_inactive.short_description = 'Mark selected tags as inactive'
    
    def make_favorite(self, request, queryset):
        """Mark selected tags as favorite"""
        count = queryset.update(is_favorite=True)
        self.message_user(request, f'{count} tags marked as favorite.')
    make_favorite.short_description = 'Mark selected tags as favorite'
    
    def remove_favorite(self, request, queryset):
        """Remove favorite status from selected tags"""
        count = queryset.update(is_favorite=False)
        self.message_user(request, f'{count} tags removed from favorites.')
    remove_favorite.short_description = 'Remove from favorites'
    
    def recalculate_usage_counts(self, request, queryset):
        """Recalculate usage counts for selected tags"""
        updated_count = 0
        for tag in queryset:
            tag.recalculate_usage_counts()
            updated_count += 1
        self.message_user(request, f'Usage counts recalculated for {updated_count} tags.')
    recalculate_usage_counts.short_description = 'Recalculate usage counts'


@admin.register(TagRelation)
class TagRelationAdmin(admin.ModelAdmin):
    """Admin interface for TagRelation model"""
    
    list_display = [
        'tag', 'app_name', 'model_name', 'object_id', 'created_by', 'created_at'
    ]
    
    list_filter = [
        'app_name', 'model_name', 'created_at'
    ]
    
    search_fields = [
        'tag__name', 'app_name', 'model_name', 'object_id',
        'created_by__username', 'created_by__email'
    ]
    
    ordering = ['-created_at']
    
    readonly_fields = ['id', 'created_at']
    
    raw_id_fields = ['tag', 'created_by']
    
    fieldsets = [
        ('Relation Information', {
            'fields': ['tag', 'app_name', 'model_name', 'object_id', 'created_by']
        }),
        ('Metadata', {
            'fields': ['id', 'created_at'],
            'classes': ['collapse']
        }),
    ]
    
    def get_queryset(self, request):
        """Optimize queryset with related data"""
        return super().get_queryset(request).select_related('tag', 'created_by')
    
    def has_add_permission(self, request):
        """TagRelations are typically created programmatically"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """TagRelations shouldn't be modified once created"""
        return False