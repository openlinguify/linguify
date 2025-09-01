from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.html import strip_tags
import uuid
import re

User = get_user_model()


class PersonalStageType(models.Model):
    """Personal task stages - inspired by Open Linguify's personal_stage_type_id"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='personal_stages')
    name = models.CharField(max_length=50)
    sequence = models.IntegerField(default=10)
    fold = models.BooleanField(default=False, help_text="Fold this stage in kanban view")
    color = models.CharField(max_length=7, default='#6c757d')
    is_closed = models.BooleanField(default=False, help_text="Tasks in this stage are considered closed")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Personal Stage'
        verbose_name_plural = 'Personal Stages'
        unique_together = ['user', 'name']
        ordering = ['sequence', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.user.username})"
    
    @classmethod
    def create_default_stages(cls, user):
        """Create default stages for new users - Open Linguify inspired onboarding"""
        default_stages = [
            {'name': 'To Do', 'sequence': 1, 'color': '#6c757d', 'is_closed': False, 'fold': False},
            {'name': 'In Progress', 'sequence': 2, 'color': '#007bff', 'is_closed': False, 'fold': False},
            {'name': 'Waiting', 'sequence': 3, 'color': '#ffc107', 'is_closed': False, 'fold': False},
            {'name': 'Done', 'sequence': 4, 'color': '#28a745', 'is_closed': True, 'fold': False},
            {'name': 'Archive', 'sequence': 5, 'color': '#6f42c1', 'is_closed': True, 'fold': True},
        ]
        
        stages = []
        for stage_data in default_stages:
            stage, created = cls.objects.get_or_create(
                user=user,
                name=stage_data['name'],
                defaults=stage_data
            )
            stages.append(stage)
        return stages


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
    """Individual tasks - inspired by Open Linguify's project.task"""
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('0', 'Normal'),
        ('1', 'Starred'),  # Open Linguify-style priority (0=normal, 1=starred)
    ]
    
    STATE_CHOICES = [
        ('1_draft', 'Draft'),
        ('1_todo', 'To Do'),
        ('1_in_progress', 'In Progress'),
        ('1_done', 'Done'),
        ('1_canceled', 'Canceled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='todo_tasks')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks', null=True, blank=True)
    parent_task = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subtasks')
    
    # Personal stages - Open Linguify inspired
    personal_stage_type = models.ForeignKey(
        PersonalStageType, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='tasks'
    )
    
    # Basic info
    title = models.CharField(max_length=200, blank=True)  # Allow blank for auto-generation
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='1_todo')  # Open Linguify style state
    priority = models.CharField(max_length=1, choices=PRIORITY_CHOICES, default='0')
    
    # Color for kanban cards
    color = models.IntegerField(default=0, help_text="Color index for kanban cards (0-11)")
    
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
    active = models.BooleanField(default=True)  # Open Linguify style active field
    sequence = models.IntegerField(default=10)  # For ordering within stages
    
    class Meta:
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        ordering = ['state', '-priority', 'due_date', 'sequence', 'id']
    
    def __str__(self):
        return self.title or 'Untitled Task'
    
    def save(self, *args, **kwargs):
        """Override save to implement Open Linguify-style auto-naming"""
        # Auto-generate title from description if empty (Open Linguify inspired)
        if not self.title and self.description:
            # Extract first line from description, clean it up
            text = strip_tags(self.description).strip()
            # Remove markdown-style formatting
            text = re.sub(r'[*_`#]', '', text)
            # Get first line
            first_line = text.partition('\n')[0]
            if first_line:
                # Truncate if too long
                self.title = (first_line[:97] + '...') if len(first_line) > 100 else first_line
            else:
                self.title = 'Untitled Task'
        elif not self.title:
            self.title = 'Untitled Task'
        
        # Set personal stage if not set
        if not self.personal_stage_type and self.user:
            default_stage = self.user.personal_stages.filter(name='To Do').first()
            if not default_stage:
                # Create default stages if they don't exist
                PersonalStageType.create_default_stages(self.user)
                default_stage = self.user.personal_stages.filter(name='To Do').first()
            self.personal_stage_type = default_stage
        
        # Sync state with personal stage (only for new tasks or when stage changes)
        if self.personal_stage_type and not self.pk:  # Only for new tasks
            if self.personal_stage_type.is_closed:
                self.state = '1_done'
                self.status = 'completed'
        
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        if self.due_date and self.state not in ('1_done', '1_canceled'):
            return timezone.now() > self.due_date
        return False
    
    @property
    def is_closed(self):
        """Check if task is in a closed state"""
        return self.state in ('1_done', '1_canceled') or (
            self.personal_stage_type and self.personal_stage_type.is_closed
        )
    
    @property
    def subtask_count(self):
        return self.subtasks.count()
    
    @property
    def completed_subtask_count(self):
        return self.subtasks.filter(state='1_done').count()
    
    @property
    def name_with_subtask_count(self):
        """Open Linguify-style title with subtask count"""
        subtask_count = self.subtask_count
        if subtask_count > 0:
            return f"{self.title} ({subtask_count})"
        return self.title
    
    def toggle_state(self):
        """Toggle between done and todo states - Open Linguify style"""
        if self.state == '1_done':
            # Move to todo state
            self.state = '1_todo'
            self.status = 'todo'
            self.completed_at = None
            self.progress_percentage = 0
            
            # Move to first non-closed stage (usually "To Do")
            if self.user:
                first_stage = self.user.personal_stages.filter(is_closed=False).order_by('sequence').first()
                if first_stage:
                    self.personal_stage_type = first_stage
        else:
            # Move to done state
            self.state = '1_done'
            self.status = 'completed'
            self.completed_at = timezone.now()
            self.progress_percentage = 100
            
            # Move to "Done" stage (closed stage)
            if self.user:
                done_stage = self.user.personal_stages.filter(is_closed=True).order_by('sequence').first()
                if not done_stage:
                    # Try to find by name if no closed stage exists
                    done_stage = self.user.personal_stages.filter(name__iexact='Done').first()
                if done_stage:
                    self.personal_stage_type = done_stage
        
        self.save()
        
        # Update project progress if task belongs to a project
        if self.project:
            self.project.update_progress()
    
    def mark_completed(self):
        """Mark task as completed and update timestamps"""
        self.state = '1_done'
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.progress_percentage = 100
        self.save()
        
        # Update project progress if task belongs to a project
        if self.project:
            self.project.update_progress()
    
    def mark_incomplete(self):
        """Mark task as incomplete"""
        self.state = '1_todo'
        self.status = 'todo'
        self.completed_at = None
        self.save()
        
        # Update project progress if task belongs to a project
        if self.project:
            self.project.update_progress()
    
    @classmethod
    def ensure_onboarding_todo(cls, user):
        """Create onboarding todo for new users - Open Linguify inspired"""
        if user.todo_tasks.filter(title__icontains='Welcome').exists():
            return  # Already has onboarding todo
        
        # Create onboarding task
        welcome_title = f"Welcome {user.first_name or user.username}!"
        welcome_description = f"""
        <h3>🎉 Welcome to your personal Todo app!</h3>
        <p>This is your first task. Here's how to get started:</p>
        <ul>
            <li>✅ <strong>Mark tasks as done</strong> by clicking the checkmark</li>
            <li>📋 <strong>Create new tasks</strong> with the "New Task" button</li>
            <li>🏷️ <strong>Organize with tags</strong> and personal stages</li>
            <li>📅 <strong>Set due dates</strong> to stay on track</li>
            <li>⭐ <strong>Star important tasks</strong> to prioritize them</li>
        </ul>
        <p>Try marking this welcome task as done when you're ready to start!</p>
        """
        
        # Ensure user has personal stages
        PersonalStageType.create_default_stages(user)
        
        cls.objects.create(
            user=user,
            title=welcome_title,
            description=welcome_description,
            priority='1',  # Starred
            state='1_todo'
        )
    
    @classmethod
    def get_todo_views_data(cls):
        """Return view configuration for different todo views - Open Linguify inspired"""
        return {
            'kanban': {
                'default_group_by': 'personal_stage_type',
                'highlight_color': 'color',
                'sample_data': True,
            },
            'list': {
                'editable': 'bottom',
                'multi_edit': True,
                'open_form_view': True,
            },
            'form': {
                'js_class': 'todo_form',
            },
            'activity': {
                'string': 'To-dos',
            }
        }


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