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
from .models import *

# Réexport pour la compatibilité
__all__ = [
    'MultilingualMixin',
    'Unit', 
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
    'TestRecapResult'
]