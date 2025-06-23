# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

"""
Modèles de l'application Course - Structure modulaire organisée.

Cette organisation améliore la lisibilité et la maintenance du code.
"""

# Import du mixin de base
from .mixins import MultilingualMixin

# Import des modèles principaux
from .core import Unit, Chapter, Lesson, ContentLesson

# Import des exercices et contenus
from .exercises import (
    VocabularyList,
    MultipleChoiceQuestion, 
    MatchingExercise,
    SpeakingExercise,
    ExerciseGrammarReordering,
    FillBlankExercise
)

# Import du contenu théorique
from .content import TheoryContent

# Import des tests
from .tests import TestRecap, TestRecapQuestion, TestRecapResult

# Import des modèles de progression utilisateur
from .user_progress import (
    UserProgress,
    UnitProgress, 
    ChapterProgress,
    LessonProgress,
    UserActivity
)

# Export de tous les modèles pour l'importation externe
__all__ = [
    'MultilingualMixin',
    'Unit', 
    'Chapter',
    'Lesson', 
    'ContentLesson',
    'VocabularyList',
    'MultipleChoiceQuestion',
    'MatchingExercise', 
    'SpeakingExercise',
    'TheoryContent',
    'ExerciseGrammarReordering',
    'FillBlankExercise',
    'TestRecap',
    'TestRecapQuestion', 
    'TestRecapResult',
    'UserProgress',
    'UnitProgress',
    'ChapterProgress', 
    'LessonProgress',
    'UserActivity'
]