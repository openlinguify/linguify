# -*- coding: utf-8 -*-
"""
Course Serializers - Import all serializers for easy access
"""

# Settings serializers (existing)
from .settings_serializers import LearningSettingsSerializer

# Course API serializers (new)
from .course_serializers import *

__all__ = [
    # Settings serializers
    'LearningSettingsSerializer',
    
    # Core model serializers
    'UnitListSerializer', 'UnitDetailSerializer',
    'ChapterListSerializer', 'ChapterDetailSerializer', 
    'LessonListSerializer', 'LessonDetailSerializer',
    'ContentLessonSerializer',
    
    # Content serializers
    'VocabularyListSerializer', 'TheoryContentSerializer',
    
    # Exercise serializers
    'MultipleChoiceQuestionSerializer', 'MatchingExerciseSerializer',
    'FillBlankExerciseSerializer', 'ExerciseGrammarReorderingSerializer',
    'SpeakingExerciseSerializer',
    
    # Test serializers
    'TestRecapSerializer', 'TestRecapQuestionSerializer',
    'TestRecapResultSerializer',
    
    # Progress serializers
    'UserProgressSerializer', 'UnitProgressSerializer',
    'ChapterProgressSerializer', 'LessonProgressSerializer',
    
    # Student serializers
    'StudentCourseSerializer', 'LearningSessionSerializer',
    'StudentReviewSerializer', 'LearningAnalyticsSerializer',
    
    # Submission serializers
    'LessonCompletionSerializer', 'ExerciseSubmissionSerializer',
    'CourseEnrollmentSerializer',
]