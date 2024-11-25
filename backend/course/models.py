from django.db import models
from authentication.models import User

# Level choices for languages
LEVEL_CHOICES = [
    ('A1', 'Beginner'),
    ('A2', 'Elementary'),
    ('B1', 'Intermediate'),
    ('B2', 'Upper Intermediate'),
    ('C1', 'Advanced'),
    ('C2', 'Proficiency'),
]

# Type activity choices
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

    def __str__(self):
        return f"Objective for {self.user.username} - {self.lesson.title}"

class Language(models.Model):
    name = models.CharField(max_length=100, unique=True, blank=False, null=False)
    code = models.CharField(max_length=2, unique=True, blank=False, null=False)

    def __str__(self):
        return f"{self.name} - {self.code}"

class Level(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, choices=LEVEL_CHOICES, blank=False, null=False)
    order = models.PositiveIntegerField(blank=False, null=False, default=1)

    def __str__(self):
        return f"{self.language.name} - {self.name}"

class LearningPath(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, default=1)
    learning_path = models.CharField(max_length=100, unique=True, blank=False, null=False, default='Learning Path')
    description = models.TextField(blank=False, null=False)

    def __str__(self):
        return f"{self.learning_path} - {self.description}"

class Unit(models.Model):
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, blank=False, null=False)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(blank=False, null=False, default=1)
    is_unlocked = models.BooleanField(default=False, blank=False, null=False)
    order = models.PositiveIntegerField(blank=False, null=False, default=1)

    def __str__(self):
        return f"{self.title} - {self.level.name}"

class LessonType(models.Model):
    class LessonTypeChoices:
        THEORY = 'Theory'
        VOCABULARY = 'Vocabulary'
        GRAMMAR = 'Grammar'
        LISTENING = 'Listening'
        SPEAKING = 'Speaking'
        READING = 'Reading'
        WRITING = 'Writing'
        TEST = 'Test'

        CHOICES = [
            (THEORY, 'Theory'),
            (VOCABULARY, 'Vocabulary'),
            (GRAMMAR, 'Grammar'),
            (LISTENING, 'Listening'),
            (SPEAKING, 'Speaking'),
            (READING, 'Reading'),
            (WRITING, 'Writing'),
            (TEST, 'Test'),
        ]

    name = models.CharField(
        max_length=100,
        choices=LessonTypeChoices.CHOICES,
        default=LessonTypeChoices.THEORY,
        unique=True,
        blank=False,
        null=False,
    )

    def __str__(self):
        return self.name

class Lesson(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    lesson_type = models.ForeignKey(LessonType, on_delete=models.CASCADE, default='Theory')
    title = models.CharField(max_length=200, blank=False, null=False)
    difficulty = models.CharField(max_length=10, choices=[('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')], default='Easy', blank=False, null=False)
    estimated_duration = models.IntegerField(help_text="In minutes", blank=False, null=False)
    order = models.PositiveIntegerField(blank=False, null=False, default=1)
    is_complete = models.BooleanField(default=False, blank=False, null=False)

    def __str__(self):
        return f"{self.unit.title} - {self.lesson_type.name} - {self.title}"

class VocabularyList(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, blank=False, null=False)

    def __str__(self):
        return self.title

class Vocabulary(models.Model):
    vocabulary_list = models.ForeignKey(VocabularyList, on_delete=models.CASCADE, default=1)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, default=1)
    word = models.CharField(max_length=100, blank=False, null=False)
    translation = models.CharField(max_length=100, blank=False, null=False)
    example_sentence = models.TextField(blank=True, null=True)
    example_translation = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.word


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
    exercise_type = models.CharField(max_length=100, choices=EXERCISE_TYPE, blank=False, null=False)
    instruction = models.TextField(blank=False, null=False, default='Text of the instruction')
    order = models.PositiveIntegerField(blank=False, null=False, default=1)

    def __str__(self):
        return self.instruction

class Grammar(models.Model):
    lesson_type = models.ForeignKey(LessonType, on_delete=models.CASCADE, default='Grammar')
    title = models.CharField(max_length=100, blank=False, null=False)
    description = models.TextField(blank=False, null=False)
    example = models.TextField(blank=False, null=False)

    def __str__(self):
        return self.title

class GrammarRulePoint(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, blank=False, null=False)
    rule = models.TextField(blank=False, null=False)

    def __str__(self):
        return self.title

class Reading(models.Model):
    title = models.CharField(max_length=100, blank=False, null=False)
    text = models.TextField(blank=False, null=False)

    def __str__(self):
        return self.title

class Writing(models.Model):
    title = models.CharField(max_length=100, blank=False, null=False)
    text = models.TextField(blank=False, null=False)

    def __str__(self):
        return self.title

class TestRecap(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, blank=False, null=False)
    question = models.TextField(blank=False, null=False)
    correct_answer = models.CharField(max_length=100, blank=False, null=False)
    incorrect_answers = models.TextField(blank=False, null=False, help_text="Separate the answers with a comma.")
    passing_score = models.FloatField(default=0.8, blank=False, null=False)

    def __str__(self):
        return self.title

class TestRecapExercise(models.Model):
    test_recap = models.ForeignKey(TestRecap, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(blank=False, null=False, default=1)

class TestRecapAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test_recap = models.ForeignKey(TestRecap, on_delete=models.CASCADE)
    score = models.FloatField(blank=False, null=False)
    attempt_date = models.DateTimeField(auto_now_add=True)
    test_recap_passed = models.BooleanField(blank=False, null=False)

    def __str__(self):
        return f"{self.user.username} - {self.test_recap.title} - {self.score} - {self.attempt_date} - {self.test_recap_passed}"
