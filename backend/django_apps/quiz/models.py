# backend/django_apps/quiz/models.py
from django.db import models
from django.conf import settings  # Import settings for AUTH_USER_MODEL

class Quiz(models.Model):
    quiz_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Use AUTH_USER_MODEL
    word = models.CharField(max_length=100)
    correct_translation = models.CharField(max_length=100)
    options = models.JSONField(default=list)
    correct_answer = models.CharField(max_length=100)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.quiz_id} - {self.user.username} - {self.word} - {self.correct_translation} - {self.correct_answer}"
