# backend/django_apps/flashcard/models.py

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from course.models import VocabularyList

class Flashcard(models.Model):
    """Modèle représentant une flashcard pour un utilisateur spécifique liée à un vocabulaire."""
    flashcard_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="flashcards")
    vocabulary = models.ForeignKey(VocabularyList, on_delete=models.CASCADE, related_name="flashcards")
    flashcard_title = models.CharField(max_length=100, blank=False, null=False)
    image_flashcard = models.ImageField(upload_to='flashcard_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.flashcard_id} - {self.user.username} - {self.flashcard_title} - {self.vocabulary.word} - {self.vocabulary.translation}"

    def save(self, *args, **kwargs):
        """Appelle la méthode save de la classe parente."""
        super().save(*args, **kwargs)

    def modify_flashcard(self, new_title):
        """Modifie le titre de la flashcard et sauvegarde les modifications."""
        self.flashcard_title = new_title
        self.save()

    @classmethod
    def create_flashcard(cls, user, vocabulary, flashcard_title, image_flashcard=None):
        """Crée et retourne une nouvelle flashcard."""
        return cls.objects.create(
            user=user,
            vocabulary=vocabulary,
            flashcard_title=flashcard_title,
            image_flashcard=image_flashcard
        )

    def delete_flashcard(self):
        """Supprime la flashcard."""
        self.delete()


class UserFlashcardProgress(models.Model):
    """Modèle pour suivre la progression d'un utilisateur sur une flashcard."""
    STATUT_CHOICES = [
        ('Not started', 'Not started'),
        ('In progress', 'In progress'),
        ('Completed', 'Completed'),
    ]

    user_flashcard_progress_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="flashcard_progress")
    flashcard = models.ForeignKey(Flashcard, on_delete=models.CASCADE, related_name="user_progress")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='Not started')
    percentage_completion = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0
    )
    score_flashcard = models.IntegerField(
        validators=[MinValueValidator(0)],
        default=0
    )
    time_study = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Time spent studying in minutes"
    )

    def __str__(self):
        return (
            f"{self.user.username} - {self.flashcard.flashcard_title} - {self.statut} - "
            f"{self.percentage_completion}% - Time studied: {self.time_study} mins"
        )

    def update_progress(self, statut=None, percentage_completion=None, score_flashcard=None, time_study=None):
        """Met à jour la progression de l'utilisateur sur une flashcard."""
        if statut:
            self.statut = statut
        if percentage_completion is not None:
            self.percentage_completion = percentage_completion
        if score_flashcard is not None:
            self.score_flashcard = score_flashcard
        if time_study is not None:
            self.time_study = time_study
        self.save()

