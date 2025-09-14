from rest_framework import serializers


class TodoSettingsSerializer(serializers.Serializer):
    """Settings for the Todo & Productivity app"""
    
    # View preferences
    default_project_view = serializers.ChoiceField(
        choices=[('list', 'List'), ('kanban', 'Kanban'), ('calendar', 'Calendar'), ('timeline', 'Timeline')],
        default='list'
    )
    default_task_view = serializers.ChoiceField(
        choices=[('list', 'List'), ('priority', 'Priority'), ('due_date', 'Due Date'), ('project', 'Project')],
        default='list'
    )
    
    # Task settings
    auto_archive_completed = serializers.BooleanField(default=False)
    auto_archive_days = serializers.IntegerField(default=30, min_value=1, max_value=365)
    auto_delete_archived = serializers.BooleanField(default=False)
    auto_delete_archive_days = serializers.IntegerField(default=30, min_value=1, max_value=365)
    show_subtask_count = serializers.BooleanField(default=True)
    show_progress_bars = serializers.BooleanField(default=True)
    
    # Notification settings
    enable_reminders = serializers.BooleanField(default=True)
    reminder_minutes_before = serializers.IntegerField(default=15, min_value=1, max_value=1440)
    daily_digest = serializers.BooleanField(default=True)
    daily_digest_time = serializers.TimeField(default='09:00:00')
    overdue_notifications = serializers.BooleanField(default=True)
    
    # Productivity settings
    enable_time_tracking = serializers.BooleanField(default=False)
    pomodoro_timer = serializers.BooleanField(default=False)
    pomodoro_duration = serializers.IntegerField(default=25, min_value=5, max_value=60)
    break_duration = serializers.IntegerField(default=5, min_value=1, max_value=30)
    
    # Interface settings
    theme = serializers.ChoiceField(
        choices=[('light', 'Light'), ('dark', 'Dark'), ('auto', 'Auto')],
        default='auto'
    )
    compact_mode = serializers.BooleanField(default=False)
    show_completed_tasks = serializers.BooleanField(default=True)
    quick_add_shortcut = serializers.BooleanField(default=True)
    
    # Default values
    default_task_priority = serializers.ChoiceField(
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')],
        default='medium'
    )
    default_reminder_time = serializers.TimeField(default='09:00:00')
    
    # Collaboration settings
    allow_task_sharing = serializers.BooleanField(default=True)
    allow_project_sharing = serializers.BooleanField(default=True)
    public_templates = serializers.BooleanField(default=False)
    
    # Data settings
    backup_frequency = serializers.ChoiceField(
        choices=[('never', 'Never'), ('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')],
        default='weekly'
    )
    export_format = serializers.ChoiceField(
        choices=[('json', 'JSON'), ('csv', 'CSV'), ('pdf', 'PDF')],
        default='json'
    )


class TodoUserPreferencesSerializer(serializers.Serializer):
    """User-specific preferences for the Todo app"""
    
    # Quick filters
    favorite_filters = serializers.ListField(
        child=serializers.CharField(max_length=50),
        default=list,
        help_text="List of favorite filter combinations"
    )
    
    # Recent items
    recent_projects = serializers.ListField(
        child=serializers.UUIDField(),
        default=list,
        help_text="List of recently accessed project IDs"
    )
    recent_tags = serializers.ListField(
        child=serializers.UUIDField(),
        default=list,
        help_text="List of recently used tag IDs"
    )
    
    # Dashboard widgets
    dashboard_widgets = serializers.ListField(
        child=serializers.CharField(max_length=50),
        default=['today_tasks', 'overdue_tasks', 'upcoming_deadlines', 'progress_overview'],
        help_text="List of enabled dashboard widgets"
    )
    
    # Keyboard shortcuts
    enable_shortcuts = serializers.BooleanField(default=True)
    custom_shortcuts = serializers.DictField(
        child=serializers.CharField(max_length=50),
        default=dict,
        help_text="Custom keyboard shortcuts mapping"
    )
    
    # Templates
    favorite_templates = serializers.ListField(
        child=serializers.UUIDField(),
        default=list,
        help_text="List of favorite template IDs"
    )
    
    # Analytics preferences
    track_time_spent = serializers.BooleanField(default=True)
    track_productivity_metrics = serializers.BooleanField(default=True)
    show_productivity_insights = serializers.BooleanField(default=True)