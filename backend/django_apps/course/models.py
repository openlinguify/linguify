from django.db import models

class Language_learning(models.Model):
    pass

class Unit(models.Model):
    pass

class Lesson(models.Model):
    pass

class Question(models.Model):
    pass

class Exercises(models.Model):
    pass

class Category_exercises(models.Model):
    pass

class Vocabulary(models.Model):
    pass

class Grammar(models.Model):
    pass

class Listening(models.Model):
    pass

class Reading(models.Model):
    pass

class Writing(models.Model):
    pass

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


from django.db import models
#from revision.models import Revision

# Choices for Levels of Language Proficiency
LEVEL_LANGUAGE = (
    ('A1-', 'A1-'),
    ('A1', 'A1'),
    ('A2', 'A2'),
    ('B1', 'B1'),
    ('B2', 'B2'),
    ('C1', 'C1'),
    ('C2', 'C2'),
)

# Choices for Types of Activity
TYPE_ACTIVITY = (
    ('Vocabulaire', 'Vocabulaire'),
    ('Video', 'Video'),
    ('Exercice', 'Exercice'),
    ('Test', 'Test'),
)


class Categorie(models.Model):
    name_categorie = models.CharField(max_length=100)
    image_categorie = models.ImageField(upload_to='images/', null=True, blank=True, default='images/default.jpg')

    def __str__(self):
        return self.name_categorie


class Sous_categorie(models.Model):
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    name_sous_categorie = models.CharField(max_length=100)
    image_sous_categorie = models.ImageField(upload_to='images/', null=True, blank=True, default='images/default.jpg')

    def __str__(self) -> str:
        """
        Returns a string representation of the sub-category, including the main category name.
        """
        return f"{self.categorie.name_categorie} - {self.name_sous_categorie}"


class Lesson(models.Model):
    sous_categorie = models.ForeignKey(Sous_categorie, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    image_lesson = models.ImageField(upload_to='images/', null=True, blank=True, default='images/default.jpg')
    level_language = models.CharField(max_length=3, choices=LEVEL_LANGUAGE, default='A1-')

    def __str__(self) -> str:
        """
        Returns a string representation of the lesson, including the sub-category name.
        """
        return f"{self.sous_categorie.name_sous_categorie} - {self.name}"


class Activity(models.Model):
    type_activity = models.CharField(max_length=100, choices=TYPE_ACTIVITY, default='Vocabulaire')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    icon_activity = models.ImageField(upload_to='images/', null=True, blank=True, default='images/default.jpg')

    def __str__(self):
        return f"{self.lesson.name} - {self.type_activity}"


class Vocabulaire(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, limit_choices_to={'type_activity': 'Vocabulaire'},
                                 null=True, blank=True)
    word = models.CharField(max_length=100)
    translation = models.CharField(max_length=100)
    type_word = models.CharField(max_length=100)
    definition = models.TextField()
    example = models.TextField()
    example_translation = models.TextField()
    rewiewed = models.BooleanField(default=False)

    def __str__(self):
        return self.word


class Video(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, limit_choices_to={'type_activity': 'Video'},
                                 null=True, blank=True)
    title_video = models.CharField(max_length=100)
    video = models.FileField(upload_to='videos/', null=True, blank=True)

    def __str__(self):
        return self.title_video


class Exercice(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, limit_choices_to={'type_activity': 'Exercice'},
                                 null=True, blank=True)
    title_exercice = models.CharField(max_length=100)
    exercice = models.FileField(upload_to='exercices/', null=True, blank=True)

    def __str__(self):
        return self.title_exercice


class Test(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, limit_choices_to={'type_activity': 'Test'},
                                 null=True, blank=True)
    title_test = models.CharField(max_length=100)
    test = models.FileField(upload_to='tests/', null=True, blank=True)

    def __str__(self):
        return self.title_test
