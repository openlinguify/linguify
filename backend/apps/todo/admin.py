from django.contrib import admin
from django.utils.html import format_html
from .models import Project, Task, Note, Category, Tag, Reminder, TaskTemplate


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'color_display', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    def color_display(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 2px 8px; border-radius: 3px; color: white;">{}</span>',
            obj.color,
            obj.color
        )
    color_display.short_description = 'Color'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'color_display', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'user__username']
    readonly_fields = ['created_at']
    
    def color_display(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 2px 8px; border-radius: 3px; color: white;">#{}</span>',
            obj.color,
            obj.name
        )
    color_display.short_description = 'Tag'


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'status', 'progress_display', 'task_count_display', 'due_date', 'is_favorite']
    list_filter = ['status', 'is_favorite', 'is_shared', 'created_at', 'due_date']
    search_fields = ['name', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'progress_percentage', 'completed_at']
    filter_horizontal = []
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'user', 'category')
        }),
        ('Status & Progress', {
            'fields': ('status', 'progress_percentage', 'default_view')
        }),
        ('Dates', {
            'fields': ('start_date', 'due_date', 'completed_at')
        }),
        ('Settings', {
            'fields': ('is_shared', 'is_favorite')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def progress_display(self, obj):
        color = 'green' if obj.progress_percentage >= 80 else 'orange' if obj.progress_percentage >= 50 else 'red'
        return format_html(
            '<div style="width: 100px; background-color: #f0f0f0; border-radius: 3px;">'
            '<div style="width: {}%; background-color: {}; height: 20px; border-radius: 3px; text-align: center; color: white; line-height: 20px;">{}'
            '</div></div>',
            obj.progress_percentage,
            color,
            f'{obj.progress_percentage}%'
        )
    progress_display.short_description = 'Progress'
    
    def task_count_display(self, obj):
        return f"{obj.completed_task_count}/{obj.task_count}"
    task_count_display.short_description = 'Tasks'


class SubTaskInline(admin.TabularInline):
    model = Task
    fk_name = 'parent_task'
    extra = 0
    fields = ['title', 'status', 'priority', 'due_date', 'progress_percentage']
    readonly_fields = ['progress_percentage']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'project', 'status', 'priority', 'progress_display', 'due_date', 'is_overdue_display', 'is_important']
    list_filter = ['status', 'priority', 'is_important', 'is_recurring', 'created_at', 'due_date']
    search_fields = ['title', 'description', 'user__username', 'project__name']
    readonly_fields = ['created_at', 'updated_at', 'completed_at', 'is_overdue']
    filter_horizontal = ['tags']
    inlines = [SubTaskInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'user', 'project', 'parent_task')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority', 'progress_percentage')
        }),
        ('Organization', {
            'fields': ('tags', 'order')
        }),
        ('Dates', {
            'fields': ('start_date', 'due_date', 'completed_at')
        }),
        ('Time Tracking', {
            'fields': ('estimated_time', 'actual_time')
        }),
        ('Settings', {
            'fields': ('is_important', 'is_recurring', 'reminder_set')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def progress_display(self, obj):
        color = 'green' if obj.progress_percentage >= 80 else 'orange' if obj.progress_percentage >= 50 else 'red'
        return format_html(
            '<div style="width: 80px; background-color: #f0f0f0; border-radius: 3px;">'
            '<div style="width: {}%; background-color: {}; height: 15px; border-radius: 3px;"></div>'
            '</div>{}%',
            obj.progress_percentage,
            color,
            obj.progress_percentage
        )
    progress_display.short_description = 'Progress'
    
    def is_overdue_display(self, obj):
        if obj.is_overdue:
            return format_html('<span style="color: red; font-weight: bold;">⚠ Overdue</span>')
        return '✓'
    is_overdue_display.short_description = 'Status'


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'project', 'task', 'content_type', 'is_favorite', 'is_pinned', 'updated_at']
    list_filter = ['content_type', 'is_favorite', 'is_pinned', 'created_at']
    search_fields = ['title', 'content', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['tags']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'content', 'content_type', 'user')
        }),
        ('Attachments', {
            'fields': ('project', 'task')
        }),
        ('Organization', {
            'fields': ('tags', 'is_favorite', 'is_pinned')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'reminder_type', 'remind_at', 'is_sent', 'sent_at']
    list_filter = ['reminder_type', 'is_sent', 'remind_at', 'created_at']
    search_fields = ['title', 'message', 'user__username']
    readonly_fields = ['created_at', 'sent_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'message', 'user', 'reminder_type')
        }),
        ('Attachments', {
            'fields': ('task', 'project')
        }),
        ('Timing', {
            'fields': ('remind_at', 'is_sent', 'sent_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(TaskTemplate)
class TaskTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'is_public', 'is_featured', 'usage_count', 'created_at']
    list_filter = ['is_public', 'is_featured', 'created_at']
    search_fields = ['name', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'usage_count']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'user')
        }),
        ('Template Data', {
            'fields': ('template_data',)
        }),
        ('Settings', {
            'fields': ('is_public', 'is_featured')
        }),
        ('Statistics', {
            'fields': ('usage_count',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )