# -*- coding: utf-8 -*-
"""
Course Review and Rating models
Student reviews and course ratings
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

from cms.core.models import TimestampedModel
from .course import Course


class CourseReview(TimestampedModel):
    """
    Student reviews for courses.
    Like Udemy/Superprof reviews.
    """

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='course_reviews'
    )

    # Rating (1-5 stars)
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    # Review text
    title = models.CharField(max_length=200, blank=True)
    review = models.TextField()

    # Detailed ratings (optional)
    content_quality = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Quality of course content"
    )
    instructor_quality = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Instructor teaching quality"
    )
    value_for_money = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Value for money"
    )

    # Moderation
    is_published = models.BooleanField(default=True)
    is_verified_purchase = models.BooleanField(default=False)

    # Engagement
    helpful_count = models.PositiveIntegerField(default=0)
    report_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'cms_course_reviews'
        unique_together = ['course', 'student']  # One review per student per course
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['course', 'is_published']),
            models.Index(fields=['student']),
        ]

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.course.title} ({self.rating}★)"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update course rating
        self.course.update_stats()

    def delete(self, *args, **kwargs):
        course = self.course
        super().delete(*args, **kwargs)
        # Update course rating after deletion
        course.update_stats()

    def mark_helpful(self):
        """Increment helpful count."""
        self.helpful_count += 1
        self.save(update_fields=['helpful_count'])

    def report(self):
        """Increment report count."""
        self.report_count += 1
        self.save(update_fields=['report_count'])


class CourseRating(models.Model):
    """
    Aggregated course ratings by star level.
    Used for displaying rating distribution.
    """

    course = models.OneToOneField(
        Course,
        on_delete=models.CASCADE,
        related_name='rating_distribution'
    )

    # Star counts
    five_star_count = models.PositiveIntegerField(default=0)
    four_star_count = models.PositiveIntegerField(default=0)
    three_star_count = models.PositiveIntegerField(default=0)
    two_star_count = models.PositiveIntegerField(default=0)
    one_star_count = models.PositiveIntegerField(default=0)

    # Total
    total_ratings = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'cms_course_ratings'

    def __str__(self):
        return f"Ratings for {self.course.title}"

    def update_from_reviews(self):
        """Recalculate rating distribution from reviews."""
        from django.db.models import Count, Q

        reviews = CourseReview.objects.filter(
            course=self.course,
            is_published=True
        )

        rating_counts = reviews.aggregate(
            five=Count('id', filter=Q(rating=5)),
            four=Count('id', filter=Q(rating=4)),
            three=Count('id', filter=Q(rating=3)),
            two=Count('id', filter=Q(rating=2)),
            one=Count('id', filter=Q(rating=1)),
        )

        self.five_star_count = rating_counts['five']
        self.four_star_count = rating_counts['four']
        self.three_star_count = rating_counts['three']
        self.two_star_count = rating_counts['two']
        self.one_star_count = rating_counts['one']
        self.total_ratings = reviews.count()

        self.save()

    @property
    def rating_percentages(self):
        """Get percentage distribution of ratings."""
        if self.total_ratings == 0:
            return {
                5: 0, 4: 0, 3: 0, 2: 0, 1: 0
            }

        return {
            5: (self.five_star_count / self.total_ratings) * 100,
            4: (self.four_star_count / self.total_ratings) * 100,
            3: (self.three_star_count / self.total_ratings) * 100,
            2: (self.two_star_count / self.total_ratings) * 100,
            1: (self.one_star_count / self.total_ratings) * 100,
        }
