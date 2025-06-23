# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

"""
Modèles d'exercices pour l'application Course.
Contient VocabularyList, MultipleChoiceQuestion, MatchingExercise, etc.
"""

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _
from .core import ContentLesson
import json
import random
import logging

logger = logging.getLogger(__name__)


class VocabularyList(models.Model):
    """Vocabulaire associé à une leçon de contenu."""
    
    content_lesson = models.ForeignKey(ContentLesson, on_delete=models.CASCADE, related_name='vocabulary_lists')
    word_en = models.CharField(max_length=100, blank=False, null=False)
    word_fr = models.CharField(max_length=100, blank=False, null=False)
    word_es = models.CharField(max_length=100, blank=False, null=False)
    word_nl = models.CharField(max_length=100, blank=False, null=False)
    definition_en = models.TextField(blank=True, null=True)
    definition_fr = models.TextField(blank=True, null=True)
    definition_es = models.TextField(blank=True, null=True)
    definition_nl = models.TextField(blank=True, null=True)
    example_sentence_en = models.TextField(blank=True, null=True)
    example_sentence_fr = models.TextField(blank=True, null=True)
    example_sentence_es = models.TextField(blank=True, null=True)
    example_sentence_nl = models.TextField(blank=True, null=True)
    word_type_en = models.CharField(max_length=50, blank=True, null=True)
    word_type_fr = models.CharField(max_length=50, blank=True, null=True)
    word_type_es = models.CharField(max_length=50, blank=True, null=True)
    word_type_nl = models.CharField(max_length=50, blank=True, null=True)
    synonymous_en = models.CharField(max_length=200, blank=True, null=True)
    synonymous_fr = models.CharField(max_length=200, blank=True, null=True)
    synonymous_es = models.CharField(max_length=200, blank=True, null=True)
    synonymous_nl = models.CharField(max_length=200, blank=True, null=True)
    antonymous_en = models.CharField(max_length=200, blank=True, null=True)
    antonymous_fr = models.CharField(max_length=200, blank=True, null=True)
    antonymous_es = models.CharField(max_length=200, blank=True, null=True)
    antonymous_nl = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        app_label = 'course'
        ordering = ['content_lesson__lesson__unit__order', 'content_lesson__lesson__order', 'content_lesson__order']

    def __str__(self):
        return f"{self.word_en} - {self.content_lesson.title_en}"

    def get_translation(self, target_language='en'):
        """Récupère la traduction du mot dans la langue cible."""
        return getattr(self, f'word_{target_language}', self.word_en)

    def get_definition(self, target_language='en'):
        """Récupère la définition dans la langue cible."""
        return getattr(self, f'definition_{target_language}', self.definition_en)

    def get_example_sentence(self, target_language='en'):
        """Récupère l'exemple de phrase dans la langue cible."""
        return getattr(self, f'example_sentence_{target_language}', self.example_sentence_en)

    def get_word_type(self, target_language='en'):
        """Récupère le type de mot dans la langue cible."""
        return getattr(self, f'word_type_{target_language}', self.word_type_en)

    def get_synonymous(self, target_language='en'):
        """Récupère les synonymes dans la langue cible."""
        return getattr(self, f'synonymous_{target_language}', self.synonymous_en)

    def get_antonymous(self, target_language='en'):
        """Récupère les antonymes dans la langue cible."""
        return getattr(self, f'antonymous_{target_language}', self.antonymous_en)


class MultipleChoiceQuestion(models.Model):
    """Question à choix multiples."""
    
    content_lesson = models.ForeignKey(ContentLesson, on_delete=models.CASCADE, related_name='multiple_choice_questions')
    question_en = models.TextField(blank=False, null=False)
    question_fr = models.TextField(blank=False, null=False)
    question_es = models.TextField(blank=False, null=False)
    question_nl = models.TextField(blank=False, null=False)
    correct_answer_en = models.CharField(max_length=200, blank=False, null=False)
    correct_answer_fr = models.CharField(max_length=200, blank=False, null=False)
    correct_answer_es = models.CharField(max_length=200, blank=False, null=False)
    correct_answer_nl = models.CharField(max_length=200, blank=False, null=False)
    
    # Fausses réponses
    fake_answer1_en = models.CharField(max_length=200, blank=True, null=True)
    fake_answer1_fr = models.CharField(max_length=200, blank=True, null=True)
    fake_answer1_es = models.CharField(max_length=200, blank=True, null=True)
    fake_answer1_nl = models.CharField(max_length=200, blank=True, null=True)
    fake_answer2_en = models.CharField(max_length=200, blank=True, null=True)
    fake_answer2_fr = models.CharField(max_length=200, blank=True, null=True)
    fake_answer2_es = models.CharField(max_length=200, blank=True, null=True)
    fake_answer2_nl = models.CharField(max_length=200, blank=True, null=True)
    fake_answer3_en = models.CharField(max_length=200, blank=True, null=True)
    fake_answer3_fr = models.CharField(max_length=200, blank=True, null=True)
    fake_answer3_es = models.CharField(max_length=200, blank=True, null=True)
    fake_answer3_nl = models.CharField(max_length=200, blank=True, null=True)
    fake_answer4_en = models.CharField(max_length=200, blank=True, null=True)
    fake_answer4_fr = models.CharField(max_length=200, blank=True, null=True)
    fake_answer4_es = models.CharField(max_length=200, blank=True, null=True)
    fake_answer4_nl = models.CharField(max_length=200, blank=True, null=True)
    
    # Indices
    hint_answer_en = models.TextField(blank=True, null=True)
    hint_answer_fr = models.TextField(blank=True, null=True)
    hint_answer_es = models.TextField(blank=True, null=True)
    hint_answer_nl = models.TextField(blank=True, null=True)

    class Meta:
        app_label = 'course'

    def __str__(self):
        return f"MCQ: {self.question_en[:50]}... - {self.content_lesson.title_en}"


class MatchingExercise(models.Model):
    """Exercice d'association entre mots."""
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    content_lesson = models.ForeignKey(ContentLesson, on_delete=models.CASCADE, related_name='matching_exercises')
    title_en = models.CharField(max_length=200, blank=True, null=True)
    title_fr = models.CharField(max_length=200, blank=True, null=True)
    title_es = models.CharField(max_length=200, blank=True, null=True)
    title_nl = models.CharField(max_length=200, blank=True, null=True)
    vocabulary_items = models.ManyToManyField(VocabularyList, blank=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='easy')
    pairs_count = models.PositiveIntegerField(default=5, validators=[MinValueValidator(3), MaxValueValidator(15)])
    order = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'course'
        ordering = ['content_lesson__lesson__unit__order', 'content_lesson__lesson__order', 'order']

    def __str__(self):
        return f"Matching: {self.title_en or 'Untitled'} - {self.content_lesson.title_en}"

    def get_exercise_data(self, native_language='en', target_language='fr'):
        """Récupère les données formatées pour l'exercice."""
        try:
            target_words, native_words, correct_pairs = self.get_matching_pairs(native_language, target_language)
            
            return {
                'exercise_id': self.id,
                'target_words': target_words,
                'native_words': native_words,
                'correct_pairs': correct_pairs,
                'difficulty': self.difficulty,
                'pairs_count': len(correct_pairs),
                'instructions': {
                    'en': "Match the words with their translations",
                    'fr': "Associez les mots avec leurs traductions",
                    'es': "Asocia las palabras con sus traducciones",
                    'nl': "Koppel de woorden aan hun vertalingen"
                }
            }
        except Exception as e:
            logger.error(f"Error generating exercise data: {str(e)}")
            return {'error': str(e)}

    def get_matching_pairs(self, native_language='en', target_language='fr'):
        """Génère les paires pour l'exercice d'association."""
        vocabulary_items = list(self.vocabulary_items.all()[:self.pairs_count])
        
        if not vocabulary_items:
            raise ValueError("No vocabulary items available for this exercise")
        
        correct_pairs = {}
        target_words = []
        native_words = []
        
        for vocab in vocabulary_items:
            target_word = getattr(vocab, f'word_{target_language}', vocab.word_en)
            native_word = getattr(vocab, f'word_{native_language}', vocab.word_en)
            
            if target_word and native_word:
                correct_pairs[target_word] = native_word
                target_words.append(target_word)
                native_words.append(native_word)
        
        # Mélanger les listes
        random.shuffle(target_words)
        random.shuffle(native_words)
        
        return target_words, native_words, correct_pairs

    @classmethod
    def create_from_content_lesson(cls, content_lesson, vocabulary_ids=None, pairs_count=8):
        """Crée automatiquement un exercice d'association."""
        exercise = cls.objects.create(
            content_lesson=content_lesson,
            title_en=f"Matching Exercise: {content_lesson.title_en}",
            title_fr=f"Exercice d'Association: {content_lesson.title_fr}",
            title_es=f"Ejercicio de Asociación: {content_lesson.title_es}",
            title_nl=f"Oefeningoefening: {content_lesson.title_nl}",
            pairs_count=pairs_count
        )
        
        # Ajouter le vocabulaire
        if vocabulary_ids:
            vocabulary_items = VocabularyList.objects.filter(id__in=vocabulary_ids)
        else:
            vocabulary_items = content_lesson.vocabulary_lists.all()[:pairs_count]
        
        exercise.vocabulary_items.set(vocabulary_items)
        return exercise


class SpeakingExercise(models.Model):
    """Exercice de prononciation."""
    
    content_lesson = models.ForeignKey(ContentLesson, on_delete=models.CASCADE, related_name='speaking_exercises')
    vocabulary_items = models.ManyToManyField(VocabularyList, blank=True)

    class Meta:
        app_label = 'course'

    def __str__(self):
        return f"Speaking Exercise - {self.content_lesson.title_en}"


class ExerciseGrammarReordering(models.Model):
    """Exercice de réorganisation grammaticale."""
    
    content_lesson = models.ForeignKey(ContentLesson, on_delete=models.CASCADE, related_name='grammar_reordering_exercises')
    sentence_en = models.TextField(blank=False, null=False)
    sentence_fr = models.TextField(blank=False, null=False)
    sentence_es = models.TextField(blank=False, null=False)
    sentence_nl = models.TextField(blank=False, null=False)
    explanation = models.TextField(blank=True, null=True)
    hint = models.TextField(blank=True, null=True)

    class Meta:
        app_label = 'course'

    def __str__(self):
        return f"Grammar Reordering: {self.sentence_en[:50]}..."


class FillBlankExercise(models.Model):
    """Exercice de remplissage de blancs."""
    
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'), 
        ('advanced', 'Advanced'),
    ]

    content_lesson = models.ForeignKey(ContentLesson, on_delete=models.CASCADE, related_name='fill_blank_exercises')
    instructions = models.JSONField(default=dict, help_text="Instructions in multiple languages")
    sentences = models.JSONField(default=dict, help_text="Sentences with blanks in multiple languages")
    answer_options = models.JSONField(default=dict, help_text="Multiple choice options for each language")
    correct_answers = models.JSONField(default=dict, help_text="Correct answers for each language")
    hints = models.JSONField(default=dict, blank=True, help_text="Optional hints for each language")
    explanations = models.JSONField(default=dict, blank=True, help_text="Optional explanations for each language")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    order = models.PositiveIntegerField(default=1)
    tags = models.JSONField(default=list, blank=True, help_text="Tags for categorization")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'course'
        ordering = ['content_lesson__lesson__unit__order', 'content_lesson__lesson__order', 'order']

    def __str__(self):
        # Obtenir la première phrase disponible pour l'affichage
        if self.sentences:
            first_sentence = next(iter(self.sentences.values()), "No sentence")
            return f"Fill Blank: {first_sentence[:50]}..."
        return f"Fill Blank Exercise - {self.content_lesson.title_en}"

    def get_available_languages(self):
        """Retourne la liste des langues disponibles pour cet exercice."""
        return list(set(self.sentences.keys()) & set(self.correct_answers.keys()))

    def get_content_for_language(self, language='en'):
        """Retourne le contenu complet pour une langue spécifique."""
        return {
            'instruction': self.instructions.get(language, self.instructions.get('en', '')),
            'sentence': self.sentences.get(language, self.sentences.get('en', '')),
            'options': self.answer_options.get(language, self.answer_options.get('en', [])),
            'correct_answer': self.correct_answers.get(language, self.correct_answers.get('en', '')),
            'hint': self.hints.get(language, self.hints.get('en', '')),
            'explanation': self.explanations.get(language, self.explanations.get('en', ''))
        }

    def check_answer(self, user_answer, language='en'):
        """Vérifie si la réponse de l'utilisateur est correcte."""
        correct_answer = self.correct_answers.get(language, self.correct_answers.get('en', ''))
        return user_answer.strip().lower() == correct_answer.strip().lower()