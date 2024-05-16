# authentication/models.py
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.db import models

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.db import models

class LevelTarget(models.TextChoices):
    A1 = 'A1', 'A1 - Beginner'
    A2 = 'A2', 'A2 - Elementary'
    B1 = 'B1', 'B1 - Intermediate'
    B2 = 'B2', 'B2 - Upper Intermediate'
    C1 = 'C1', 'C1 - Advanced'
    C2 = 'C2', 'C2 - Proficient'
class Objectives(models.TextChoices):
    GET_A_JOB = 'get_a_job', 'Get a job easily'
    TRAVEL = 'travel', 'Travel in a foreign country'
    LIVE_ABROAD = 'live_abroad', 'Live abroad for a while'
    STUDY_ABROAD = 'study_abroad', 'Study abroad'
    IMPROVE_SKILLS = 'improve_skills', 'Improve skills for work'
    PASS_EXAM = 'pass_exam', 'Pass an exam or test'
    OTHER = 'other', 'Other objective'
class Language(models.Model):
    language_id = models.AutoField(primary_key=True)
    language_name = models.CharField(max_length=100, unique=True)
    language_code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.language_name
class UserSetting(models.Model):
    user_setting_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    settings_language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='settings_language')
    settings_theme = models.CharField(max_length=30, default='light', choices=[('light', 'Light'), ('dark', 'Dark')])
    settings_notifications = models.BooleanField(default=True)
    settings_email_notifications = models.BooleanField(default=True)
    settings_push_notifications = models.BooleanField(default=True)
    settings_sound_notifications = models.BooleanField(default=True)
    settings_language_notifications = models.BooleanField(default=True)
    settings_flashcards_notifications = models.BooleanField(default=True)
    settings_exercises_notifications = models.BooleanField(default=True)
    settings_lessons_notifications = models.BooleanField(default=True)
    settings_courses_notifications = models.BooleanField(default=True)
    settings_groups_notifications = models.BooleanField(default=True)
    settings_friends_notifications = models.BooleanField(default=True)
    settings_messages_notifications = models.BooleanField(default=True)
    settings_calls_notifications = models.BooleanField(default=True)
    settings_video_notifications = models.BooleanField(default=True)
    settings_audio_notifications = models.BooleanField(default=True)
    settings_text_notifications = models.BooleanField(default=True)
    settings_images_notifications = models.BooleanField(default=True)
    settings_videos_notifications = models.BooleanField(default=True)
    settings_audios_notifications = models.BooleanField(default=True)
    settings_files_notifications = models.BooleanField(default=True)
    settings_links_notifications = models.BooleanField(default=True)
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('CREATOR', 'Creator'),
        ('SUBSCRIBER', 'Subscriber'),
    ]
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='SUBSCRIBER')
    objectives = models.CharField(max_length=30, choices=Objectives.choices, default='GET_A_JOB')
    level_target_language = models.CharField(max_length=30, choices=LevelTarget.choices, default='A1')
    language_id = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='user_language_id')
    learning_language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='user_learning_language', default=1)
    mother_language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='user_mother_language')
    settings = models.OneToOneField('UserSetting', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.username} - {self.email} - {self.role}"
class UserFeedback(models.Model):
    user_feedback_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    flashcard_id = models.ForeignKey('flashcards.Flashcard', on_delete=models.CASCADE)
    feedback_type = models.CharField(max_length=100, default='like', null=True, blank=True, choices=[('like', 'Like'), ('dislike', 'Dislike')])
    feedback_content = models.TextField(default='Great flashcard!', null=True, blank=True)
    feedback_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User Feedback {self.user_feedback_id}"