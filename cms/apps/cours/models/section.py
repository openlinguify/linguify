# -*- coding: utf-8 -*-
"""
Course Section model
Sections organize lessons into logical groups (like chapters/modules)
"""
from django.db import models
from django.utils.text import slugify

from cms.core.models import SyncableModel, MultilingualMixin
from .course import Course


class CourseSection(SyncableModel, MultilingualMixin):
    """
    Course sections - organize lessons into modules/chapters.
    Like Udemy's sections.
    """

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='sections'
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

    # Section metadata
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    # Learning objectives for this section
    learning_objectives = models.JSONField(
        default=list,
        help_text="What students will learn in this section"
    )

    # Duration
    estimated_duration_minutes = models.PositiveIntegerField(
        default=0,
        help_text="Estimated time to complete this section"
    )

    # Lesson count (auto-calculated)
    lesson_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'cms_course_sections'
        ordering = ['course', 'order']
        unique_together = ['course', 'order']

    def __str__(self):
        return f"Section {self.order}: {self.get_localized_field('title', 'fr')}"

    @property
    def title(self):
        return self.get_localized_field('title', 'fr')

    @property
    def description(self):
        return self.get_localized_field('description', 'fr')

    def update_stats(self):
        """Update section statistics."""
        from .lesson import CourseLesson

        self.lesson_count = CourseLesson.objects.filter(section=self).count()

        # Calculate total duration from lessons
        total_duration = CourseLesson.objects.filter(
            section=self
        ).aggregate(
            total=models.Sum('duration_minutes')
        )['total'] or 0

        self.estimated_duration_minutes = total_duration
        self.save(update_fields=['lesson_count', 'estimated_duration_minutes'])

    def move_up(self):
        """Move section up in order."""
        if self.order > 0:
            previous = CourseSection.objects.filter(
                course=self.course,
                order=self.order - 1
            ).first()

            if previous:
                previous.order, self.order = self.order, previous.order
                previous.save()
                self.save()

    def move_down(self):
        """Move section down in order."""
        next_section = CourseSection.objects.filter(
            course=self.course,
            order=self.order + 1
        ).first()

        if next_section:
            next_section.order, self.order = self.order, next_section.order
            next_section.save()
            self.save()
