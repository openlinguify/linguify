#linguify/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User, AbstractUser
import random
from authentication.models import User


class Courses_languages(models.Model):
    course_languages_id = models.AutoField(primary_key=True)
    course_languages_title = models.CharField(max_length=100)
    course_description = models.TextField(max_length=500)
    course_image = models.ImageField(upload_to='course_images/', null=True, blank=True)
    def __str__(self):
        return self.course_languages_title

    objects = models.Manager()  # Ensure the default manager is set
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


