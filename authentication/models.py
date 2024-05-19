# authentication/models.py
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

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
    
class Objectives(models.TextChoices):
    GET_A_JOB = 'get_a_job', 'Get a job easily'
    TRAVEL = 'travel', 'Travel in a foreign country'
    LIVE_ABROAD = 'live_abroad', 'Live abroad for a while'
    STUDY_ABROAD = 'study_abroad', 'Study abroad'
    IMPROVE_SKILLS = 'improve_skills', 'Improve skills for work'
    PASS_EXAM = 'pass_exam', 'Pass an exam or test'
    OTHER = 'other', 'Other objective'

class UserSetting(models.Model):
    user_setting_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    settings_theme = models.CharField(max_length=30, default='light', choices=[('light', 'Light'), ('dark', 'Dark')])
    settings_notifications = models.BooleanField(default=True)
    settings_email_notifications = models.BooleanField(default=True)
    settings_push_notifications = models.BooleanField(default=True) 
    settings_sound_notifications = models.BooleanField(default=True)
    settings_language_notifications = models.BooleanField(default=True)
    settings_flashcards_notifications = models.BooleanField(default=True)
    
class User(AbstractUser):
    profile_picture = models.ImageField(verbose_name='Profile Picture')
    mother_language = models.CharField(max_length=50, choices=Language.choices, default=Language.ENGLISH, null=True, blank=True)    
    learning_language = models.CharField(max_length=50, choices=Language.choices, default=Language.SPANISH, null=True, blank=True)
    language_level = models.CharField(max_length=50, choices=Level.choices, default=Level.A1, null=True, blank=True)
    objectives = models.CharField(max_length=30, choices=Objectives.choices, default=Objectives.GET_A_JOB, null=True, blank=True)
    settings = models.OneToOneField(UserSetting, on_delete=models.CASCADE, null=True, blank=True, related_name='user_settings')

    def __str__(self):
        return f"{self.username} - {self.email}"

class UserFeedback(models.Model):
    user_feedback_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    feedback_type = models.CharField(max_length=100, default='like', null=True, blank=True, choices=[('like', 'Like'), ('dislike', 'Dislike')])
    feedback_content = models.TextField(default='Great flashcard!', null=True, blank=True)
    feedback_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User Feedback {self.user_feedback_id}"