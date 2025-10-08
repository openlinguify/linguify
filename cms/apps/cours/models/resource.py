# -*- coding: utf-8 -*-
"""
Course Resource model
Downloadable resources and materials
"""
from django.db import models
from django.core.validators import FileExtensionValidator
import uuid

from cms.core.models import TimestampedModel
from .course import Course
from .lesson import CourseLesson


class CourseResource(TimestampedModel):
    """
    Course resources - downloadable files, links, etc.
    Can be attached to courses or specific lessons.
    """

    RESOURCE_TYPE_CHOICES = [
        ('pdf', '📑 PDF Document'),
        ('doc', '📄 Document'),
        ('video', '🎥 Video'),
        ('audio', '🎵 Audio'),
        ('code', '💻 Source Code'),
        ('image', '🖼️ Image'),
        ('archive', '📦 Archive (ZIP)'),
        ('link', '🔗 External Link'),
        ('ebook', '📚 E-book'),
        ('worksheet', '📝 Worksheet'),
        ('slides', '📊 Presentation'),
        ('other', '📎 Other'),
    ]

    resource_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    # Attached to course or lesson
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='resources'
    )
    lesson = models.ForeignKey(
        CourseLesson,
        on_delete=models.CASCADE,
        related_name='resources',
        null=True,
        blank=True,
        help_text="Optional: attach to specific lesson"
    )

    # Resource metadata
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPE_CHOICES)

    # File or link
    file = models.FileField(
        upload_to='courses/resources/',
        blank=True,
        validators=[FileExtensionValidator(
            allowed_extensions=[
                'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
                'zip', 'rar', 'mp3', 'mp4', 'jpg', 'jpeg', 'png',
                'txt', 'csv', 'json', 'xml', 'py', 'js', 'html', 'css'
            ]
        )]
    )
    external_link = models.URLField(blank=True)

    # File information
    file_size = models.PositiveIntegerField(
        default=0,
        help_text="File size in bytes"
    )
    file_extension = models.CharField(max_length=10, blank=True)

    # Access control
    is_downloadable = models.BooleanField(default=True)
    is_preview = models.BooleanField(
        default=False,
        help_text="Available before enrollment"
    )
    requires_completion = models.BooleanField(
        default=False,
        help_text="Requires lesson/course completion"
    )

    # Tracking
    download_count = models.PositiveIntegerField(default=0)

    # Organization
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'cms_course_resources'
        ordering = ['course', 'lesson', 'order']

    def __str__(self):
        return f"{self.title} ({self.get_resource_type_display()})"

    @property
    def file_size_display(self):
        """Human readable file size."""
        if self.file_size == 0:
            return "N/A"

        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        else:
            return f"{self.file_size / (1024 * 1024):.1f} MB"

    def increment_downloads(self):
        """Increment download count."""
        self.download_count += 1
        self.save(update_fields=['download_count'])

    def save(self, *args, **kwargs):
        # Extract file size and extension if file is present
        if self.file:
            self.file_size = self.file.size
            self.file_extension = self.file.name.split('.')[-1].lower()

        super().save(*args, **kwargs)
