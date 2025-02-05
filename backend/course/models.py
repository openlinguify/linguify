# course/models.py
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from authentication.models import User

"""
Learning Path Overview:
-----------------------
1. Languages:
    - English, French, Spanish, Dutch.
2. Levels:
    - A1 to C2.
3. Units:
    - Unit 1: Vocabulary, Theory, and Exercises.
    - Unit 2: Grammar and Exercises.
4. Progression:
    - Includes Theory -> Exercises -> Test.

Refer to the diagram for more details: path/to/image.png
"""

# class MultilingualMixin:
#     def get_localized_field(self, field_base_name, target_language='en'):
#         field_name = f"{field_base_name}_{target_language}"
#         return getattr(self, field_name, getattr(self, f"{field_base_name}_en", None))

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

class Unit(models.Model):
    LEVEL_CHOICES = [
        ('A1', 'A1'),
        ('A2', 'A2'),
        ('B1', 'B1'),
        ('B2', 'B2'),
        ('C1', 'C1'),
        ('C2', 'C2'),
    ]
    title_en = models.CharField(max_length=100, blank=False, null=False)
    title_fr = models.CharField(max_length=100, blank=False, null=False)
    title_es = models.CharField(max_length=100, blank=False, null=False)
    title_nl = models.CharField(max_length=100, blank=False, null=False)
    description_en = models.TextField(null=True, blank=True)
    description_fr = models.TextField(null=True, blank=True)
    description_es = models.TextField(null=True, blank=True)
    description_nl = models.TextField(null=True, blank=True)
    level = models.CharField(max_length=2, choices=LEVEL_CHOICES, blank=False, null=False)
    order = models.PositiveIntegerField(blank=False, null=False, default=1)
    
    def get_formatted_titles(self):
        titles = {
            'EN': self.title_en,
            'FR': self.title_fr,
            'ES': self.title_es,
            'NL': self.title_nl
        }
        return ' | '.join(
            f"{lang}: {title[:20]}..." if len(title) > 20 else f"{lang}: {title}"
            for lang, title in titles.items()
        )


    def __str__(self):
        unit_info = f"Unit {self.order:02d}".ljust(15)
        level_info = f"[{self.level}]".ljust(5)
        return f"{unit_info} {level_info} {self.get_formatted_titles()}"

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


class Lesson(models.Model):
    LESSON_TYPE = [
        ('theory', 'Theory'),
        ('vocabulary', 'Vocabulary'),
        ('grammar', 'Grammar'),
        ('pronunciation', 'Pronunciation'),
        ('listening', 'Listening'),
        ('speaking', 'Speaking'),
        ('reading', 'Reading'),
        ('writing', 'Writing'),
        ('test', 'Test'),
    ]
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='lessons')
    lesson_type = models.CharField(max_length=100, choices=LESSON_TYPE, blank=False, null=False)
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

    def __str__(self):
        return f"{self.unit.title_en} - {self.title_en} - {self.lesson_type}"

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

class ContentLesson(models.Model):
    CONTENT_TYPE = [
        ('Theory', 'Theory'),
        ('Vocabulary', 'Vocabulary'),
        ('Grammar', 'Grammar'),
        ('Multiple choice', 'Multiple choice'),
        ('Numbers', 'Numbers'),
        ('Reordering', 'Reordering'),
        ('Matching', 'Matching'),
        ('Question and answer', 'Question and answer'),
        ('fill_blank', 'Fill in the blanks'),
        ('True or False', 'True or False'),
        ('Test', 'Test'),
    ]
        
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='content_lessons')
    content_type = models.CharField(max_length=100, choices=CONTENT_TYPE, blank=False, null=False, db_index=True)
    title_en = models.CharField(max_length=255, blank=False, null=False)
    title_fr = models.CharField(max_length=255, blank=False, null=False)
    title_es = models.CharField(max_length=255, blank=False, null=False)
    title_nl = models.CharField(max_length=255, blank=False, null=False)
    instruction_en = models.TextField(blank=False, null=False, default='Text of the instruction')
    instruction_fr = models.TextField(blank=False, null=False, default='Text of the instruction')
    instruction_es = models.TextField(blank=False, null=False, default='Text of the instruction')
    instruction_nl = models.TextField(blank=False, null=False, default='Text of the instruction')
    estimated_duration = models.IntegerField(help_text="Duration in minutes", validators=[MinValueValidator(1)], blank=False, null=False)
    order = models.PositiveIntegerField(blank=False, validators=[MinValueValidator(1)],null=False, default=1)

    class Meta:
        ordering = ['order', 'id']
        verbose_name= "Content Lesson"
        verbose_name_plural = "Content Lessons"
        indexes = [
            models.Index(fields=['content_type']),
            models.Index(fields=['order']),
        ]


    def __str__(self):
        return f"{self.lesson.title_en} - {self.title_en} - {self.content_type}"
    
    def get_title(self, target_language='en'):
        """
        Get the title in the specified language.
        
        Args:
            target_language (str): Language code ('en', 'fr', 'es', or 'nl')
            
        Returns:
            str: Title in the requested language
        """
        return getattr(self, f'title_{target_language}', self.title_en)

    def get_instruction(self, target_language='en'):
        """
        Get the instruction in the specified language.
        
        Args:
            target_language (str): Language code ('en', 'fr', 'es', or 'nl')
            
        Returns:
            str: Instruction in the requested language
        """
        return getattr(self, f'instruction_{target_language}', self.instruction_en)

    def save(self, *args, **kwargs):
        """Override save to ensure content type is lowercase and validate duration"""
        self.content_type = self.content_type.lower()
        if self.estimated_duration < 1:
            self.estimated_duration = 1
        super().save(*args, **kwargs)

class VocabularyList(models.Model):

    content_lesson = models.ForeignKey(ContentLesson, on_delete=models.CASCADE, related_name='vocabulary_lists', default=1)
    word_en = models.CharField(max_length=100, blank=False, null=False)
    word_fr = models.CharField(max_length=100, blank=False, null=False)
    word_es = models.CharField(max_length=100, blank=False, null=False)
    word_nl = models.CharField(max_length=100, blank=False, null=False)
    definition_en = models.TextField(blank=False, null=False)
    definition_fr = models.TextField(blank=False, null=False)
    definition_es = models.TextField(blank=False, null=False)
    definition_nl = models.TextField(blank=False, null=False)
    example_sentence_en = models.TextField(blank=True, null=True)
    example_sentence_fr = models.TextField(blank=True, null=True)
    example_sentence_es = models.TextField(blank=True, null=True)
    example_sentence_nl = models.TextField(blank=True, null=True)
    word_type_en = models.CharField(max_length=100, blank=False, null=False)
    word_type_fr = models.CharField(max_length=100, blank=False, null=False)
    word_type_es = models.CharField(max_length=100, blank=False, null=False)
    word_type_nl = models.CharField(max_length=100, blank=False, null=False)
    synonymous_en = models.TextField(blank=True, null=True)
    synonymous_fr = models.TextField(blank=True, null=True)
    synonymous_es = models.TextField(blank=True, null=True)
    synonymous_nl = models.TextField(blank=True, null=True)
    antonymous_en = models.TextField(blank=True, null=True)
    antonymous_fr = models.TextField(blank=True, null=True)
    antonymous_es = models.TextField(blank=True, null=True)
    antonymous_nl = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.content_lesson} - {self.word_en} - {self.definition_en}"

    def get_translation(self, target_language):
        switch = {
            'fr': self.word_fr,
            'es': self.word_es,
            'nl': self.word_nl,
        }
        return switch.get(target_language, self.word_en)

    def get_example_sentence(self, target_language):
        switch = {
            'fr': self.example_sentence_fr,
            'es': self.example_sentence_es,
            'nl': self.example_sentence_nl,
        }
        return switch.get(target_language, self.example_sentence_en)

    def get_definition(self, target_language):
        switch = {
            'fr': self.definition_fr,
            'es': self.definition_es,
            'nl': self.definition_nl,
        }
        return switch.get(target_language, self.definition_en)
    
    def get_word_type(self, target_language):
        switch = {
            'fr': self.word_type_fr,
            'es': self.word_type_es,
            'nl': self.word_type_nl,
        }
        return switch.get(target_language, self.word_type_en)
    
    def get_synonymous(self, target_language):
        switch = {
            'fr': self.synonymous_fr,
            'es': self.synonymous_es,
            'nl': self.synonymous_nl,
        }
        return switch.get(target_language, self.synonymous_en)
    
    def get_antonymous(self, target_language):
        switch = {
            'fr': self.antonymous_fr,
            'es': self.antonymous_es,
            'nl': self.antonymous_nl,
        }
        return switch.get(target_language, self.antonymous_en)

class MultipleChoiceQuestion(models.Model):
    content_lesson = models.ForeignKey(ContentLesson, on_delete=models.CASCADE, related_name='multiple_choices', default=1)
    # example of question Level A1: What is the capital of Belgium?
    question_en = models.CharField(max_length=255, blank=False, null=False)
    question_fr = models.CharField(max_length=255, blank=False, null=False)
    question_es = models.CharField(max_length=255, blank=False, null=False)
    question_nl = models.CharField(max_length=255, blank=False, null=False)
    # example of correct answer Level A1: Brussels
    correct_answer_en = models.CharField(max_length=255, blank=False, null=False)

    fake_answer1_en = models.CharField(max_length=255, blank=False, null=False)
    fake_answer2_en = models.CharField(max_length=255, blank=False, null=False)
    fake_answer3_en = models.CharField(max_length=255, blank=False, null=False)
    fake_answer4_en = models.CharField(max_length=255, blank=False, null=False)

    hint_answer_en = models.CharField(max_length=255, blank=True, null=True)
    # example of correct answer Level A1: Bruxelles
    correct_answer_fr = models.CharField(max_length=255, blank=False, null=False)

    fake_answer1_fr = models.CharField(max_length=255, blank=False, null=False)
    fake_answer2_fr = models.CharField(max_length=255, blank=False, null=False)
    fake_answer3_fr = models.CharField(max_length=255, blank=False, null=False)
    fake_answer4_fr = models.CharField(max_length=255, blank=False, null=False)

    hint_answer_fr = models.CharField(max_length=255, blank=True, null=True)
    # example of correct answer Level A1: Bruselas
    correct_answer_es = models.CharField(max_length=255, blank=False, null=False)

    fake_answer1_es = models.CharField(max_length=255, blank=False, null=False)
    fake_answer2_es = models.CharField(max_length=255, blank=False, null=False)
    fake_answer3_es = models.CharField(max_length=255, blank=False, null=False)
    fake_answer4_es = models.CharField(max_length=255, blank=False, null=False)

    hint_answer_es = models.CharField(max_length=255, blank=True, null=True)

    # example of correct answer Level A1: Brussel
    correct_answer_nl = models.CharField(max_length=255, blank=False, null=False)

    fake_answer1_nl = models.CharField(max_length=255, blank=False, null=False)
    fake_answer2_nl = models.CharField(max_length=255, blank=False, null=False)
    fake_answer3_nl = models.CharField(max_length=255, blank=False, null=False)
    fake_answer4_nl = models.CharField(max_length=255, blank=False, null=False)

    hint_answer_nl = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.content_lesson} - {self.question_en}"

class Numbers(models.Model):
    content_lesson = models.ForeignKey(ContentLesson, on_delete=models.CASCADE, related_name='numbers', default=1)
    number = models.CharField(max_length=255, blank=False, null=False)
    number_en = models.CharField(max_length=255, blank=False, null=False)
    number_fr = models.CharField(max_length=255, blank=False, null=False)
    number_es = models.CharField(max_length=255, blank=False, null=False)
    number_nl = models.CharField(max_length=255, blank=False, null=False)
    is_reviewed = models.BooleanField(default=False, blank=False, null=False)

    def __str__(self):
        return f"{self.content_lesson} - {self.content_lesson.title_en} - {self.number} - {self.number_en} - {self.is_reviewed}"
    
class ExerciseVocabularyMultipleChoice(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    question = models.TextField(blank=False, null=False, help_text="Question based on example sentence")
    correct_answer = models.CharField(max_length=255, blank=False, null=False, help_text="Correct answer from vocabulary")
    incorrect_answers = models.JSONField(blank=False, null=False, help_text="List of incorrect answers")
    explanation = models.TextField(blank=True, null=True, help_text="Explanation for the correct answer")

    def __str__(self):
        return f"{self.lesson.title_en} - {self.question}"
    
    @classmethod
    def create_from_vocabulary(cls, lesson, vocab):
        return cls(
            lesson=lesson,
            question=vocab.example_sentence_en,
            correct_answer=vocab.word_en,
            incorrect_answers=[vocab.word_fr, vocab.word_es, vocab.word_nl],
            explanation=f"{vocab.word_en} means {vocab.definition_en}",
        )
class ExerciseVocabularyFillBlank(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    sentence_fill_blank_en = models.TextField(blank=False, null=False, help_text="Sentence with a blank space")
    sentence_fill_blank_fr = models.TextField(blank=False, null=False, help_text="Sentence with a blank space")
    sentence_fill_blank_es = models.TextField(blank=False, null=False, help_text="Sentence with a blank space")
    sentence_fill_blank_nl = models.TextField(blank=False, null=False, help_text="Sentence with a blank space")
    correct_answer_en = models.CharField(max_length=255, blank=False, null=False, help_text="Correct answer for the blank space")
    correct_answer_fr = models.CharField(max_length=255, blank=False, null=False)
    correct_answer_es = models.CharField(max_length=255, blank=False, null=False)
    correct_answer_nl = models.CharField(max_length=255, blank=False, null=False)
    explanation_en = models.TextField(blank=True, null=True)
    explanation_fr = models.TextField(blank=True, null=True)
    explanation_es = models.TextField(blank=True, null=True)
    explanation_nl = models.TextField(blank=True, null=True)
    hint_en = models.TextField(blank=True, null=True)
    hint_fr = models.TextField(blank=True, null=True)
    hint_es = models.TextField(blank=True, null=True)
    hint_nl = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.lesson.title_en} - {self.sentence_fill_blank_en}"
class ExerciseGrammarReordering(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    sentence_en = models.TextField(blank=False, null=False, help_text="Sentence to reorder")
    sentence_fr = models.TextField(blank=False, null=False, help_text="Sentence to reorder")
    sentence_es = models.TextField(blank=False, null=False, help_text="Sentence to reorder")
    sentence_nl = models.TextField(blank=False, null=False, help_text="Sentence to reorder")
    correct_order = models.JSONField(blank=False, null=False, help_text="List of words in the correct order")
    explanation = models.TextField(blank=True, null=True, help_text="Explanation for the correct order")
    hint = models.TextField(blank=True, null=True, help_text="Hint to help the user")

    def __str__(self):
        return f"{self.lesson.title_en} - {self.sentence_en}"
    
    @classmethod
    def create_from_vocabulary(cls, lesson, vocab):
        """
        Creates reordering exercises using vocabulary example sentences.
        """
        words = vocab.example_sentence_en.split()
        return cls(
            lesson=lesson,
            sentence=vocab.example_sentence_en,
            correct_order=words,
            explanation="Reorder the words to match the correct sentence structure.",
            hint="Start with the subject and follow the sentence structure rules.",
            difficulty_level='medium'
        ) 
class GrammarRule(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='grammar_rules', default=1)

    title_en = models.CharField(max_length=255, blank=False, null=False, default="Grammar rule title")
    title_fr = models.CharField(max_length=255, blank=False, null=False, default="Grammar rule title")
    title_es = models.CharField(max_length=255, blank=False, null=False, default="Grammar rule title")
    title_nl = models.CharField(max_length=255, blank=False, null=False, default="Grammar rule title")
    content = models.TextField(blank=False, null=False, help_text="Explication de la règle de grammaire", default="Grammar rule content")

    examples = models.JSONField(
        blank=False,
        null=False,
        help_text="Exemples sous forme JSON. Exemple : [{'en': 'I eat', 'fr': 'Je mange'}]",
        default=list,
    )
    special_cases = models.TextField(
        blank=True,
        null=True,
        help_text="Notes sur les cas particuliers ou exceptions (optionnel)",
    )
    related_tenses = models.JSONField(
        blank=True,
        null=True,
        help_text="Liste des temps liés. Exemple : ['Present Simple', 'Past Perfect']",
    )

    def __str__(self):
        return f"{self.lesson.title_en} - {self.title}"
class Grammar(models.Model):
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
    test_recap = models.ForeignKey(TestRecap, on_delete=models.CASCADE)
    score = models.FloatField(blank=False, null=False)
    attempt_date = models.DateTimeField(auto_now_add=True)
    test_recap_passed = models.BooleanField(blank=False, null=False)

    def __str__(self):
        return f"{self.test_recap.title} - {self.score}"
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


    