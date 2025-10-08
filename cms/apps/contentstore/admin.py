"""
Content store admin configuration following OpenEdX patterns.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    CourseAsset, CourseContent, CourseSettings, ContentLibrary,
    CMSUnit, CMSChapter, CMSLesson, CMSContentLesson, 
    CMSVocabularyList, CMSVocabularyWord, CMSTheoryContent
)


@admin.register(CourseAsset)
class CourseAssetAdmin(admin.ModelAdmin):
    list_display = [
        'display_name', 
        'asset_type', 
        'file_size_display', 
        'course_id', 
        'is_locked',
        'sync_status',
        'created_at'
    ]
    list_filter = [
        'asset_type', 
        'is_locked', 
        'sync_status', 
        'created_at',
        'content_type'
    ]
    search_fields = [
        'display_name', 
        'description', 
        'course_id',
        'uploaded_by__username'
    ]
    readonly_fields = [
        'asset_key',
        'file_size',
        'content_type',
        'backend_id',
        'last_sync_success',
        'created_at',
        'updated_at',
        'preview_image'
    ]
    
    fieldsets = (
        ('Asset Information', {
            'fields': ('display_name', 'description', 'asset_type', 'is_locked')
        }),
        ('File Details', {
            'fields': ('file_path', 'thumbnail', 'preview_image', 'content_type', 'file_size', 'asset_key'),
            'classes': ('collapse',)
        }),
        ('Course Association', {
            'fields': ('course_id', 'usage_locations', 'uploaded_by')
        }),
        ('Sync Information', {
            'fields': ('sync_status', 'backend_id', 'last_sync_success', 'sync_error'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def preview_image(self, obj):
        """Show image preview in admin."""
        if obj.is_image() and obj.file_path:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px;" />',
                obj.file_path.url
            )
        return "No preview available"
    preview_image.short_description = "Preview"
    
    def file_size_display(self, obj):
        """Display file size in human readable format."""
        return obj.file_size_display
    file_size_display.short_description = "File Size"
    file_size_display.admin_order_field = 'file_size'


@admin.register(CourseContent)
class CourseContentAdmin(admin.ModelAdmin):
    list_display = [
        'display_name',
        'content_type', 
        'course_id',
        'is_draft',
        'visibility',
        'sync_status',
        'version',
        'last_modified_by',
        'updated_at'
    ]
    list_filter = [
        'content_type',
        'is_draft',
        'visibility', 
        'sync_status',
        'created_at'
    ]
    search_fields = [
        'display_name',
        'course_id', 
        'usage_key',
        'author__username'
    ]
    readonly_fields = [
        'content_id',
        'backend_id',
        'last_sync_success',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Content Information', {
            'fields': ('display_name', 'content_type', 'usage_key', 'parent_usage_key')
        }),
        ('Course Association', {
            'fields': ('course_id', 'author', 'last_modified_by')
        }),
        ('Content Data', {
            'fields': ('data', 'metadata'),
            'classes': ('collapse',)
        }),
        ('Publishing', {
            'fields': ('is_draft', 'visibility', 'start_date', 'end_date', 'version')
        }),
        ('Sync Information', {
            'fields': ('sync_status', 'backend_id', 'last_sync_success', 'sync_error'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('content_id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CourseSettings)
class CourseSettingsAdmin(admin.ModelAdmin):
    list_display = [
        'display_name',
        'course_id',
        'language',
        'start_date',
        'end_date',
        'updated_at'
    ]
    list_filter = [
        'language',
        'start_date',
        'end_date',
        'created_at'
    ]
    search_fields = [
        'display_name',
        'course_id',
        'short_description'
    ]
    readonly_fields = [
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('course_id', 'display_name', 'short_description', 'overview')
        }),
        ('Course Details', {
            'fields': ('language', 'effort', 'course_image')
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date', 'enrollment_start', 'enrollment_end')
        }),
        ('Advanced Settings', {
            'fields': ('advanced_settings', 'grading_policy'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ContentLibrary)
class ContentLibraryAdmin(admin.ModelAdmin):
    list_display = [
        'display_name',
        'library_key',
        'library_type',
        'version',
        'allow_public_learning',
        'sync_status',
        'created_at'
    ]
    list_filter = [
        'library_type',
        'allow_public_learning',
        'allow_public_read',
        'sync_status',
        'created_at'
    ]
    search_fields = [
        'display_name',
        'library_key',
        'description'
    ]
    readonly_fields = [
        'bundle_uuid',
        'backend_id',
        'last_sync_success',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Library Information', {
            'fields': ('display_name', 'library_key', 'description', 'library_type')
        }),
        ('Access Control', {
            'fields': ('allow_public_learning', 'allow_public_read')
        }),
        ('Versioning', {
            'fields': ('version', 'bundle_uuid')
        }),
        ('Sync Information', {
            'fields': ('sync_status', 'backend_id', 'last_sync_success', 'sync_error'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Customize admin site header
admin.site.site_header = "Linguify CMS Administration"
admin.site.site_title = "Linguify CMS Admin"
admin.site.index_title = "Content Management System"