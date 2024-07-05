from django.db import models
from revision.models import Revision

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
