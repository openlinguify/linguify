from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

class Language(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class CoursesLanguagesCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=500)

    def __str__(self):
        return self.name

class CoursesSubcategory(models.Model):
    SUBCATEGORY_CHOICES = [
        ('Vocabulary', 'Vocabulary'),
        ('Grammar', 'Grammar'),
        ('Exercise', 'Exercise'),
    ]
    title = models.CharField(max_length=100, choices=SUBCATEGORY_CHOICES)
    category = models.ForeignKey(CoursesLanguagesCategory, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Vocabulary(models.Model):
    title = models.CharField(max_length=100)
    word = models.CharField(max_length=100)
    translation = models.CharField(max_length=100)
    example_sentence = models.TextField(max_length=500)

    def __str__(self):
        return f"{self.title}: {self.word} - {self.translation}"

class Grammar(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    example = models.TextField(max_length=500)

    def __str__(self):
        return self.title

class Unit(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    subcategory = models.ForeignKey(CoursesSubcategory, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Theme(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    image = models.ImageField(upload_to='theme_images/', null=True, blank=True)

    def __str__(self):
        return self.name

class UserLessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    status = models.CharField(max_length=100, default='Not started')
    percentage_completion = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], default=0)
    time_study = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    score_revision = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    score_exercise = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    score_quiz = models.IntegerField(validators=[MinValueValidator(0)], default=0)

    def __str__(self):
        return f"{self.user} - {self.unit} - {self.status}"

class Quiz(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.CharField(max_length=100)
    correct_translation = models.CharField(max_length=100)
    options = models.JSONField(default=list)
    correct_answer = models.CharField(max_length=100)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.word} - {self.correct_translation}"

    def calculate_percentage_completion(self):
        return 100 if self.is_completed else 0


class CoursesLanguages:
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)

    def __str__(self):
        return self.title


class Units:
    pass


class Revision:
    pass


class UserRevisionProgress:
    pass