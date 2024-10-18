# linguify/models.py

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
import random
from django.utils import timezone
from authentication.models import Language, Level

class CourseLanguage(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    image = models.ImageField(upload_to='course_images/', null=True, blank=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='course_languages')
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='vocabularies')  # Utilisation correcte des choices
    duration = models.PositiveIntegerField(help_text="Duration in hours", null=True, blank=True)
    prerequisites = models.TextField(max_length=500, null=True, blank=True, help_text="Prerequisites for this course")

    def __str__(self):
        return self.title


    def get_units(self):
        return self.units.all()

class CourseCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.name

class CourseSubcategory(models.Model):
    SUBCATEGORY_CHOICES = [
        ('Vocabulary', 'Vocabulary'),
        ('Grammar', 'Grammar'),
        ('Exercise', 'Exercise'),
    ]
    title = models.CharField(max_length=100, choices=SUBCATEGORY_CHOICES)
    category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE, related_name='subcategories')

    def __str__(self):
        return self.title

class Vocabulary(models.Model):
    title = models.CharField(max_length=100)
    word = models.CharField(max_length=500)
    translation = models.CharField(max_length=500)
    example_sentence = models.TextField(max_length=500)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='vocabularies')
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='vocabularies')
    theme = models.ForeignKey('Theme', on_delete=models.SET_NULL, null=True, blank=True, related_name='vocabularies')

    def __str__(self):
        return f"{self.title} - {self.word} - {self.translation}"
    @property
    def get_vocabulary(self):
        return f"{self.word} - {self.translation}"

class Grammar(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    example = models.TextField(max_length=500)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='grammars')
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='vocabularies')
    theme = models.ForeignKey('Theme', on_delete=models.SET_NULL, null=True, blank=True, related_name='grammars')

    def __str__(self):
        return self.title

    @property
    def get_grammar(self):
        return f"{self.title} - {self.description}"

class Unit(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    course = models.ForeignKey(CourseLanguage, on_delete=models.CASCADE, related_name='units')
    subcategory = models.ForeignKey(CourseSubcategory, on_delete=models.CASCADE, related_name='units')
    unit_type = models.CharField(max_length=100)
    order = models.PositiveIntegerField()
    duration = models.PositiveIntegerField(help_text="Duration in minutes", null=True, blank=True)

    def __str__(self):
        return self.title
class Level(models.TextChoices):
    A1 = 'A1', 'A1 - Beginner'
    A2 = 'A2', 'A2 - Elementary'
    B1 = 'B1', 'B1 - Intermediate'
    B2 = 'B2', 'B2 - Upper Intermediate'
    C1 = 'C1', 'C1 - Advanced'
    C2 = 'C2', 'C2 - Proficiency'
class Theme(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500, null=True, blank=True)
    image = models.ImageField(upload_to='theme_images/', null=True, blank=True)

    def __str__(self):
        return self.name

class UserLessonProgress(models.Model):
    STATUS_CHOICES = [
        ('Not started', 'Not started'),
        ('In progress', 'In progress'),
        ('Completed', 'Completed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_progresses')
    course = models.ForeignKey(CourseLanguage, on_delete=models.CASCADE, related_name='user_progresses')
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='user_progresses')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Not started')
    percentage_completion = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], default=0)
    time_study = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)
    score_revision = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)
    score_exercise = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)
    score_quiz = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)

    def __str__(self):
        return f"{self.user.username} - {self.unit.title} - {self.status}"

    def update_progress(self, progress_increment=10):
        """Updates the completion percentage."""
        self.percentage_completion = min(100, self.percentage_completion + progress_increment)
        self.save()

    def mark_complete(self):
        """Marks the lesson as completed."""
        self.status = 'Completed'
        self.percentage_completion = 100
        self.save()

class Revision(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    word = models.CharField(max_length=100)
    translation = models.CharField(max_length=100)
    last_revision_date = models.DateTimeField(auto_now=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='revisions')
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='vocabularies')level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='revisions')
    theme = models.ForeignKey('Theme', on_delete=models.SET_NULL, null=True, blank=True, related_name='revisions')

    def __str__(self):
        return f"{self.title} - {self.word} - {self.translation}"

    @classmethod
    def get_random_words(cls, language, level, num_words=1):
        vocabulary_words = cls.objects.filter(language=language, level=level)
        if vocabulary_words.exists():
            return random.sample(list(vocabulary_words), num_words)
        else:
            return None

class UserRevisionProgress(models.Model):
    STATUS_CHOICES = [
        ('Not started', 'Not started'),
        ('In progress', 'In progress'),
        ('Completed', 'Completed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='revision_progresses')
    revision = models.ForeignKey(Revision, on_delete=models.CASCADE, related_name='user_progresses')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Not started')
    percentage_completion = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], default=0)
    time_study = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)
    score_revision = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)
    words_succeeded = models.PositiveIntegerField(default=0)
    words_failed = models.PositiveIntegerField(default=0)
    words_to_review = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.revision.title} - {self.status}"

    def start_revision(self):
        self.status = 'In progress'
        self.save()

    def update_progress(self, succeeded=True):
        if succeeded:
            self.words_succeeded += 1
        else:
            self.words_failed += 1
            self.words_to_review += 1

        total_words = self.words_succeeded + self.words_failed
        if total_words > 0:
            self.percentage_completion = int((self.words_succeeded / total_words) * 100)
        else:
            self.percentage_completion = 0

        self.save()

    def reset_progress(self):
        self.status = 'Not started'
        self.percentage_completion = 0
        self.time_study = 0
        self.score_revision = 0
        self.words_succeeded = 0
        self.words_failed = 0
        self.words_to_review = 0
        self.save()

    def get_review_words(self, num_words=1):
        if self.words_to_review > 0:
            return Revision.get_random_words(self.revision.language, self.revision.level, num_words)
        else:
            return None

    @classmethod
    def get_user_revision_progress(cls, user, revision):
        return cls.objects.filter(user=user, revision=revision).first()

    def complete_revision(self):
        self.status = 'Completed'
        self.percentage_completion = 100
        self.save()

    def update_score(self, score):
        self.score_revision += score
        self.save()

    def update_time_study(self, time):
        self.time_study += time
        self.save()

class Quiz(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quizzes')
    word = models.CharField(max_length=100)
    correct_translation = models.CharField(max_length=100)
    options = models.JSONField(default=list)
    correct_answer = models.CharField(max_length=100)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='quizzes')
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='vocabularies')

    def __str__(self):
        return f"Quiz {self.pk} - {self.user.username} - {self.word}"

class Flashcard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='flashcards')
    vocabulary = models.ForeignKey(Vocabulary, on_delete=models.CASCADE, related_name='flashcards')
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name='flashcards')
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='flashcard_images/', null=True, blank=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='flashcards')
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='vocabularies')

    def __str__(self):
        return f"{self.title} - {self.vocabulary.word} - {self.vocabulary.translation}"

    def get_flashcard(self):
        return f"{self.vocabulary.word} - {self.vocabulary.translation}"

class UserFlashcardProgress(models.Model):
    STATUS_CHOICES = [
        ('Not started', 'Not started'),
        ('In progress', 'In progress'),
        ('Completed', 'Completed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='flashcard_progresses')
    flashcard = models.ForeignKey(Flashcard, on_delete=models.CASCADE, related_name='user_progresses')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Not started')
    percentage_completion = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], default=0)
    score = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)
    time_study = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)
    last_reviewed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.flashcard.title} - {self.status}"

    def update_progress(self, correct=True):
        """Update the progress based on the user's interaction with the flashcard."""
        if correct:
            self.score += 1
        total_vocabulary = self.flashcard.vocabulary_set.count()
        if total_vocabulary > 0:
            self.percentage_completion = int((self.score / total_vocabulary) * 100)
        else:
            self.percentage_completion = 0

        if self.percentage_completion >= 100:
            self.status = 'Completed'

        self.save()

    def reset_progress(self):
        """Reset the user's progress on the flashcard."""
        self.status = 'Not started'
        self.percentage_completion = 0
        self.score = 0
        self.time_study = 0
        self.save()

class Flashcard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='flashcards')
    vocabulary = models.ManyToManyField(Vocabulary, related_name='flashcards')
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name='flashcards')
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='flashcard_images/', null=True, blank=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='flashcards')
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='vocabularies')

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    def add_vocabulary(self, vocabulary_item):
        """Add a vocabulary item to the flashcard."""
        self.vocabulary.add(vocabulary_item)

    def remove_vocabulary(self, vocabulary_item):
        """Remove a vocabulary item from the flashcard."""
        self.vocabulary.remove(vocabulary_item)

    def get_flashcard_content(self):
        """Get all vocabulary items associated with this flashcard."""
        return self.vocabulary.all()

    def modify_flashcard(self, title=None, theme=None, image=None):
        """Modify flashcard details."""
        if title:
            self.title = title
        if theme:
            self.theme = theme
        if image:
            self.image = image
        self.save()
class RevisionCard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='revision_cards')
    vocabulary = models.ForeignKey(Vocabulary, on_delete=models.CASCADE, related_name='revision_cards')
    last_reviewed = models.DateTimeField(auto_now=True)
    ease_factor = models.FloatField(default=2.5)
    interval = models.PositiveIntegerField(default=1)
    repetitions = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.vocabulary.word}"

    def review(self, quality):
        # Implement the SM-2 algorithm for spaced repetition
        if quality < 3:
            self.repetitions = 0
            self.interval = 1
        else:
            self.repetitions += 1
            if self.repetitions == 1:
                self.interval = 1
            elif self.repetitions == 2:
                self.interval = 6
            else:
                self.interval = int(self.interval * self.ease_factor)

        self.ease_factor = max(1.3, self.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
        self.last_reviewed = timezone.now()
        self.save()
