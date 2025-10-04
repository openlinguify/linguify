# -*- coding: utf-8 -*-
# Part of Open Linguify. See LICENSE file for full copyright and licensing details.
from django.db import models
from apps.authentication.models import User
from django.conf import settings
from core.models.tags import Tag, get_tags_for_object, add_tag_to_object, remove_tag_from_object


def default_list():
    return []

class NoteCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='note_categories')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='subcategories')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
        unique_together = ['name', 'user', 'parent']

    def __str__(self):
        return self.name
    
# Les tags sont maintenant gérés par le système global dans core.models.tags

class Note(models.Model):
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ]
    TYPE_CHOICES = [
        ('NOTE', 'Note'),
        ('TASK', 'Task'),
        ('REMINDER', 'Reminder'),
        ('MEETING', 'Meeting'),
        ('IDEA', 'Idea'),
        ('PROJECT', 'Project'),
        ('VOCABULARY', 'Vocabulary'),
        ('GRAMMAR', 'Grammar'),
        ('EXPRESSION', 'Expression'),
        ('CULTURE', 'Culture'),
        ('EVENT', 'Event'),
        ('TEXT', 'Text'),
        ('IMAGE', 'Image'),
        ('VIDEO', 'Video')
    ]
    DIFFICULTY_CHOICES = [
        ('BEGINNER', 'Beginner'),
        ('INTERMEDIATE', 'Intermediate'),
        ('ADVANCED', 'Advanced'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, default="") # Make content optional with default empty string
    category = models.ForeignKey(NoteCategory, on_delete=models.SET_NULL, blank=True, null=True)
    # tags are now managed through the global tag system via TagRelation
    note_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='NOTE')
    
    # Language learning specific fields
    language = models.CharField(max_length=50, blank=True, null=True)
    translation = models.TextField(blank=True, null=True)
    pronunciation = models.CharField(max_length=255, blank=True, null=True)
    example_sentences = models.JSONField(default=default_list, blank=True)
    related_words = models.JSONField(default=default_list, blank=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, blank=True, null=True)

    # Metadata fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_reviewed_at = models.DateTimeField(blank=True, null=True)
    review_count = models.IntegerField(default=0)

    # organization fields
    is_pinned = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')

    class Meta:
        ordering = ['-is_pinned', '-updated_at', '-created_at'] # Pinned notes first, then by updated_at, then by created_at
        indexes = [
            models.Index(fields=['user', 'category']),
            models.Index(fields=['-updated_at']),
            models.Index(fields=['user', 'is_archived']),
            models.Index(fields=['user', 'is_pinned']),
            models.Index(fields=['user', 'last_reviewed_at']),
            models.Index(fields=['user', 'note_type']),
            models.Index(fields=['language']),
        ]

    def __str__(self):
        return self.title
    
    def mark_reviewed(self):
        from django.utils import timezone
        now = timezone.now()
        self.last_reviewed_at = now
        self.review_count += 1
        self.save()
    
    def _calculate_next_review_date(self, from_date=None):
        from django.utils import timezone
        from datetime import timedelta
        
        if from_date is None:
            from_date = timezone.now()
            
        # Intervalle de révision basé sur le nombre de révisions
        intervals = {
            0: timedelta(days=1),
            1: timedelta(days=3),
            2: timedelta(days=7),
            3: timedelta(days=14),
            4: timedelta(days=30),
            5: timedelta(days=60)
        }
        
        review_level = min(self.review_count, 5)
        return from_date + intervals[review_level]
    
    @property
    def tags(self):
        """Get tags for this note using the global tag system"""
        return get_tags_for_object('notebook', 'Note', self.id, self.user)
    
    def add_tag(self, tag):
        """Add a tag to this note using the global tag system"""
        return add_tag_to_object(tag, 'notebook', 'Note', self.id, self.user)
    
    def remove_tag(self, tag):
        """Remove a tag from this note using the global tag system"""
        return remove_tag_from_object(tag, 'notebook', 'Note', self.id)
    
    def set_tags(self, tags):
        """Set tags for this note using the global tag system"""
        # First remove all existing tags
        current_tags = self.tags
        for tag in current_tags:
            self.remove_tag(tag)
        # Then add new tags
        for tag in tags:
            self.add_tag(tag)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    @property
    def needs_review(self):
        """Détermine si la note doit être révisée basé sur la dernière révision"""
        from django.utils import timezone

        if not self.last_reviewed_at:
            return True

        next_review = self._calculate_next_review_date(self.last_reviewed_at)
        return timezone.now() >= next_review

    def convert_to_tasks(self, project=None):
        """
        Convert note content into tasks
        Parses content and creates tasks from:
        - Checkbox items: [ ] task or [x] completed task
        - Numbered lists: 1. task
        - Bullet points: - task or * task
        Returns list of created tasks
        """
        import re

        tasks = []
        lines = self.content.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            task_title = None
            is_completed = False

            # Check for checkbox format: [ ] or [x]
            checkbox_match = re.match(r'^\[([ xX])\]\s*(.+)$', line)
            if checkbox_match:
                is_completed = checkbox_match.group(1).lower() == 'x'
                task_title = checkbox_match.group(2).strip()

            # Check for numbered list: 1. task
            elif re.match(r'^\d+\.\s+(.+)$', line):
                numbered_match = re.match(r'^\d+\.\s+(.+)$', line)
                task_title = numbered_match.group(1).strip()

            # Check for bullet points: - task or * task
            elif re.match(r'^[-*]\s+(.+)$', line):
                bullet_match = re.match(r'^[-*]\s+(.+)$', line)
                task_title = bullet_match.group(1).strip()

            # Create task if we found a valid format
            if task_title:
                from apps.todo.models import Task

                task = Task.objects.create(
                    user=self.user,
                    title=task_title,
                    description=f"Created from note: {self.title}",
                    source_note=self,
                    project=project,
                    state='1_done' if is_completed else '1_todo',
                    status='completed' if is_completed else 'todo'
                )
                tasks.append(task)

        return tasks

class SharedNote(models.Model):
    """Modèle pour le partage de notes entre utilisateurs"""
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_notes')
    shared_at = models.DateTimeField(auto_now_add=True)
    can_edit = models.BooleanField(default=False)

    class Meta:
        unique_together = ['note', 'shared_with']

    def __str__(self):
        return f"{self.note.title} shared with {self.shared_with.username}"