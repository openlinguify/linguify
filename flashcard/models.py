from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from linguify.models import Vocabulary, Theme
from authentication.models import User


class Flashcard(models.Model):
    flashcard_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vocabulary = models.ForeignKey(Vocabulary, on_delete=models.CASCADE)
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE)
    flashcard_title = models.CharField(max_length=100, blank=False, null=False)
    image_flashcard = models.ImageField(upload_to='flashcard_images/', null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def modify_flashcard(self, new_title):
        self.flashcard_title = new_title
        self.save()

    def __str__(self):
        return f"{self.flashcard_id} - {self.user.username} - {self.flashcard_title} - {self.vocabulary.word} - {self.vocabulary.translation}"


class UserFlashcardProgress(models.Model):
    STATUT_CHOICES = [
        ('Not started', 'Not started'),
        ('In progress', 'In progress'),
        ('Completed', 'Completed'),
    ]
    user_flashcard_progress_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flashcard = models.ForeignKey(Flashcard, on_delete=models.CASCADE)
    statut = models.CharField(max_length=100, choices=STATUT_CHOICES)
    percentage_completion = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    score_flashcard = models.IntegerField(validators=[MinValueValidator(0)])
    time_study = models.IntegerField(validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.user.username} - {self.flashcard.flashcard_title} - {self.statut} - {self.percentage_completion}% - Time studied: {self.time_study} mins"
