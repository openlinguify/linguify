# -*- coding: utf-8 -*-
"""
Course models for Linguify CMS
Main course entity with categories and tags
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.text import slugify
import uuid

from cms.core.models import TimestampedModel, SyncableModel, MultilingualMixin
from apps.teachers.models import Teacher


class CourseCategory(TimestampedModel):
    """Course categories for organization (like Udemy categories)."""

    CATEGORY_CHOICES = [
        ('development', '💻 Development'),
        ('business', '💼 Business'),
        ('finance', '💰 Finance & Accounting'),
        ('it_software', '🖥️ IT & Software'),
        ('office_productivity', '📊 Office Productivity'),
        ('personal_development', '🌟 Personal Development'),
        ('design', '🎨 Design'),
        ('marketing', '📈 Marketing'),
        ('lifestyle', '🎯 Lifestyle'),
        ('photography', '📷 Photography & Video'),
        ('health_fitness', '💪 Health & Fitness'),
        ('music', '🎵 Music'),
        ('teaching', '👨‍🏫 Teaching & Academics'),
        ('languages', '🗣️ Languages'),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    category_type = models.CharField(max_length=30, choices=CATEGORY_CHOICES, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='bi-folder')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'cms_course_categories'
        ordering = ['order', 'name']
        verbose_name_plural = 'Course Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class CourseTag(TimestampedModel):
    """Tags for course discovery and search."""

    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    usage_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'cms_course_tags'
        ordering = ['-usage_count', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Course(SyncableModel, MultilingualMixin):
    """
    Main Course model - like Udemy/Superprof courses.
    Ultra-modular course container with all metadata.
    """

    STATUS_CHOICES = [
        ('draft', '📝 Draft'),
        ('in_review', '👀 In Review'),
        ('published', '✅ Published'),
        ('archived', '📦 Archived'),
    ]

    LEVEL_CHOICES = [
        ('all_levels', 'All Levels'),
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]

    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('fr', 'Français'),
        ('es', 'Español'),
        ('nl', 'Nederlands'),
    ]

    # Identification
    course_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    slug = models.SlugField(max_length=200, unique=True)

    # Teacher/Instructor
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name='created_courses'
    )
    co_instructors = models.ManyToManyField(
        Teacher,
        related_name='co_instructed_courses',
        blank=True
    )

    # Multilingual fields
    title_en = models.CharField(max_length=200)
    title_fr = models.CharField(max_length=200)
    title_es = models.CharField(max_length=200)
    title_nl = models.CharField(max_length=200)

    subtitle_en = models.CharField(max_length=250, blank=True)
    subtitle_fr = models.CharField(max_length=250, blank=True)
    subtitle_es = models.CharField(max_length=250, blank=True)
    subtitle_nl = models.CharField(max_length=250, blank=True)

    description_en = models.TextField()
    description_fr = models.TextField()
    description_es = models.TextField()
    description_nl = models.TextField()

    # What students will learn
    learning_objectives = models.JSONField(
        default=list,
        help_text="List of learning outcomes"
    )

    # Course requirements/prerequisites
    requirements = models.JSONField(
        default=list,
        help_text="List of prerequisites"
    )

    # Target audience
    target_audience = models.JSONField(
        default=list,
        help_text="Who is this course for"
    )

    # Course metadata
    category = models.ForeignKey(
        CourseCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='courses'
    )
    tags = models.ManyToManyField(CourseTag, related_name='courses', blank=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='all_levels')
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='fr')

    # Media
    thumbnail = models.ImageField(
        upload_to='courses/thumbnails/',
        blank=True,
        help_text="Course thumbnail (1920x1080 recommended)"
    )
    promo_video = models.FileField(
        upload_to='courses/promos/',
        blank=True,
        help_text="Promotional video"
    )

    # Status and publishing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)

    # Enrollment settings
    is_enrollable = models.BooleanField(default=True)
    max_students = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of students (null = unlimited)"
    )
    enrollment_count = models.PositiveIntegerField(default=0)

    # Course duration
    estimated_duration_hours = models.PositiveIntegerField(
        default=0,
        help_text="Total estimated duration in hours"
    )
    total_lectures = models.PositiveIntegerField(default=0)
    total_resources = models.PositiveIntegerField(default=0)

    # Ratings and reviews
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    total_reviews = models.PositiveIntegerField(default=0)

    # SEO
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)

    # Analytics
    view_count = models.PositiveIntegerField(default=0)
    completion_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Average completion rate percentage"
    )

    # Features
    has_certificate = models.BooleanField(default=True)
    has_lifetime_access = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)

    # Dates
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'cms_courses'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['teacher', 'status']),
            models.Index(fields=['category', 'is_published']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.get_localized_field('title', 'fr')} - {self.teacher.full_name}"

    @property
    def title(self):
        return self.get_localized_field('title', 'fr')

    @property
    def subtitle(self):
        return self.get_localized_field('subtitle', 'fr')

    @property
    def description(self):
        return self.get_localized_field('description', 'fr')

    def save(self, *args, **kwargs):
        # Auto-generate slug from title if not set
        if not self.slug:
            base_slug = slugify(self.title_en or self.title_fr)
            self.slug = f"{base_slug}-{str(self.course_id)[:8]}"

        # Set published_at when publishing for the first time
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
            self.status = 'published'

        super().save(*args, **kwargs)

    def publish(self):
        """Publish the course."""
        self.is_published = True
        self.status = 'published'
        self.published_at = timezone.now()
        self.save()

    def unpublish(self):
        """Unpublish the course."""
        self.is_published = False
        self.status = 'draft'
        self.save()

    def archive(self):
        """Archive the course."""
        self.status = 'archived'
        self.is_enrollable = False
        self.save()

    def increment_views(self):
        """Increment view count."""
        self.view_count += 1
        self.save(update_fields=['view_count'])

    def update_stats(self):
        """Update course statistics (ratings, enrollments, etc.)."""
        from .enrollment import CourseEnrollment
        from .review import CourseReview

        # Update enrollment count
        self.enrollment_count = CourseEnrollment.objects.filter(course=self).count()

        # Update ratings
        reviews = CourseReview.objects.filter(course=self)
        self.total_reviews = reviews.count()
        if self.total_reviews > 0:
            avg_rating = reviews.aggregate(models.Avg('rating'))['rating__avg']
            self.average_rating = round(avg_rating, 2)

        self.save(update_fields=['enrollment_count', 'total_reviews', 'average_rating'])

    def is_full(self):
        """Check if course has reached max students."""
        if self.max_students is None:
            return False
        return self.enrollment_count >= self.max_students

    def can_enroll(self):
        """Check if new students can enroll."""
        return (
            self.is_published
            and self.is_enrollable
            and not self.is_full()
        )
