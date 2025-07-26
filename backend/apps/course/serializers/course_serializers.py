# -*- coding: utf-8 -*-
"""
Course API Serializers - Comprehensive REST API for Course app
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Sum

from ..models import (
    Unit, Chapter, Lesson, ContentLesson, TheoryContent,
    VocabularyList, MatchingExercise, MultipleChoiceQuestion,
    ExerciseGrammarReordering, FillBlankExercise, SpeakingExercise,
    TestRecap, TestRecapQuestion, TestRecapResult,
    UserProgress, UnitProgress, ChapterProgress, LessonProgress,
    UserActivity, StudentCourse, StudentLessonProgress,
    StudentContentProgress, LearningSession, StudentReview,
    LearningAnalytics
)

User = get_user_model()


class BaseMultilingualSerializer(serializers.ModelSerializer):
    """Base serializer for multilingual models"""
    
    def get_localized_content(self, obj, field_name, language='en'):
        """Get localized content for a field"""
        localized_field = f"{field_name}_{language}"
        return getattr(obj, localized_field, getattr(obj, f"{field_name}_en", ""))


# ==================== CORE MODELS ====================

class UnitListSerializer(serializers.ModelSerializer):
    """Serializer for Unit list view"""
    lessons_count = serializers.IntegerField(read_only=True)
    user_progress = serializers.SerializerMethodField()
    estimated_duration = serializers.SerializerMethodField()
    
    class Meta:
        model = Unit
        fields = [
            'id', 'title_en', 'title_fr', 'title_es', 'title_nl',
            'description_en', 'description_fr', 'description_es', 'description_nl',
            'level', 'order', 'is_free', 'estimated_duration',
            'lessons_count', 'user_progress'
        ]
    
    def get_estimated_duration(self, obj):
        """Get estimated duration for this unit"""
        return obj.get_estimated_duration()
    
    def get_user_progress(self, obj):
        """Get user progress for this unit"""
        user = self.context.get('request').user if self.context.get('request') else None
        if user and user.is_authenticated:
            try:
                progress = UnitProgress.objects.get(user=user, unit=obj)
                return {
                    'completed_lessons': progress.lessons_completed,
                    'total_lessons': progress.unit.get_total_lessons_count(),
                    'percentage': progress.progress_percentage,
                    'is_completed': progress.is_completed,
                    'current_lesson_id': None  # Cette propriété n'existe pas dans le modèle
                }
            except UnitProgress.DoesNotExist:
                return None
        return None


class UnitDetailSerializer(UnitListSerializer):
    """Detailed serializer for Unit"""
    lessons = serializers.SerializerMethodField()
    prerequisites = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta(UnitListSerializer.Meta):
        fields = UnitListSerializer.Meta.fields + ['lessons', 'prerequisites']
    
    def get_lessons(self, obj):
        """Get lessons for this unit"""
        lessons = obj.lesson_set.all().order_by('order')
        return LessonListSerializer(lessons, many=True, context=self.context).data


class ChapterListSerializer(BaseMultilingualSerializer):
    """Serializer for Chapter list view"""
    lessons_count = serializers.IntegerField(read_only=True)
    user_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Chapter
        fields = [
            'id', 'title', 'description', 'order', 'icon',
            'points', 'style', 'unit_id', 'lessons_count', 'user_progress'
        ]
    
    def get_user_progress(self, obj):
        """Get user progress for this chapter"""
        user = self.context.get('request').user if self.context.get('request') else None
        if user and user.is_authenticated:
            try:
                progress = ChapterProgress.objects.get(user=user, chapter=obj)
                return {
                    'completed_lessons': progress.lessons_completed,
                    'total_lessons': progress.chapter.lessons.count(),
                    'progress_percentage': progress.progress_percentage,
                    'is_completed': progress.status == 'completed',
                    'is_current': progress.status == 'in_progress',
                    'is_locked': progress.status == 'locked'
                }
            except ChapterProgress.DoesNotExist:
                return None
        return None


class ChapterDetailSerializer(ChapterListSerializer):
    """Detailed serializer for Chapter"""
    lessons = serializers.SerializerMethodField()
    unit = UnitListSerializer(read_only=True)
    
    class Meta(ChapterListSerializer.Meta):
        fields = ChapterListSerializer.Meta.fields + ['lessons', 'unit']
    
    def get_lessons(self, obj):
        """Get lessons for this chapter"""
        lessons = obj.lesson_set.all().order_by('order')
        return LessonListSerializer(lessons, many=True, context=self.context).data


class LessonListSerializer(serializers.ModelSerializer):
    """Serializer for Lesson list view"""
    user_progress = serializers.SerializerMethodField()
    content_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'order', 'estimated_duration',
            'user_progress', 'content_count'
        ]
    
    def get_user_progress(self, obj):
        """Get user progress for this lesson"""
        user = self.context.get('request').user if self.context.get('request') else None
        if user and user.is_authenticated:
            try:
                progress = LessonProgress.objects.get(user=user, lesson=obj)
                return {
                    'is_completed': progress.is_completed,
                    'completed_at': progress.completed_at,
                    'time_spent': progress.time_spent,
                    'score': progress.score
                }
            except LessonProgress.DoesNotExist:
                return None
        return None
    
    def get_content_count(self, obj):
        """Get content count for this lesson"""
        return obj.contentlesson_set.count()


class LessonDetailSerializer(LessonListSerializer):
    """Detailed serializer for Lesson"""
    content = serializers.SerializerMethodField()
    unit = UnitListSerializer(read_only=True)
    chapter = ChapterListSerializer(read_only=True)
    
    class Meta(LessonListSerializer.Meta):
        fields = LessonListSerializer.Meta.fields + ['content', 'unit', 'chapter']
    
    def get_content(self, obj):
        """Get all content for this lesson"""
        content_lessons = obj.contentlesson_set.all().order_by('order')
        return ContentLessonSerializer(content_lessons, many=True, context=self.context).data


# ==================== CONTENT MODELS ====================

class ContentLessonSerializer(serializers.ModelSerializer):
    """Serializer for ContentLesson"""
    vocabulary_lists = serializers.SerializerMethodField()
    theory_content = serializers.SerializerMethodField()
    exercises = serializers.SerializerMethodField()
    
    class Meta:
        model = ContentLesson
        fields = [
            'id', 'content_type', 'order', 'vocabulary_lists',
            'theory_content', 'exercises'
        ]
    
    def get_vocabulary_lists(self, obj):
        """Get vocabulary lists for this content"""
        if obj.content_type == 'vocabulary':
            vocab_lists = obj.vocabularylist_set.all()
            return VocabularyListSerializer(vocab_lists, many=True).data
        return []
    
    def get_theory_content(self, obj):
        """Get theory content"""
        if obj.content_type == 'theory':
            theory = obj.theorycontent_set.all()
            return TheoryContentSerializer(theory, many=True).data
        return []
    
    def get_exercises(self, obj):
        """Get exercises for this content"""
        exercises = []
        
        # Multiple choice questions
        mcq = obj.multiplechoicequestion_set.all()
        if mcq.exists():
            exercises.extend([{
                'type': 'multiple_choice',
                'data': MultipleChoiceQuestionSerializer(mcq, many=True).data
            }])
        
        # Matching exercises
        matching = obj.matchingexercise_set.all()
        if matching.exists():
            exercises.extend([{
                'type': 'matching',
                'data': MatchingExerciseSerializer(matching, many=True).data
            }])
        
        # Fill blank exercises
        fill_blank = obj.fillblankexercise_set.all()
        if fill_blank.exists():
            exercises.extend([{
                'type': 'fill_blank',
                'data': FillBlankExerciseSerializer(fill_blank, many=True).data
            }])
        
        # Grammar reordering
        grammar = obj.exercisegrammarreordering_set.all()
        if grammar.exists():
            exercises.extend([{
                'type': 'grammar_reordering',
                'data': ExerciseGrammarReorderingSerializer(grammar, many=True).data
            }])
        
        # Speaking exercises
        speaking = obj.speakingexercise_set.all()
        if speaking.exists():
            exercises.extend([{
                'type': 'speaking',
                'data': SpeakingExerciseSerializer(speaking, many=True).data
            }])
        
        return exercises


class VocabularyListSerializer(BaseMultilingualSerializer):
    """Serializer for VocabularyList"""
    
    class Meta:
        model = VocabularyList
        fields = [
            'id', 'french_word', 'english_translation', 'spanish_translation',
            'dutch_translation', 'pronunciation', 'word_type', 'difficulty_level',
            'example_sentence_fr', 'example_sentence_en', 'example_sentence_es',
            'example_sentence_nl', 'audio_file'
        ]


class TheoryContentSerializer(BaseMultilingualSerializer):
    """Serializer for TheoryContent"""
    
    class Meta:
        model = TheoryContent
        fields = [
            'id', 'title_en', 'title_fr', 'title_es', 'title_nl',
            'content_en', 'content_fr', 'content_es', 'content_nl',
            'content_type', 'difficulty_level', 'available_languages'
        ]


# ==================== EXERCISE MODELS ====================

class MultipleChoiceQuestionSerializer(serializers.ModelSerializer):
    """Serializer for MultipleChoiceQuestion"""
    
    class Meta:
        model = MultipleChoiceQuestion
        fields = [
            'id', 'question_text', 'option_a', 'option_b', 'option_c',
            'option_d', 'correct_answer', 'explanation'
        ]


class MatchingExerciseSerializer(serializers.ModelSerializer):
    """Serializer for MatchingExercise"""
    
    class Meta:
        model = MatchingExercise
        fields = [
            'id', 'left_items', 'right_items', 'correct_matches',
            'instructions', 'difficulty_level'
        ]


class FillBlankExerciseSerializer(serializers.ModelSerializer):
    """Serializer for FillBlankExercise"""
    
    class Meta:
        model = FillBlankExercise
        fields = [
            'id', 'sentence_with_blanks', 'correct_answers', 'instructions',
            'hints', 'difficulty_level'
        ]


class ExerciseGrammarReorderingSerializer(serializers.ModelSerializer):
    """Serializer for ExerciseGrammarReordering"""
    
    class Meta:
        model = ExerciseGrammarReordering
        fields = [
            'id', 'scrambled_sentence', 'correct_order', 'difficulty_level'
        ]


class SpeakingExerciseSerializer(serializers.ModelSerializer):
    """Serializer for SpeakingExercise"""
    
    class Meta:
        model = SpeakingExercise
        fields = [
            'id', 'text_to_pronounce', 'audio_example', 'pronunciation_tips',
            'difficulty_level', 'target_language'
        ]


# ==================== TEST MODELS ====================

class TestRecapSerializer(serializers.ModelSerializer):
    """Serializer for TestRecap"""
    questions = serializers.SerializerMethodField()
    
    class Meta:
        model = TestRecap
        fields = [
            'id', 'question', 'questions'
        ]
    
    def get_questions(self, obj):
        """Get questions for this test"""
        questions = obj.testrecapquestion_set.all()
        return TestRecapQuestionSerializer(questions, many=True).data


class TestRecapQuestionSerializer(serializers.ModelSerializer):
    """Serializer for TestRecapQuestion"""
    
    class Meta:
        model = TestRecapQuestion
        fields = [
            'id', 'question_text', 'question_type', 'options',
            'correct_answer', 'explanation', 'points', 'order'
        ]


class TestRecapResultSerializer(serializers.ModelSerializer):
    """Serializer for TestRecapResult"""
    test_recap = TestRecapSerializer(read_only=True)
    
    class Meta:
        model = TestRecapResult
        fields = [
            'id', 'user', 'test_recap', 'score', 'total_points',
            'percentage', 'completed_at', 'time_spent', 'answers'
        ]
        read_only_fields = ['user', 'completed_at']


# ==================== PROGRESS MODELS ====================

class UserProgressSerializer(serializers.ModelSerializer):
    """Serializer for UserProgress"""
    
    class Meta:
        model = UserProgress
        fields = [
            'id', 'user', 'overall_progress', 'completed_lessons_count',
            'streak_days', 'total_xp', 'current_level',
            'last_activity_date', 'total_study_time'
        ]
        read_only_fields = ['user']


class UnitProgressSerializer(serializers.ModelSerializer):
    """Serializer for UnitProgress"""
    unit = UnitListSerializer(read_only=True)
    total_lessons = serializers.SerializerMethodField()
    
    class Meta:
        model = UnitProgress
        fields = [
            'id', 'user', 'unit', 'lessons_completed', 'chapters_completed',
            'progress_percentage', 'status', 'is_completed', 'is_current', 'is_locked',
            'total_lessons', 'started_at', 'completed_at'
        ]
        read_only_fields = ['user']
    
    def get_total_lessons(self, obj):
        """Get total lessons count for this unit"""
        return obj.unit.get_total_lessons_count()


class ChapterProgressSerializer(serializers.ModelSerializer):
    """Serializer for ChapterProgress"""
    chapter = ChapterListSerializer(read_only=True)
    
    class Meta:
        model = ChapterProgress
        fields = [
            'id', 'user', 'chapter', 'lessons_completed',
            'progress_percentage', 'status', 'started_at', 'completed_at'
        ]
        read_only_fields = ['user']


class LessonProgressSerializer(serializers.ModelSerializer):
    """Serializer for LessonProgress"""
    lesson = LessonListSerializer(read_only=True)
    
    class Meta:
        model = LessonProgress
        fields = [
            'id', 'user', 'lesson', 'is_completed', 'completed_at',
            'time_spent', 'score'
        ]
        read_only_fields = ['user', 'completed_at']


# ==================== STUDENT MODELS ====================

class StudentCourseSerializer(serializers.ModelSerializer):
    """Serializer for StudentCourse"""
    course_details = serializers.SerializerMethodField()
    progress_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentCourse
        fields = [
            'id', 'student', 'course_id', 'enrolled_at', 'completed_at',
            'progress_percentage', 'is_completed', 'course_details',
            'progress_summary'
        ]
        read_only_fields = ['student', 'enrolled_at']
    
    def get_course_details(self, obj):
        """Get course details from CMS"""
        # This would integrate with CMS to get course details
        return {
            'title': f"Course {obj.course_id}",
            'description': "Course description from CMS",
            'level': "A1-A2",
            'duration': "4 weeks"
        }
    
    def get_progress_summary(self, obj):
        """Get progress summary for this course"""
        return {
            'completed_lessons': 0,  # Calculate from lessons
            'total_lessons': 0,      # Get from course structure
            'time_spent': 0,         # Sum from learning sessions
            'last_activity': obj.enrolled_at  # Last activity date
        }


class LearningSessionSerializer(serializers.ModelSerializer):
    """Serializer for LearningSession"""
    
    class Meta:
        model = LearningSession
        fields = [
            'id', 'student', 'lesson', 'started_at', 'ended_at',
            'duration_seconds', 'exercises_completed', 'score'
        ]
        read_only_fields = ['student', 'started_at']


class StudentReviewSerializer(serializers.ModelSerializer):
    """Serializer for StudentReview"""
    lesson = LessonListSerializer(read_only=True)
    
    class Meta:
        model = StudentReview
        fields = [
            'id', 'student', 'lesson', 'rating', 'comment',
            'difficulty_rating', 'created_at'
        ]
        read_only_fields = ['student', 'created_at']


# ==================== ANALYTICS MODELS ====================

class LearningAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for LearningAnalytics"""
    
    class Meta:
        model = LearningAnalytics
        fields = [
            'id', 'student', 'date', 'lessons_completed', 'time_spent_minutes',
            'exercises_completed', 'average_score', 'streak_days'
        ]
        read_only_fields = ['student', 'date']


# ==================== SUBMISSION SERIALIZERS ====================

class LessonCompletionSerializer(serializers.Serializer):
    """Serializer for lesson completion"""
    lesson_id = serializers.IntegerField()
    time_spent = serializers.IntegerField(help_text="Time spent in seconds")
    score = serializers.FloatField(min_value=0, max_value=100, required=False)
    exercises_completed = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        help_text="List of completed exercises with results"
    )


class ExerciseSubmissionSerializer(serializers.Serializer):
    """Serializer for exercise submission"""
    exercise_type = serializers.CharField()
    exercise_id = serializers.IntegerField()
    answer = serializers.JSONField()
    time_spent = serializers.IntegerField(help_text="Time spent in seconds")


class CourseEnrollmentSerializer(serializers.Serializer):
    """Serializer for course enrollment"""
    course_id = serializers.IntegerField()
    enrollment_method = serializers.CharField(default='manual')