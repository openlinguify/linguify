# course/models.py
from django.db import models
from authentication.models import User

# class MultilingualMixin:
#     def get_localized_field(self, field_base_name, target_language='en'):
#         field_name = f"{field_base_name}_{target_language}"
#         return getattr(self, field_name, getattr(self, f"{field_base_name}_en", None))

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

    def __str__(self):
        return f"{self.language} - {self.learning_path}"

class Unit(models.Model):
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE)
    title_en = models.CharField(max_length=100, blank=False, null=False)
    title_fr = models.CharField(max_length=100, blank=False, null=False)
    title_es = models.CharField(max_length=100, blank=False, null=False)
    title_nl = models.CharField(max_length=100, blank=False, null=False)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(blank=False, null=False, default=1)
    is_unlocked = models.BooleanField(default=False, blank=False, null=False)
    progress = models.FloatField(default=0.0, blank=False)

    def __str__(self):
        return f"{self.title_en} - {self.level.name}"

    def get_unit_title(self, target_language='en'):
        match target_language:
            case 'fr':
                return self.title_fr
            case 'es':
                return self.title_es
            case 'nl':
                return self.title_nl
            case "en":
                return self.title_en
            case _:
                return "Language not supported"

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
    lesson_type = models.ForeignKey(LessonType, on_delete=models.CASCADE, null=True, blank=True, related_name='lessons')
    title_en = models.CharField(max_length=255, blank=False, null=False)
    title_fr = models.CharField(max_length=255, blank=False, null=False)
    title_es = models.CharField(max_length=255, blank=False, null=False)
    title_nl = models.CharField(max_length=255, blank=False, null=False)
    description_en = models.TextField(blank=False, null=False)
    description_fr = models.TextField(blank=False, null=False)
    description_es = models.TextField(blank=False, null=False)
    description_nl = models.TextField(blank=False, null=False)
    estimated_duration = models.IntegerField(help_text="In minutes", blank=False, null=False)
    order = models.PositiveIntegerField(blank=False, null=False, default=1)
    is_complete = models.BooleanField(default=False, blank=False, null=False)

    def __str__(self):
        return f"{self.unit.title_en} - {self.lesson_type.name} - {self.title_en}"

    def get_title(self, target_language='en'):
        if target_language == 'fr':
            return self.title_fr
        elif target_language == 'es':
            return self.title_es
        elif target_language == 'nl':
            return self.title_nl
        else:
            return self.title_en

    def get_description(self, target_language):
        switch = {
            'fr': self.description_fr,
            'es': self.description_es,
            'nl': self.description_nl,
        }
        return switch.get(target_language, self.description_en)

class VocabularyList(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    word_en = models.CharField(max_length=100, blank=False, null=False)
    word_fr = models.CharField(max_length=100, blank=False, null=False)
    word_es = models.CharField(max_length=100, blank=False, null=False)
    word_nl = models.CharField(max_length=100, blank=False, null=False)
    example_sentence_en = models.TextField(blank=True, null=True)
    example_sentence_fr = models.TextField(blank=True, null=True)
    example_sentence_es = models.TextField(blank=True, null=True)
    example_sentence_nl = models.TextField(blank=True, null=True)
    word_type = models.CharField(max_length=100, blank=False, null=False)

    def __str__(self):
        return f"Vocabulary list for Lesson {self.lesson.title_en}"


class Exercise(models.Model):
    EXERCISE_TYPE = [
        ('Multiple choice', 'Multiple choice'),
        ('Reordering', 'Reordering'),
        ('Matching', 'Matching'),
        ('Question and answer', 'Question and answer'),
        ('fill_blank', 'Fill in the blanks'),
        ('True or False', 'True or False'),
    ]
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

class GrammarModule(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, blank=False, null=False)
    is_locked = models.BooleanField(default=True, blank=False, null=False)

    @property
    def unlock_module(self):
        for module in GrammarModule.objects.all():
            if module.is_locked:
                module.is_locked = False
                module.save()
                return module
            else:
                return None

    def __str__(self):
        return self.title

    def get_list_grammar_modules(self):
        pass

class GrammarRule(models.Model):
    grammar_module = models.ForeignKey(GrammarModule, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, blank=False, null=False)

class GrammarRuleContent(models.Model):
    theory = models.TextField(blank=False, null=False)
    example = models.TextField(blank=False, null=False)
    example_fr = models.TextField(blank=False, null=False)
    example_es = models.TextField(blank=False, null=False)
    example_de = models.TextField(blank=False, null=False)
    example_it = models.TextField(blank=False, null=False)
    example_translation = models.TextField(blank=False, null=False)
    example_translation_fr = models.TextField(blank=False, null=False)
    example_translation_es = models.TextField(blank=False, null=False)
    example_translation_de = models.TextField(blank=False, null=False)
    example_translation_it = models.TextField(blank=False, null=False)
    grammar_rule = models.ForeignKey(GrammarRule, on_delete=models.CASCADE)

class GrammarRuleExercise(models.Model):
    grammar_rule = models.ForeignKey(GrammarRule, on_delete=models.CASCADE)
    question = models.TextField(blank=False, null=False)
    correct_answer = models.CharField(max_length=100, blank=False, null=False)
    incorrect_answers = models.TextField(blank=False, null=False, help_text="Separate the answers with a comma.")
    passing_score = models.FloatField(default=0.8, blank=False, null=False)

    def __str__(self):
        return self.question

    def get_grammar_rule_exercise(self):
        pass
