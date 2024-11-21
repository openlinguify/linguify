# backend/django_apps/course/models.py
from django.db import models
from django_apps.users.models import User
#Level_choices of the languages

LEVEL_CHOICES = [
    ('A1', 'Beginner'),
    ('A2', 'Elementary'),
    ('B1', 'Intermediate'),
    ('B2', 'Upper Intermediate'),
    ('C1', 'Advanced'),
    ('C2', 'Proficiency'),
]

TYPE_ACTIVITY = [
    ('Theory', 'Theory'),
    ('Vocabulary', 'Vocabulary'),
    ('Grammar', 'Grammar'),
    ('Listening', 'Listening'),
    ('Speaking', 'Speaking'),
    ('Reading', 'Reading'),
    ('Writing', 'Writing'),
    ('Test', 'Test'),
]

class Objective(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey('Lesson', on_delete=models.CASCADE)

class Language(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=2, unique=True)

    def __str__(self):
        return f"{self.name} - {self.code}"

class Level(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, choices=LEVEL_CHOICES)
    order = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.language} - {self.level}"

class LearningPath(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    learning_path = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return f"{self.learning_path} - {self.description}"

class Unit(models.Model):
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    is_unlocked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} - {self.level}"

class LessonType(models.Model):
    name = models.CharField(max_length=100) # Theory, Vocabulary, Grammar, Listening, Speaking, Reading, Writing, Test


class Lesson(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    lesson_type = models.ForeignKey(LessonType, on_delete=models.CASCADE)

    title = models.CharField(max_length=200)
    difficulty = models.CharField(max_length=10, choices=[('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')], default='Easy')
    estimated_duration = models.IntegerField(help_text="In minutes")
    order = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.unit} - {self.lesson_type} - {self.title}"

class VocabularyList(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title

class Vocabulary(models.Model):
    vocabulary_list = models.ForeignKey(VocabularyList, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    word = models.CharField(max_length=100)
    translation = models.CharField(max_length=100)
    example_sentence = models.TextField()
    example_translation = models.TextField()

EXERCISE_TYPE = [
    ('Multiple choice', 'Multiple choice'),
    ('Reordering', 'Reordering'),
    ('Matching', 'Matching'),
    ('Question and answer', 'Question and answer'),
    ('Fill in the blank', 'Fill in the blank'),
    ('True or False', 'True or False'),
]

class Exercise(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    exercise_type = models.CharField(max_length=100, choices=EXERCISE_TYPE)
    instruction = models.TextField(blank=False, null=False, default='Text of the instruction')
    order = models.PositiveIntegerField()

    def __str__(self):
        return self.instruction


class Vocabulary(models.Model):
    word = models.CharField(max_length=100)
    translation = models.CharField(max_length=100)
    example_sentence = models.TextField()
    example_translation = models.TextField()

    def __str__(self):
        return self.word

class Grammar(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, limit_choices_to={'activity_type': 'Grammar'})
    title = models.CharField(max_length=100)
    description = models.TextField()
    example = models.TextField()

    def __str__(self):
        return self.title

class GrammarRulePoint(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    rule = models.TextField()

# class Video(mdels.Model):
#     title = models.CharField(max_length=100)
#     lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
#    description = models.TextField()
#     video = models.FileField(upload_to='theory_video/')

#     def __str__(self):
#         return self.title

# class Listening(models.Model):
#     activity = models.ForeignKey(Activity, on_delete=models.CASCADE, limit_choices_to={'activity_type': 'Listening'})
#     title = models.CharField(max_length=100)
#     audio = models.FileField(upload_to='listening_audio/')
#
#     def __str__(self):
#         return self.title

# class Speaking(models.Model):
#     activity = models.ForeignKey(Activity, on_delete=models.CASCADE, limit_choices_to={'activity_type': 'Speaking'})
#     title = models.CharField(max_length=100)
#     audio = models.FileField(upload_to='speaking_audio/')
#
#     def __str__(self):
#         return self.title

class Reading(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, limit_choices_to={'activity_type': 'Reading'})
    title = models.CharField(max_length=100)
    text = models.TextField()

    def __str__(self):
        return self.title

class Writing(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, limit_choices_to={'activity_type': 'Writing'})
    title = models.CharField(max_length=100)
    text = models.TextField()

    def __str__(self):
        return self.title

class TestRecap(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)

    question = models.TextField()
    correct_answer = models.CharField(max_length=100)
    incorrect_answers = models.TextField(help_text="Separate the answers with a comma.")
    # Minimum score to pass the test
    passing_score = models.FloatField(default=0.8)

class TestRecapExercise(models.Model):
    test_recap = models.ForeignKey(TestRecap, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

# to takz into account the historicity of the test recap

class TestRecapAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test_recap = models.ForeignKey(TestRecap, on_delete=models.CASCADE)
    score = models.FloatField()
    attempt_date = models.DateTimeField(auto_now_add=True)
    test_recap_passed = models.BooleanField()

    def __str__(self):
        return f"{self.user.username} - {self.test_recap.title} - {self.score} - {self.attempt_date} - {self.test_recap_passed}"



