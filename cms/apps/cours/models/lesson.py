# -*- coding: utf-8 -*-
"""
Course Lesson and Content models
Individual lessons with various content types
"""
from django.db import models
from django.core.validators import FileExtensionValidator
import uuid

from cms.core.models import SyncableModel, MultilingualMixin
from .course import Course
from .section import CourseSection


class CourseLesson(SyncableModel, MultilingualMixin):
    """
    Individual lesson within a course section.
    Can contain multiple content blocks.
    """

    LESSON_TYPE_CHOICES = [
        ('video', '🎥 Video'),
        ('text', '📄 Article/Text'),
        ('quiz', '❓ Quiz'),
        ('exercise', '✏️ Exercise'),
        ('coding', '💻 Coding Exercise'),
        ('project', '🚀 Project'),
        ('discussion', '💬 Discussion'),
        ('live', '📡 Live Session'),
        ('assignment', '📝 Assignment'),
        ('resource', '📎 Downloadable Resource'),
    ]

    lesson_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons'
    )

    section = models.ForeignKey(
        CourseSection,
        on_delete=models.CASCADE,
        related_name='lessons'
    )

    # Multilingual fields
    title_en = models.CharField(max_length=200)
    title_fr = models.CharField(max_length=200)
    title_es = models.CharField(max_length=200)
    title_nl = models.CharField(max_length=200)

    description_en = models.TextField(blank=True)
    description_fr = models.TextField(blank=True)
    description_es = models.TextField(blank=True)
    description_nl = models.TextField(blank=True)

    # Lesson metadata
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPE_CHOICES, default='video')
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    is_preview = models.BooleanField(
        default=False,
        help_text="Can be previewed before enrollment"
    )

    # Duration
    duration_minutes = models.PositiveIntegerField(
        default=0,
        help_text="Lesson duration in minutes"
    )

    # Content (can be extended with CourseContent)
    video_url = models.URLField(blank=True, help_text="Video URL (YouTube, Vimeo, etc.)")
    video_file = models.FileField(
        upload_to='courses/videos/',
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'webm', 'mov'])]
    )

    # Completion tracking
    is_completable = models.BooleanField(
        default=True,
        help_text="Can be marked as complete"
    )
    requires_previous = models.BooleanField(
        default=True,
        help_text="Requires previous lessons to be completed"
    )

    class Meta:
        db_table = 'cms_course_lessons'
        ordering = ['course', 'section', 'order']
        unique_together = ['section', 'order']

    def __str__(self):
        return f"Lesson {self.order}: {self.get_localized_field('title', 'fr')}"

    @property
    def title(self):
        return self.get_localized_field('title', 'fr')

    @property
    def description(self):
        return self.get_localized_field('description', 'fr')

    def move_up(self):
        """Move lesson up in order within section."""
        if self.order > 0:
            previous = CourseLesson.objects.filter(
                section=self.section,
                order=self.order - 1
            ).first()

            if previous:
                previous.order, self.order = self.order, previous.order
                previous.save()
                self.save()

    def move_down(self):
        """Move lesson down in order within section."""
        next_lesson = CourseLesson.objects.filter(
            section=self.section,
            order=self.order + 1
        ).first()

        if next_lesson:
            next_lesson.order, self.order = self.order, next_lesson.order
            next_lesson.save()
            self.save()


class CourseContent(SyncableModel):
    """
    Content blocks within a lesson.
    Allows multiple content types in a single lesson.
    """

    CONTENT_TYPE_CHOICES = [
        ('text', '📄 Rich Text'),
        ('video', '🎥 Video'),
        ('audio', '🎵 Audio'),
        ('image', '🖼️ Image'),
        ('pdf', '📑 PDF Document'),
        ('code', '💻 Code Block'),
        ('quiz', '❓ Quiz'),
        ('exercise', '✏️ Interactive Exercise'),
        ('embed', '🔗 Embedded Content'),
        ('file', '📎 File Download'),
    ]

    content_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    lesson = models.ForeignKey(
        CourseLesson,
        on_delete=models.CASCADE,
        related_name='content_blocks'
    )

    # Content metadata
    title = models.CharField(max_length=200, blank=True)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES)
    order = models.PositiveIntegerField(default=0)

    # Content data (flexible JSON structure)
    content_data = models.JSONField(
        default=dict,
        help_text="Content data structure varies by type"
    )

    # Text content (for text/rich text types)
    text_content = models.TextField(blank=True)

    # Media files
    media_file = models.FileField(upload_to='courses/content/', blank=True)
    media_url = models.URLField(blank=True)

    # Duration (for video/audio)
    duration_seconds = models.PositiveIntegerField(default=0)

    # Visibility
    is_published = models.BooleanField(default=True)

    class Meta:
        db_table = 'cms_course_content'
        ordering = ['lesson', 'order']
        unique_together = ['lesson', 'order']

    def __str__(self):
        return f"{self.title or 'Content'} ({self.get_content_type_display()})"
