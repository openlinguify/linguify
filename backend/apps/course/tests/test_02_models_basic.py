"""
Tests for Course models using Django TestCase
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.course.models import (
    Unit, Lesson, ContentLesson, VocabularyList, TheoryContent, Numbers,
    MatchingExercise, FillBlankExercise, SpeakingExercise
)


class UnitModelTests(TestCase):
    """Tests for Unit model"""
    
    def setUp(self):
        """Set up test data"""
        self.unit_data = {
            'title_en': "English Grammar Basics",
            'title_fr': "Bases de Grammaire Anglaise", 
            'title_es': "Fundamentos de Gramática Inglesa",
            'title_nl': "Engelse Grammatica Basis",
            'level': "B1",
            'order': 3
        }
    
    def test_unit_creation(self):
        """Test creating a unit"""
        unit = Unit.objects.create(**self.unit_data)
        self.assertEqual(unit.title_en, "English Grammar Basics")
        self.assertEqual(unit.level, "B1")
        self.assertEqual(unit.order, 3)
    
    def test_unit_str_representation(self):
        """Test unit string representation"""
        unit = Unit.objects.create(**self.unit_data)
        # Le __str__ de Unit utilise un format spécifique avec troncature
        str_repr = str(unit)
        self.assertIn("Unit 03", str_repr)
        self.assertIn("[B1]", str_repr)
        self.assertIn("English Grammar Basi", str_repr)  # Titre tronqué


class LessonModelTests(TestCase):
    """Tests for Lesson model"""
    
    def setUp(self):
        """Set up test data"""
        self.unit = Unit.objects.create(
            title_en="English Grammar Basics",
            title_fr="Bases de Grammaire Anglaise",
            title_es="Fundamentos de Gramática Inglesa", 
            title_nl="Engelse Grammatica Basis",
            level="B1",
            order=3
        )
        
        self.lesson_data = {
            'title_en': "Introduction to Verbs",
            'title_fr': "Introduction aux Verbes",
            'title_es': "Introducción a los Verbos",
            'title_nl': "Introductie tot Werkwoorden",
            'order': 1,
            'unit': self.unit,
            'lesson_type': 'grammar'
        }
    
    def test_lesson_creation(self):
        """Test creating a lesson"""
        lesson = Lesson.objects.create(**self.lesson_data)
        self.assertEqual(lesson.title_en, "Introduction to Verbs")
        self.assertEqual(lesson.order, 1)
        self.assertEqual(lesson.unit, self.unit)
        self.assertEqual(lesson.lesson_type, 'grammar')
    
    def test_lesson_str_representation(self):
        """Test lesson string representation"""
        lesson = Lesson.objects.create(**self.lesson_data)
        self.assertIn("Introduction to Verbs", str(lesson))
    
    def test_lesson_ordering(self):
        """Test lesson ordering"""
        lesson1 = Lesson.objects.create(**{**self.lesson_data, 'order': 1})
        lesson2 = Lesson.objects.create(**{**self.lesson_data, 'title_en': 'Lesson 2', 'order': 2})
        
        lessons = Lesson.objects.all()
        self.assertEqual(lessons[0], lesson1)
        self.assertEqual(lessons[1], lesson2)


class ContentLessonModelTests(TestCase):
    """Tests for ContentLesson model"""
    
    def setUp(self):
        """Set up test data"""
        self.unit = Unit.objects.create(
            title_en="English Grammar Basics",
            title_fr="Bases de Grammaire Anglaise",
            title_es="Fundamentos de Gramática Inglesa",
            title_nl="Engelse Grammatica Basis", 
            level="B1",
            order=3
        )
        
        self.lesson = Lesson.objects.create(
            title_en="Introduction to Verbs",
            title_fr="Introduction aux Verbes",
            title_es="Introducción a los Verbos",
            title_nl="Introductie tot Werkwoorden",
            order=1,
            unit=self.unit,
            lesson_type='grammar'
        )
        
        self.content_lesson_data = {
            'lesson': self.lesson,
            'content_type': 'Theory',
            'title_en': "Verb Tenses",
            'title_fr': "Temps des Verbes", 
            'title_es': "Tiempos Verbales",
            'title_nl': "Werkwoordtijden",
            'instruction_en': "Learn about different verb tenses",
            'instruction_fr': "Apprenez les différents temps des verbes",
            'instruction_es': "Aprende sobre los diferentes tiempos verbales",
            'instruction_nl': "Leer over verschillende werkwoordtijden",
            'estimated_duration': 5
        }
    
    def test_content_lesson_creation(self):
        """Test creating a content lesson"""
        content_lesson = ContentLesson.objects.create(**self.content_lesson_data)
        self.assertEqual(content_lesson.title_en, "Verb Tenses")
        self.assertEqual(content_lesson.content_type, 'theory')  # content_type est automatiquement converti en minuscules
        self.assertEqual(content_lesson.lesson, self.lesson)
    
    def test_content_lesson_str_representation(self):
        """Test content lesson string representation"""
        content_lesson = ContentLesson.objects.create(**self.content_lesson_data)
        self.assertIn("Verb Tenses", str(content_lesson))


class VocabularyListModelTests(TestCase):
    """Tests for VocabularyList model"""
    
    def setUp(self):
        """Set up test data"""
        self.unit = Unit.objects.create(
            title_en="English Grammar Basics",
            title_fr="Bases de Grammaire Anglaise",
            title_es="Fundamentos de Gramática Inglesa",
            title_nl="Engelse Grammatica Basis",
            level="B1", 
            order=3
        )
        
        self.lesson = Lesson.objects.create(
            title_en="Introduction to Verbs",
            title_fr="Introduction aux Verbes",
            title_es="Introducción a los Verbos",
            title_nl="Introductie tot Werkwoorden",
            order=1,
            unit=self.unit,
            lesson_type='vocabulary'
        )
        
        self.content_lesson = ContentLesson.objects.create(
            lesson=self.lesson,
            content_type='VocabularyList',
            title_en="Verb Vocabulary",
            title_fr="Vocabulaire des Verbes",
            title_es="Vocabulario de Verbos",
            title_nl="Werkwoord Vocabulaire",
            instruction_en="Learn verb vocabulary",
            instruction_fr="Apprendre le vocabulaire des verbes",
            instruction_es="Aprende vocabulario de verbos",
            instruction_nl="Leer werkwoord vocabulaire",
            estimated_duration=5
        )
    
    def test_vocabulary_list_creation(self):
        """Test creating a vocabulary list"""
        vocab_data = {
            'content_lesson': self.content_lesson,
            'word_en': "run",
            'word_fr': "courir",
            'word_es': "correr", 
            'word_nl': "rennen",
            'definition_en': "to move fast on foot",
            'definition_fr': "se déplacer rapidement à pied",
            'definition_es': "moverse rápido a pie",
            'definition_nl': "snel bewegen te voet"
        }
        
        vocab_list = VocabularyList.objects.create(**vocab_data)
        self.assertEqual(vocab_list.word_en, "run")
        self.assertEqual(vocab_list.content_lesson, self.content_lesson)
        self.assertEqual(vocab_list.definition_en, "to move fast on foot")


class MatchingExerciseModelTests(TestCase):
    """Tests for MatchingExercise model"""
    
    def setUp(self):
        """Set up test data"""
        self.unit = Unit.objects.create(
            title_en="English Grammar Basics",
            title_fr="Bases de Grammaire Anglaise",
            title_es="Fundamentos de Gramática Inglesa", 
            title_nl="Engelse Grammatica Basis",
            level="B1",
            order=3
        )
        
        self.lesson = Lesson.objects.create(
            title_en="Introduction to Verbs",
            title_fr="Introduction aux Verbes",
            title_es="Introducción a los Verbos",
            title_nl="Introductie tot Werkwoorden",
            order=1,
            unit=self.unit,
            lesson_type='exercise'
        )
        
        self.content_lesson = ContentLesson.objects.create(
            lesson=self.lesson,
            content_type='Matching',
            title_en="Match Verbs",
            title_fr="Associer les Verbes",
            title_es="Emparejar Verbos",
            title_nl="Werkwoorden Koppelen",
            instruction_en="Match English verbs with French translations",
            instruction_fr="Associez les verbes anglais avec les traductions françaises",
            instruction_es="Emparejar verbos ingleses con traducciones francesas",
            instruction_nl="Koppel Engelse werkwoorden met Franse vertalingen",
            estimated_duration=5
        )
    
    def test_matching_exercise_creation(self):
        """Test creating a matching exercise"""
        exercise_data = {
            'content_lesson': self.content_lesson,
            'difficulty': 'easy',
            'pairs_count': 4
        }
        
        exercise = MatchingExercise.objects.create(**exercise_data)
        self.assertEqual(exercise.content_lesson, self.content_lesson)
        self.assertEqual(exercise.difficulty, 'easy')
        self.assertEqual(exercise.pairs_count, 4)


class UtilityTests(TestCase):
    """Tests for utility functions and edge cases"""
    
    def test_model_field_max_lengths(self):
        """Test model field maximum lengths"""
        # Test title fields have reasonable max lengths
        unit = Unit._meta.get_field('title_en')
        self.assertGreaterEqual(unit.max_length, 100)
        
        lesson = Lesson._meta.get_field('title_en') 
        self.assertGreaterEqual(lesson.max_length, 100)
    
    def test_model_ordering(self):
        """Test model ordering works correctly"""
        unit = Unit.objects.create(
            title_en="Test Unit",
            title_fr="Unité Test",
            title_es="Unidad Prueba", 
            title_nl="Test Eenheid",
            level="A1",
            order=1
        )
        
        lesson1 = Lesson.objects.create(
            title_en="Lesson 1",
            title_fr="Leçon 1",
            title_es="Lección 1",
            title_nl="Les 1",
            order=2,
            unit=unit,
            lesson_type='theory'
        )
        
        lesson2 = Lesson.objects.create(
            title_en="Lesson 2", 
            title_fr="Leçon 2",
            title_es="Lección 2",
            title_nl="Les 2",
            order=1,
            unit=unit,
            lesson_type='exercise'
        )
        
        # Should be ordered by order field
        lessons = list(Lesson.objects.all())
        self.assertEqual(lessons[0], lesson2)  # order=1
        self.assertEqual(lessons[1], lesson1)  # order=2
    
    def test_timezone_aware_datetime_fields(self):
        """Test that datetime fields are timezone aware"""
        unit = Unit.objects.create(
            title_en="Test Unit",
            title_fr="Unité Test", 
            title_es="Unidad Prueba",
            title_nl="Test Eenheid",
            level="A1",
            order=1
        )
        
        if hasattr(unit, 'created_at'):
            self.assertIsNotNone(unit.created_at.tzinfo)
        if hasattr(unit, 'updated_at'):
            self.assertIsNotNone(unit.updated_at.tzinfo)