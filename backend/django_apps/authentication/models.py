from django.db import models  # Ensure this is imported correctly
from django.contrib.auth.models import AbstractUser  # Import AbstractUser for the custom user model

# Choices for Levels and Languages
class Level(models.TextChoices):
    BEGINNER = 'A1', 'Beginner'
    ELEMENTARY = 'A2', 'Elementary'
    INTERMEDIATE = 'B1', 'Intermediate'
    UPPER_INTERMEDIATE = 'B2', 'Upper Intermediate'
    ADVANCED = 'C1', 'Advanced'
    PROFICIENCY = 'C2', 'Proficiency'

class Language(models.TextChoices):
    ENGLISH = 'en', 'English'
    SPANISH = 'es', 'Spanish'
    FRENCH = 'fr', 'French'
    GERMAN = 'de', 'German'

# Base User Model
class User(AbstractUser):
    # Common fields for all users
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    bio = models.TextField(max_length=500, null=True, blank=True)
    learning_language = models.CharField(max_length=20, choices=Language.choices, default=Language.ENGLISH)
    language_level = models.CharField(max_length=2, choices=Level.choices, default=Level.BEGINNER)
    is_coach = models.BooleanField(default=False)  # Flag to indicate if a user is a coach

    # Modify the related_name to avoid conflicts
    groups = models.ManyToManyField(
        'auth.Group',  # Ensure 'auth' is recognized
        related_name='custom_user_groups',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',  # Ensure 'auth' is recognized
        related_name='custom_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return self.username

# Extended Coach Profile Model
class CoachProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='coach_profile')
    coaching_languages = models.CharField(max_length=20, choices=Language.choices, default=Language.ENGLISH)
    price_per_hour = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    availability = models.TextField(null=True, blank=True)
    description = models.TextField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return f"Coach Profile of {self.user.username}"

# Review Model
class Review(models.Model):
    coach = models.ForeignKey(CoachProfile, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    comment = models.TextField(max_length=500, null=True, blank=True)
    review_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.coach.user.username}"

# User Feedback Model
class UserFeedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    feedback_type = models.CharField(max_length=10, choices=[('like', 'Like'), ('dislike', 'Dislike')], default='like')
    feedback_content = models.TextField(null=True, blank=True)
    feedback_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.feedback_type}"
