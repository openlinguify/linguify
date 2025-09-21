# Import de tous les modèles depuis le fichier models.py
from .models import (
    # Modèles principaux
    LanguagelearningItem,
    Language,
    UserLanguage,
    Lesson,
    UserLessonProgress,
    LanguageLearningSettings,
    UserLearningProfile,  # Nouveau modèle pour le profil d'apprentissage
    # Modèles de cours
    CourseUnit,
    CourseModule,
    ModuleProgress,
    UserCourseProgress,
    # Constantes
    LANGUAGE_CHOICES,
    LEVEL_CHOICES,
    OBJECTIVES_CHOICES,
    PROFICIENCY_LEVELS,
)

# Export de tous les modèles
__all__ = [
    # Modèles principaux
    'LanguagelearningItem',
    'Language',
    'UserLanguage',
    'Lesson',
    'UserLessonProgress',
    'LanguageLearningSettings',
    'UserLearningProfile',  # Nouveau modèle
    # Modèles de cours
    'CourseUnit',
    'CourseModule',
    'ModuleProgress',
    'UserCourseProgress',
    # Constantes
    'LANGUAGE_CHOICES',
    'LEVEL_CHOICES',
    'OBJECTIVES_CHOICES',
    'PROFICIENCY_LEVELS',
]