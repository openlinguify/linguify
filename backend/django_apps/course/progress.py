# backend/django_apps/course/progress.py
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User
from .models import Unit, LearningPath

STATUT_CHOICES = [
    ('Not started', 'Not started'),
    ('In progress', 'In progress'),
    ('Completed', 'Completed'),
]

class UserLessonProgress(models.Model):
    user_lesson_progress_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey('Lesson', on_delete=models.CASCADE)
    statut = models.CharField(max_length=100, choices=STATUT_CHOICES)
    percentage_completion = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    score_lesson = models.IntegerField(validators=[MinValueValidator(0)])
    time_study = models.IntegerField(validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title} - {self.statut} - {self.percentage_completion}% - Time studied: {self.time_study} mins"

class UserUnitProgress(models.Model):
    user_unit_progress_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    statut = models.CharField(max_length=100, choices=STATUT_CHOICES)
    percentage_completion = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    score_unit = models.IntegerField(validators=[MinValueValidator(0)])
    time_study = models.IntegerField(validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.user.username} - {self.unit.title} - {self.statut} - {self.percentage_completion}% - Time studied: {self.time_study} mins"

    def update_progress(self, user, unit, statut, percentage_completion, score_unit, time_study):
        self.user = user
        self.unit = unit
        self.statut = statut
        self.percentage_completion = percentage_completion
        self.score_unit = score_unit
        self.time_study = time_study
        self.save()

    def remove_progress(self, user_unit_progress_id):
        self.user_unit_progress_id = user_unit_progress_id
        self.delete()
        self.save()

    def get_user_progress(self, user):
        self.user = user
        return self.user_unit_progress_id


class UserLearningPathProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE)
    current_unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.learning_path.name} - {'In Progress' if not self.finished_at else 'Completed'}"

