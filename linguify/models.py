#linguify/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User, AbstractUser
import random
from authentication.models import User, Language, Level
class Courses_languages(models.Model):
    course_languages_id = models.AutoField(primary_key=True)
    course_languages_title = models.CharField(max_length=100)
    course_description = models.TextField(max_length=500)
    course_image = models.ImageField(upload_to='course_images/', null=True, blank=True)
    def __str__(self):
        return self.course_languages_title

class Courses_languages_categories(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100)
    category_description = models.TextField(max_length=500)

    def __str__(self):
        return self.category_name

class Courses_subcategories(models.Model):
    SUBCATEGORY_CHOICES = [
        ('Vocabulary', 'Vocabulary'),
        ('Grammar', 'Grammar'),
        ('Exercice', 'Exercice'),
    ]
    subcategory_id = models.AutoField(primary_key=True)
    subcategory_title = models.CharField(max_length=100, choices=SUBCATEGORY_CHOICES, null=False)
    category_id = models.ForeignKey(Courses_languages_categories, on_delete=models.CASCADE)

    def __str__(self):
        return self.subcategory_title

class Vocabulary(models.Model):
    vocabulary_id = models.AutoField(primary_key=True)
    vocabulary_title = models.CharField(max_length=100)
    word = models.CharField(max_length=500)
    translation = models.CharField(max_length=500)
    example_sentence = models.TextField(max_length=500)
    def __str__(self):
        return f"{self.vocabulary_id} - {self.language_id} - {self.vocabulary_title} - {self.word} - {self.translation}"
    @property
    def get_vocabulary(self):
        return f"{self.word} - {self.translation}"

class Grammar(models.Model):
    grammar_id = models.AutoField(primary_key=True)
    grammar_title = models.CharField(max_length=100)
    grammar_description = models.TextField(max_length=500)
    grammar_example = models.TextField(max_length=500)
    def __str__(self):
        return f"{self.id} - {self.language_id} - {self.grammar_title}"
    @property
    def get_grammar(self):
        return f"{self.grammar_title} - {self.grammar_description}"
class Units(models.Model):
    unit_id = models.AutoField(primary_key=True)
    unit_title = models.CharField(max_length=100)
    unit_description = models.TextField(max_length=500)
    course_id = models.ForeignKey(Courses_languages, on_delete=models.CASCADE)
    subcategory_id = models.ForeignKey(Courses_subcategories, on_delete=models.CASCADE)
    unit_type = models.CharField(max_length=100)
    def __str__(self):
        return self.unit_title
class Theme(models.Model):
    id = models.AutoField(primary_key=True)
    theme_name = models.CharField(max_length=100)
    theme_description = models.TextField(max_length=500)
    theme_image = models.ImageField(upload_to='theme_images/', null=True, blank=True)
    def __str__(self):
        return self.theme_name
class UserLessonProgress(models.Model):
    user_lesson_progress_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    course_id = models.ForeignKey(Courses_languages, on_delete=models.CASCADE)
    unit_id = models.ForeignKey('Units', on_delete=models.CASCADE)
    statut = models.CharField(max_length=100)
    percentage_completion = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    time_study = models.IntegerField(validators=[MinValueValidator(0)])
    score_revision = models.IntegerField(validators=[MinValueValidator(0)])
    score_exercise = models.IntegerField(validators=[MinValueValidator(0)])
    score_quiz = models.IntegerField(validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.user_id} - {self.user_lesson_progress_id} - {self.course_id} - {self.unit_id} - {self.status}"
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
class Quiz(models.Model):
    quiz_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.CharField(max_length=100)
    correct_translation = models.CharField(max_length=100)
    options = models.JSONField(default=list)
    correct_answer = models.CharField(max_length=100)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.quiz_id} - {self.user_id} - {self.mother_language} - {self.learning_language} - {self.word} - {self.correct_translation}"
class Flashcard(models.Model):
    flashcard_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vocabulary = models.ForeignKey(Vocabulary, on_delete=models.CASCADE)
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE)
    flashcard_title = models.CharField(max_length=100, blank=False, null=False)
    image_flashcard = models.ImageField(upload_to='flashcard_images/', null=True, blank=True)
    def add_vocabulary_to_flashcard(self, vocabulary_id):
        vocabulary_entry = Vocabulary.objects.get(id=vocabulary_id)
        self.vocabulary.add(vocabulary_entry)
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        vocabulary_entry = Vocabulary.objects.get(id=1)
        self.vocabulary.add(vocabulary_entry)
    def remove_vocabulary_from_flashcard(self, vocabulary_id):
        vocabulary_entry = Vocabulary.objects.get(id=vocabulary_id)
        self.vocabulary.remove(vocabulary_entry)
    def modify_flashcard(self, flashcard_id):
        flashcard = Flashcard.objects.get(id=flashcard_id)
        flashcard.flashcard_title = 'new title'
        flashcard.save()
    def __str__(self):
        return f"{self.flashcard_id} - {self.user} - {self.language} - {self.flashcard_title} - {self.vocabulary.word} - {self.vocabulary.translation} - {self.level}"

    @property
    def get_flashcard(self):
        return f"{self.vocabulary.word} - {self.vocabulary.translation}"
class UserFlashcardProgress(models.Model):
    """
    This Django model represents the progress of a user on a specific flashcard.

    Attributes:
    user_flashcard_progress_id: An automatically incrementing integer that serves as the primary key.
    user_id: A foreign key that links to the AuthUser model. It represents the user who is making progress.
    flashcard_id: A foreign key that links to the Flashcards model. It represents the flashcard on which progress is being made.
    statut: A character field that represents the status of the user's progress. It can be 'Not started', 'In progress', or 'Completed'.
    pourcentage_completion: An integer field that represents the percentage of completion of the flashcard by the user. It must be between 0 and 100.
    time_study: An integer field that represents the time spent studying the flashcard. It must be a non-negative integer.
    """
    STATUT_CHOICES = [
        ('Not started', 'Not started'),
        ('In progress', 'In progress'),
        ('Completed', 'Completed'),
    ]
    user_flashcard_progress_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    flashcard_id = models.ForeignKey(Flashcard, on_delete=models.CASCADE)
    statut = models.CharField(max_length=100, choices=STATUT_CHOICES)
    percentage_completion = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    score_flashcard = models.IntegerField(validators=[MinValueValidator(0)])
    time_study = models.IntegerField(validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.user_id} - {self.flashcard_id} - {self.statut} - {self.percentage_completion} - {self.time_study}"
    @property
    def calculate_percentage_completion(self):
        total_items = 100
        actual_completude = 0
        if self.statut == 'Completed':
            actual_completude = total_items
        else:
            actual_completude = self.percentage_completion
        return actual_completude

