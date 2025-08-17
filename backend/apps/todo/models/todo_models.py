from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid

User = get_user_model()


class Category(models.Model):
    """Categories for organizing projects and tasks"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='todo_categories')
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#007bff')  # Hex color
    icon = models.CharField(max_length=50, default='bi-folder')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        unique_together = ['user', 'name']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.user.username})"


class Tag(models.Model):
    """Tags for flexible organization"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='todo_tags')
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default='#6c757d')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        unique_together = ['user', 'name']
        ordering = ['name']
    
    def __str__(self):
        return f"#{self.name}"


class Project(models.Model):
    """Projects to group related tasks"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('archived', 'Archived'),
    ]
    
    VIEW_CHOICES = [
        ('list', 'List View'),
        ('kanban', 'Kanban Board'),
        ('calendar', 'Calendar View'),
        ('timeline', 'Timeline View'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='todo_projects')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    default_view = models.CharField(max_length=20, choices=VIEW_CHOICES, default='list')
    
    # Dates
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Settings
    is_shared = models.BooleanField(default=False)
    is_favorite = models.BooleanField(default=False)
    
    # Progress
    progress_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
        ordering = ['-is_favorite', '-updated_at']
    
    def __str__(self):
        return self.name
    
    @property
    def task_count(self):
        return self.tasks.count()
    
    @property
    def completed_task_count(self):
        return self.tasks.filter(status='completed').count()
    
    def update_progress(self):
        """Auto-calculate progress based on completed tasks"""
        total_tasks = self.task_count
        if total_tasks == 0:
            self.progress_percentage = 0
        else:
            completed_tasks = self.completed_task_count
            self.progress_percentage = int((completed_tasks / total_tasks) * 100)
        self.save(update_fields=['progress_percentage'])


class Task(models.Model):
    """Individual tasks"""
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='todo_tasks')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks', null=True, blank=True)
    parent_task = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subtasks')
    
    # Basic info
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Organization
    tags = models.ManyToManyField(Tag, blank=True, related_name='tasks')
    order = models.IntegerField(default=0)  # For custom ordering
    
    # Dates
    due_date = models.DateTimeField(null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Progress
    progress_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Time tracking
    estimated_time = models.IntegerField(null=True, blank=True, help_text="Estimated time in minutes")
    actual_time = models.IntegerField(null=True, blank=True, help_text="Actual time spent in minutes")
    
    # Settings
    is_important = models.BooleanField(default=False)
    is_recurring = models.BooleanField(default=False)
    reminder_set = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        ordering = ['-is_important', 'due_date', 'priority', 'order', '-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def is_overdue(self):
        if self.due_date and self.status != 'completed':
            return timezone.now() > self.due_date
        return False
    
    @property
    def subtask_count(self):
        return self.subtasks.count()
    
    @property
    def completed_subtask_count(self):
        return self.subtasks.filter(status='completed').count()
    
    def mark_completed(self):
        """Mark task as completed and update timestamps"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.progress_percentage = 100
        self.save()
        
        # Update project progress if task belongs to a project
        if self.project:
            self.project.update_progress()
    
    def mark_incomplete(self):
        """Mark task as incomplete"""
        self.status = 'todo'
        self.completed_at = None
        self.save()
        
        # Update project progress if task belongs to a project
        if self.project:
            self.project.update_progress()


class Note(models.Model):
    """Rich text notes that can be standalone or attached to tasks/projects"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='todo_notes')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='notes', null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='notes', null=True, blank=True)
    
    title = models.CharField(max_length=200)
    content = models.TextField()  # Rich text content (markdown or HTML)
    content_type = models.CharField(max_length=20, choices=[('markdown', 'Markdown'), ('html', 'HTML')], default='markdown')
    
    # Organization
    tags = models.ManyToManyField(Tag, blank=True, related_name='notes')
    is_favorite = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'
        ordering = ['-is_pinned', '-is_favorite', '-updated_at']
    
    def __str__(self):
        return self.title


class Reminder(models.Model):
    """Reminders for tasks and deadlines"""
    REMINDER_TYPES = [
        ('task_due', 'Task Due'),
        ('project_deadline', 'Project Deadline'),
        ('custom', 'Custom Reminder'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='todo_reminders')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='reminders', null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='reminders', null=True, blank=True)
    
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPES, default='custom')
    title = models.CharField(max_length=200)
    message = models.TextField(blank=True)
    
    # Timing
    remind_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Status
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Reminder'
        verbose_name_plural = 'Reminders'
        ordering = ['remind_at']
    
    def __str__(self):
        return f"Reminder: {self.title} at {self.remind_at}"


class TaskTemplate(models.Model):
    """Templates for common task workflows"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='todo_templates')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Template data (JSON structure)
    template_data = models.JSONField(default=dict)
    
    # Sharing
    is_public = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    # Stats
    usage_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Task Template'
        verbose_name_plural = 'Task Templates'
        ordering = ['-is_featured', '-usage_count', 'name']
    
    def __str__(self):
        return self.name