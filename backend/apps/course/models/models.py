# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

"""
Modèles de l'application Course - Point d'entrée principal.

Cette refactorisation améliore l'organisation du code en divisant 
les modèles en modules logiques.

Structure:
- models/mixins.py: Mixins réutilisables
- models/core.py: Modèles principaux (Unit, Lesson, ContentLesson)
- models/exercises.py: Exercices et vocabulaire
- models/content.py: Contenu théorique
- models/tests.py: Tests et évaluations
"""

# Import de tous les modèles depuis les modules
from .mixins import *
from .core import *
from .exercises import *
from .content import *
from .tests import *
from .user_progress import *

# Réexport pour la compatibilité
__all__ = [
    # Mixins
    'MultilingualMixin',
    
    # Core models
    'Unit', 
    'Chapter',
    'Lesson', 
    'ContentLesson',
    
    # Exercise models
    'VocabularyList',
    'MultipleChoiceQuestion',
    'MatchingExercise', 
    'SpeakingExercise',
    'ExerciseGrammarReordering',
    'FillBlankExercise',
    
    # Content models
    'TheoryContent',
    
    # Test models
    'TestRecap',
    'TestRecapQuestion', 
    'TestRecapResult',
    
    # Progress models
    'UserProgress',
    'UnitProgress',
    'ChapterProgress',
    'LessonProgress',
    'UserActivity',
    'StudentCourse',
    'StudentLessonProgress',
    'StudentContentProgress',
    'LearningSession',
    'StudentReview',
    'LearningAnalytics'
]