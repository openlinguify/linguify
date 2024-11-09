from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import random


class Revision(models.Model):
    revision_id = models.AutoField(primary_key=True)
    revision_title = models.CharField(max_length=100)
    revision_description = models.TextField(max_length=500)
    word = models.CharField(max_length=100)
    translation = models.CharField(max_length=100)
    last_revision_date = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.revision_title} - {self.word} - {self.translation}"
    @classmethod
    def get_random_words(cls, language, level, num_words=1):
        """Retrieve random vocabulary words based on language and level."""
        vocabulary_words = cls.objects.filter(language=language, level=level)
        if vocabulary_words.exists():
            return random.sample(list(vocabulary_words), num_words)
        else:
            return None
class UserRevisionProgress(models.Model):
    STATUT_CHOICES = [
        ('Not started', 'Not started'),
        ('In progress', 'In progress'),
        ('Completed', 'Completed'),
    ]
    user_revision_progress_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    revision_id = models.ForeignKey(Revision, on_delete=models.CASCADE)
    statut = models.CharField(max_length=100, choices=STATUT_CHOICES, default='Not started')
    percentage_completion = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], default=0)
    time_study = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    score_revision = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    words_succeeded = models.IntegerField(default=0)
    words_failed = models.IntegerField(default=0)
    words_to_review = models.IntegerField(default=0)
    def __str__(self):
        return f"{self.user.username} - {self.revision.title}"
    def start_revision(self):
        """Start the revision for the user."""
        self.statut = 'In progress'
        self.save()
    def update_progress(self, succeeded=True):
        """Update the progress of the user based on the result of the revision."""
        if succeeded:
            self.words_succeeded += 1
        else:
            self.words_failed += 1
            self.words_to_review += 1

        total_words = self.words_succeeded + self.words_failed
        if total_words > 0:
            self.percentage_completion = (self.words_succeeded / total_words) * 100
        else:
            self.percentage_completion = 0

        self.save()
    def reset_progress(self):
        """Reset the progress of the user."""
        self.statut = 'Not started'
        self.percentage_completion = 0
        self.time_study = 0
        self.score_revision = 0
        self.words_succeeded = 0
        self.words_failed = 0
        self.words_to_review = 0
        self.save()
    def get_review_words(self, num_words=1):
        """Retrieve words to review based on the progress of the user."""
        if self.words_to_review > 0:
            return Revision.get_random_words(self.revision.language, self.revision.level, num_words)
        else:
            return None
    @classmethod
    def get_user_revision_progress(cls, user, revision):
        """Retrieve the progress of a user on a specific revision."""
        try:
            return cls.objects.get(user=user, revision=revision)
        except cls.DoesNotExist:
            return None
    def complete_revision(self):
        self.statut = 'Completed'
        self.percentage_completion = 100
        self.save()

    def update_score(self, score):
        self.score_revision += score
        self.save()

    def update_time_study(self, time):
        self.time_study += time
        self.save()