# authentication/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver

# Choices for Levels, Languages and Objectives
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
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    theme = models.CharField(max_length=30, default='light', choices=[('light', 'Light'), ('dark', 'Dark')])
    notifications = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    sound_notifications = models.BooleanField(default=True)
    language_notifications = models.BooleanField(default=True)
    flashcards_notifications = models.BooleanField(default=True)
class User(AbstractUser):
    user_type = models.CharField(max_length=20, choices=[('student', 'Student'), ('teacher', 'Teacher')])
    settings = models.OneToOneField(UserSetting, on_delete=models.CASCADE, null=True, blank=True, related_name='user_settings')

    def clean(self):
        if self.user_type == 'student' and hasattr(self, 'teacher_profile'):
            raise ValidationError('User cannot be both student and teacher.')
        if self.user_type == 'teacher' and hasattr(self, 'student_profile'):
            raise ValidationError('User cannot be both student and teacher.')

    def __str__(self):
        return f"{self.username} - {self.email}"
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    last_name = models.CharField(max_length=50, null=True, blank=True)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    username = models.CharField(max_length=50, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    bio = models.TextField(max_length=500, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    learning_language = models.CharField(max_length=50, choices=Language.choices, default=Language.ENGLISH, null=True, blank=True)
    mother_language = models.CharField(max_length=50, choices=Language.choices, default=Language.ENGLISH, null=True, blank=True)
    language_level = models.CharField(max_length=50, choices=Level.choices, default=Level.A1, null=True, blank=True)
    objectives = models.CharField(max_length=30, choices=Objectives.choices, default=Objectives.GET_A_JOB, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    enrollment_date = models.DateField(auto_now_add=True, null=True, blank=True)
    is_active = models.BooleanField(default=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    is_verified = models.BooleanField(default=False, null=True, blank=True)
    is_premium = models.BooleanField(default=False, null=True, blank=True)
    is_suspended = models.BooleanField(default=False, null=True, blank=True)
    is_deleted = models.BooleanField(default=False, null=True, blank=True)


class MeetingType(models.TextChoices):
    ONLINE = 'online', 'Online'
    IN_PERSON = 'in_person', 'In Person'
    BOTH = 'both', 'Both'
class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    hire_date = models.DateField(auto_now_add=True, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    presentation = models.TextField(max_length=500, null=True, blank=True)
    mother_language = models.CharField(max_length=50, choices=Language.choices, default=Language.ENGLISH, null=True, blank=True)
    meeting_type = models.CharField(max_length=50, choices=MeetingType.choices, default=MeetingType.ONLINE, null=True, blank=True)
    price_per_hour = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, null=True, blank=True)
    number_of_ratings = models.IntegerField(default=0, null=True, blank=True)
    number_of_students = models.IntegerField(default=0, null=True, blank=True)
    availability = models.TextField(null=True, blank=True)  # JSON or a string that describes the availability
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, null=True, blank=True)
class Review(models.Model):
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='reviews')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='reviews')
    review_date = models.DateTimeField(auto_now_add=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    comment = models.TextField(max_length=500, null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_teacher_rating()

    def update_teacher_rating(self):
        reviews = Review.objects.filter(teacher=self.teacher)
        total_rating = 0
        for review in reviews:
            total_rating += review.rating
        self.teacher.rating = total_rating / len(reviews)
        self.teacher.save()
class UserFeedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    feedback_type = models.CharField(max_length=100, default='like', null=True, blank=True, choices=[('like', 'Like'), ('dislike', 'Dislike')])
    feedback_content = models.TextField(default='Great flashcard!', null=True, blank=True)
    feedback_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.feedback_type}"

# Signals for creating user profiles automatically
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 'student':
            StudentProfile.objects.create(user=instance)
        elif instance.user_type == 'teacher':
            TeacherProfile.objects.create(user=instance)
        UserSetting.objects.create(user=instance)
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 'student':
            instance.student_profile.save()
        elif instance.user_type == 'teacher':
            instance.teacher_profile.save()

        # Ensure settings are properly created if they don't exist
        if not hasattr(instance, 'settings'):
            UserSetting.objects.create(user=instance)
        else:
            instance.settings.save()