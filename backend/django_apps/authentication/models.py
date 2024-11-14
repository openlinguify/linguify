from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.exceptions import ValidationError

class Level(models.TextChoices):
    A1 = 'A1', 'A1 - Beginner'
    A2 = 'A2', 'A2 - Elementary'
    B1 = 'B1', 'B1 - Intermediate'
    B2 = 'B2', 'B2 - Upper Intermediate'
    C1 = 'C1', 'C1 - Advanced'
    C2 = 'C2', 'C2 - Proficiency'

class Language(models.TextChoices):
    ENGLISH = 'en', 'English'
    SPANISH = 'es', 'Spanish'
    FRENCH = 'fr', 'French'
    GERMAN = 'de', 'German'

class User(models.Model):

    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    username = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=50, null=True, blank=True)
    password = models.CharField(max_length=50, null=True, blank=True)
    user_language = models.CharField(max_length=50, choices=Language.choices, default=Language.ENGLISH, null=True, blank=True)
    level = models.CharField(max_length=50, choices=Level.choices, default=Level.A1, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

