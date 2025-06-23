# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

"""
Modèles de tests pour l'application Course.
Contient TestRecap, TestRecapQuestion et TestRecapResult.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from apps.authentication.models import User
from .core import Lesson, ContentLesson
from .exercises import VocabularyList, MultipleChoiceQuestion, MatchingExercise
import json
import random
import logging

logger = logging.getLogger(__name__)


class TestRecap(models.Model):
    """Test récapitulatif d'une leçon."""
    
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='test_recaps')
    title_en = models.CharField(max_length=200, blank=False, null=False)
    title_fr = models.CharField(max_length=200, blank=False, null=False)
    title_es = models.CharField(max_length=200, blank=False, null=False)
    title_nl = models.CharField(max_length=200, blank=False, null=False)
    description_en = models.TextField(blank=True, null=True)
    description_fr = models.TextField(blank=True, null=True)
    description_es = models.TextField(blank=True, null=True)
    description_nl = models.TextField(blank=True, null=True)
    passing_score = models.FloatField(
        default=0.6, 
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Minimum score to pass (0.0 to 1.0)"
    )
    time_limit = models.PositiveIntegerField(
        default=10, 
        help_text="Time limit in minutes"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'course'
        ordering = ['lesson__unit__order', 'lesson__order']

    def __str__(self):
        return f"Test: {self.title_en} - {self.lesson.title_en}"

    @property
    def title(self):
        """Property pour compatibilité avec les templates"""
        return self.title_fr or self.title_en
    
    @property
    def description(self):
        """Property pour compatibilité avec les templates"""
        return self.description_fr or self.description_en

    def total_points(self):
        """Calcule le total des points possibles."""
        return sum(question.points for question in self.questions.all())

    def get_title_for_language(self, language='en'):
        """Récupère le titre dans la langue spécifiée."""
        return getattr(self, f'title_{language}', self.title_en)

    def get_description_for_language(self, language='en'):
        """Récupère la description dans la langue spécifiée."""
        return getattr(self, f'description_{language}', self.description_en)


class TestRecapQuestion(models.Model):
    """Question d'un test récapitulatif."""
    
    QUESTION_TYPES = [
        ('vocabulary', 'Vocabulary'),
        ('multiple_choice', 'Multiple Choice'),
        ('matching', 'Matching'),
        ('fill_blank', 'Fill in the Blank'),
    ]

    test_recap = models.ForeignKey(TestRecap, on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    order = models.PositiveIntegerField(default=1)
    points = models.PositiveIntegerField(default=1)
    
    # Relations vers les exercices spécifiques
    vocabulary_item = models.ForeignKey(VocabularyList, on_delete=models.CASCADE, null=True, blank=True)
    multiple_choice_question = models.ForeignKey(MultipleChoiceQuestion, on_delete=models.CASCADE, null=True, blank=True)
    matching_exercise = models.ForeignKey(MatchingExercise, on_delete=models.CASCADE, null=True, blank=True)
    
    # Données JSON pour questions personnalisées
    custom_question_data = models.JSONField(default=dict, blank=True)

    class Meta:
        app_label = 'course'
        ordering = ['test_recap', 'order']
        unique_together = [['test_recap', 'order']]

    def __str__(self):
        return f"Question {self.order}: {self.question_type} - {self.test_recap.title_en}"

    def get_question_data(self, language_code='en', force_real_data=False):
        """Récupère les données de la question selon son type."""
        try:
            if self.question_type == 'vocabulary' and self.vocabulary_item:
                return self._get_vocabulary_question_data(language_code)
            elif self.question_type == 'multiple_choice' and self.multiple_choice_question:
                return self._get_multiple_choice_question_data(language_code)
            elif self.question_type == 'matching' and self.matching_exercise:
                return self._get_matching_question_data(language_code)
            elif self.custom_question_data:
                return self.custom_question_data.get(language_code, self.custom_question_data.get('en', {}))
            else:
                # Données de démonstration si aucune donnée réelle n'est disponible
                if not force_real_data:
                    return self._get_demo_question_data(language_code)
                else:
                    return {'error': 'No question data available'}
                    
        except Exception as e:
            logger.error(f"Error getting question data: {str(e)}")
            return {'error': str(e)}

    def _get_vocabulary_question_data(self, language_code):
        """Génère les données pour une question de vocabulaire."""
        vocab = self.vocabulary_item
        target_word = getattr(vocab, f'word_{language_code}', vocab.word_en)
        
        # Générer des options multiples
        other_vocab = VocabularyList.objects.exclude(id=vocab.id).order_by('?')[:3]
        options = [getattr(v, f'definition_{language_code}', v.definition_en) for v in other_vocab]
        correct_answer = getattr(vocab, f'definition_{language_code}', vocab.definition_en)
        options.append(correct_answer)
        random.shuffle(options)
        
        return {
            'question': f"What does '{target_word}' mean?",
            'options': options,
            'correct_answer': correct_answer,
            'type': 'vocabulary'
        }

    def _get_multiple_choice_question_data(self, language_code):
        """Génère les données pour une question à choix multiples."""
        mcq = self.multiple_choice_question
        question = getattr(mcq, f'question_{language_code}', mcq.question_en)
        correct_answer = getattr(mcq, f'correct_answer_{language_code}', mcq.correct_answer_en)
        
        # Récupérer les fausses réponses
        fake_answers = []
        for i in range(1, 5):
            fake_answer = getattr(mcq, f'fake_answer{i}_{language_code}', '')
            if fake_answer:
                fake_answers.append(fake_answer)
        
        options = fake_answers + [correct_answer]
        random.shuffle(options)
        
        return {
            'question': question,
            'options': options,
            'correct_answer': correct_answer,
            'type': 'multiple_choice'
        }

    def _get_matching_question_data(self, language_code):
        """Génère les données pour un exercice d'association."""
        matching = self.matching_exercise
        # Pour simplifier, on prend juste quelques paires de l'exercice
        exercise_data = matching.get_exercise_data('en', language_code)
        
        return {
            'question': f"Match the following pairs:",
            'pairs': exercise_data.get('correct_pairs', {}),
            'type': 'matching'
        }

    def _get_demo_question_data(self, language_code):
        """Génère des données de démonstration pour les tests."""
        demo_questions = {
            'en': {
                'vocabulary': {
                    'question': "What does 'bonjour' mean?",
                    'options': ['Good morning', 'Good evening', 'Goodbye', 'Thank you'],
                    'correct_answer': 'Good morning',
                    'type': 'vocabulary'
                },
                'multiple_choice': {
                    'question': "Which is the correct form?",
                    'options': ['Je suis', 'Je es', 'Je est', 'Je sont'],
                    'correct_answer': 'Je suis',
                    'type': 'multiple_choice'
                }
            },
            'fr': {
                'vocabulary': {
                    'question': "Que signifie 'hello' ?",
                    'options': ['Bonjour', 'Bonsoir', 'Au revoir', 'Merci'],
                    'correct_answer': 'Bonjour',
                    'type': 'vocabulary'
                },
                'multiple_choice': {
                    'question': "Quelle est la forme correcte ?",
                    'options': ['Je suis', 'Je es', 'Je est', 'Je sont'],
                    'correct_answer': 'Je suis',
                    'type': 'multiple_choice'
                }
            }
        }
        
        lang_data = demo_questions.get(language_code, demo_questions['en'])
        question_data = lang_data.get(self.question_type, lang_data['vocabulary'])
        
        return question_data


class TestRecapResult(models.Model):
    """Résultat d'un test récapitulatif."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_results')
    test_recap = models.ForeignKey(TestRecap, on_delete=models.CASCADE, related_name='results')
    score = models.FloatField(help_text="Score as percentage (0-100)")
    passed = models.BooleanField(default=False)
    time_spent = models.PositiveIntegerField(help_text="Time spent in seconds")
    detailed_results = models.JSONField(default=dict, help_text="Detailed results per question")
    completed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'course'
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.user.username} - {self.test_recap.title_en} - {self.score}%"

    @property
    def correct_questions(self):
        """Calcule le nombre de questions correctes."""
        if not self.detailed_results:
            return 0
        return sum(1 for result in self.detailed_results.values() if result.get('correct', False))

    @property
    def total_questions(self):
        """Calcule le nombre total de questions."""
        return len(self.detailed_results) if self.detailed_results else 0

    def calculate_score(self):
        """Calcule le score basé sur les résultats détaillés."""
        if not self.detailed_results:
            return 0.0
        
        total_points = 0
        earned_points = 0
        
        for question_id, result in self.detailed_results.items():
            points = result.get('points', 1)
            total_points += points
            if result.get('correct', False):
                earned_points += points
        
        return (earned_points / total_points * 100) if total_points > 0 else 0.0

    def save(self, *args, **kwargs):
        """Surcharge de save pour calculer automatiquement le score et le statut."""
        if not self.score and self.detailed_results:
            self.score = self.calculate_score()
        
        # Déterminer si le test est réussi
        self.passed = self.score >= (self.test_recap.passing_score * 100)
        
        super().save(*args, **kwargs)