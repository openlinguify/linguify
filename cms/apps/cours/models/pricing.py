# -*- coding: utf-8 -*-
"""
Course Pricing models
Handle course pricing, discounts, and coupons
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid

from cms.core.models import TimestampedModel
from .course import Course


class CoursePricing(TimestampedModel):
    """
    Course pricing configuration.
    Supports multiple currency and pricing tiers.
    """

    PRICING_TYPE_CHOICES = [
        ('free', 'Free'),
        ('paid', 'Paid'),
        ('subscription', 'Subscription'),
    ]

    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
    ]

    course = models.OneToOneField(
        Course,
        on_delete=models.CASCADE,
        related_name='pricing'
    )

    # Pricing type
    pricing_type = models.CharField(
        max_length=20,
        choices=PRICING_TYPE_CHOICES,
        default='paid'
    )

    # Price
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='EUR')
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    original_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Original price before discount"
    )

    # Discount
    has_discount = models.BooleanField(default=False)
    discount_percentage = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    discount_start_date = models.DateTimeField(null=True, blank=True)
    discount_end_date = models.DateTimeField(null=True, blank=True)

    # Subscription (if applicable)
    subscription_period_days = models.PositiveIntegerField(
        default=30,
        help_text="Subscription period in days"
    )

    # Trial
    has_trial = models.BooleanField(default=False)
    trial_period_days = models.PositiveIntegerField(default=7)

    class Meta:
        db_table = 'cms_course_pricing'

    def __str__(self):
        return f"{self.course.title} - {self.price} {self.currency}"

    @property
    def final_price(self):
        """Calculate final price after discount."""
        if self.has_discount and self.is_discount_active():
            discount_amount = (self.price * self.discount_percentage) / 100
            return self.price - discount_amount
        return self.price

    def is_discount_active(self):
        """Check if discount is currently active."""
        if not self.has_discount:
            return False

        now = timezone.now()
        if self.discount_start_date and now < self.discount_start_date:
            return False
        if self.discount_end_date and now > self.discount_end_date:
            return False

        return True

    def apply_discount(self, percentage, start_date=None, end_date=None):
        """Apply a discount to the course."""
        self.has_discount = True
        self.discount_percentage = percentage
        self.discount_start_date = start_date or timezone.now()
        self.discount_end_date = end_date
        if not self.original_price:
            self.original_price = self.price
        self.save()

    def remove_discount(self):
        """Remove the current discount."""
        self.has_discount = False
        self.discount_percentage = 0
        self.discount_start_date = None
        self.discount_end_date = None
        self.save()


class CourseDiscount(TimestampedModel):
    """
    Discount coupons for courses.
    """

    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]

    coupon_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    code = models.CharField(max_length=50, unique=True)

    # Applicable courses
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='discounts',
        null=True,
        blank=True,
        help_text="Specific course (null = all courses)"
    )

    # Discount details
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    # Validity
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField(null=True, blank=True)

    # Usage limits
    max_uses = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of uses (null = unlimited)"
    )
    current_uses = models.PositiveIntegerField(default=0)
    max_uses_per_user = models.PositiveIntegerField(
        default=1,
        help_text="Maximum uses per user"
    )

    # Minimum purchase
    minimum_purchase_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    class Meta:
        db_table = 'cms_course_discounts'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} - {self.discount_value}"

    def is_valid(self):
        """Check if coupon is valid."""
        if not self.is_active:
            return False

        now = timezone.now()
        if now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False

        if self.max_uses and self.current_uses >= self.max_uses:
            return False

        return True

    def apply_discount(self, price):
        """Calculate discounted price."""
        if not self.is_valid():
            return price

        if self.discount_type == 'percentage':
            discount_amount = (price * self.discount_value) / 100
            return max(0, price - discount_amount)
        else:  # fixed
            return max(0, price - self.discount_value)

    def increment_usage(self):
        """Increment usage count."""
        self.current_uses += 1
        self.save(update_fields=['current_uses'])
