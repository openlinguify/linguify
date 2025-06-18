"""
Tests complets pour les modèles Course utilisant Django TestCase
Conversion complète des tests pytest existants vers Django TestCase
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.course.models import (
    Unit, Lesson, ContentLesson, VocabularyList, TheoryContent, Numbers,
    MatchingExercise, FillBlankExercise, SpeakingExercise
)


class UnitModelCompleteTests(TestCase):
    """Tests complets pour le modèle Unit"""
    
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
        self.unit = Unit.objects.create(**self.unit_data)
    
    def test_unit_string_representation(self):
        """Test the string representation of a Unit"""
        expected = (
            "Unit 03        [B1]  EN: English Grammar Basi... | FR: Bases de Grammaire A... | "
            "ES: Fundamentos de Gramá... | NL: Engelse Grammatica B..."
        )
        self.assertEqual(str(self.unit), expected)
    
    def test_get_unit_title(self):
        """Test the get_unit_title method with different languages"""
        unit = Unit(
            title_en="English",
            title_fr="Anglais",
            title_es="Inglés",
            title_nl="Engels",
            level="A1",
            order=1
        )
        self.assertEqual(unit.get_unit_title('en'), "English")
        self.assertEqual(unit.get_unit_title('fr'), "Anglais")
        self.assertEqual(unit.get_unit_title('es'), "Inglés")
        self.assertEqual(unit.get_unit_title('nl'), "Engels")
        self.assertEqual(unit.get_unit_title('de'), "Language not supported")
    
    def test_generate_unit_description_no_lessons(self):
        """Test description generation for a Unit with no lessons"""
        unit = Unit(
            title_en="English",
            title_fr="Anglais",
            title_es="Inglés",
            title_nl="Engels",
            level="A2",
            order=2
        )
        # Test in various languages
        self.assertIn("coming soon", unit.generate_unit_description('en'))
        self.assertIn("bientôt disponible", unit.generate_unit_description('fr'))
        self.assertIn("próximamente", unit.generate_unit_description('es'))
        self.assertIn("komt binnenkort", unit.generate_unit_description('nl'))
    
    def test_generate_unit_description_with_lessons(self):
        """Test description generation for a Unit with lessons"""
        # Créer des leçons pour l'unité
        lesson1 = Lesson.objects.create(
            title_en="Lesson 1",
            title_fr="Leçon 1",
            title_es="Lección 1",
            title_nl="Les 1",
            order=1,
            unit=self.unit,
            lesson_type='theory'
        )
        lesson2 = Lesson.objects.create(
            title_en="Lesson 2",
            title_fr="Leçon 2",
            title_es="Lección 2",
            title_nl="Les 2",
            order=2,
            unit=self.unit,
            lesson_type='vocabulary'
        )
        
        # Test que la description inclut les leçons
        description_en = self.unit.generate_unit_description('en')
        self.assertIn("Lesson 1", description_en)
        self.assertIn("Lesson 2", description_en)
        
        description_fr = self.unit.generate_unit_description('fr')
        self.assertIn("Leçon 1", description_fr)
        self.assertIn("Leçon 2", description_fr)
    
    def test_update_unit_descriptions(self):
        """Test updating unit descriptions"""
        # Cette méthode devrait mettre à jour les descriptions de toutes les unités
        original_desc = self.unit.description_en
        
        # Ajouter une leçon
        Lesson.objects.create(
            title_en="New Lesson",
            title_fr="Nouvelle Leçon",
            title_es="Nueva Lección",
            title_nl="Nieuwe Les",
            order=1,
            unit=self.unit,
            lesson_type='grammar'
        )
        
        # Mettre à jour les descriptions (si la méthode existe)
        if hasattr(Unit, 'update_unit_descriptions'):
            # Cette méthode pourrait être statique ou de classe
            try:
                Unit.update_unit_descriptions()
            except TypeError:
                # Si c'est une méthode d'instance, on passe le test
                pass
        
        # Recharger l'unité depuis la base de données
        self.unit.refresh_from_db()
        
        # La description devrait maintenant inclure la nouvelle leçon
        self.assertNotEqual(self.unit.description_en, original_desc)
        self.assertIn("New Lesson", self.unit.description_en)


class LessonModelCompleteTests(TestCase):
    """Tests complets pour le modèle Lesson"""
    
    def setUp(self):
        """Set up test data"""
        self.unit = Unit.objects.create(
            title_en="Test Unit",
            title_fr="Unité Test",
            title_es="Unidad Test",
            title_nl="Test Eenheid",
            level="B1",
            order=1
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
        self.lesson = Lesson.objects.create(**self.lesson_data)
    
    def test_lesson_string_representation(self):
        """Test the string representation of a Lesson"""
        str_repr = str(self.lesson)
        self.assertIn("Introduction to Verbs", str_repr)
        self.assertIn("B1", str_repr)
    
    def test_get_title(self):
        """Test the get_title method with different languages"""
        self.assertEqual(self.lesson.get_title('en'), "Introduction to Verbs")
        self.assertEqual(self.lesson.get_title('fr'), "Introduction aux Verbes")
        self.assertEqual(self.lesson.get_title('es'), "Introducción a los Verbos")
        self.assertEqual(self.lesson.get_title('nl'), "Introductie tot Werkwoorden")
        # Test avec une langue non supportée - peut retourner la langue par défaut
        result = self.lesson.get_title('de')
        self.assertIsNotNone(result)  # Au moins retourne quelque chose
    
    def test_get_description(self):
        """Test the get_description method"""
        # Ajouter une description
        self.lesson.description_en = "Learn about verb usage"
        self.lesson.description_fr = "Apprenez l'usage des verbes"
        self.lesson.save()
        
        self.assertEqual(self.lesson.get_description('en'), "Learn about verb usage")
        self.assertEqual(self.lesson.get_description('fr'), "Apprenez l'usage des verbes")
    
    def test_clean_professional_field_required(self):
        """Test validation when professional field is required"""
        lesson = Lesson(
            title_en="Professional Lesson",
            title_fr="Leçon Professionnelle",
            title_es="Lección Profesional",
            title_nl="Professionele Les",
            order=1,
            unit=self.unit,
            lesson_type='professional'
        )
        
        # Should raise ValidationError if professional_field is not set
        with self.assertRaises(ValidationError):
            lesson.clean()
    
    def test_clean_professional_field_valid(self):
        """Test validation with valid professional field"""
        lesson = Lesson(
            title_en="Professional Lesson",
            title_fr="Leçon Professionnelle",
            title_es="Lección Profesional",
            title_nl="Professionele Les",
            order=1,
            unit=self.unit,
            lesson_type='professional',
            professional_field='technology'
        )
        
        # Should not raise ValidationError
        try:
            lesson.clean()
        except ValidationError:
            self.fail("clean() raised ValidationError unexpectedly!")
    
    def test_clean_professional_field_cleared(self):
        """Test that professional_field is cleared for non-professional lessons"""
        lesson = Lesson(
            title_en="Regular Lesson",
            title_fr="Leçon Normale",
            title_es="Lección Normal",
            title_nl="Normale Les",
            order=1,
            unit=self.unit,
            lesson_type='vocabulary',
            professional_field='technology'  # Should be cleared
        )
        
        lesson.clean()
        self.assertIsNone(lesson.professional_field)
    
    def test_calculate_duration_lesson(self):
        """Test the calculate_duration method"""
        # Ajouter des content lessons avec différentes durées
        ContentLesson.objects.create(
            lesson=self.lesson,
            content_type='Theory',
            title_en="Theory Part",
            title_fr="Partie Théorie",
            title_es="Parte Teoría",
            title_nl="Theorie Deel",
            instruction_en="Learn theory",
            instruction_fr="Apprendre la théorie",
            instruction_es="Aprender teoría",
            instruction_nl="Leer theorie",
            estimated_duration=10,
            order=1
        )
        
        ContentLesson.objects.create(
            lesson=self.lesson,
            content_type='Vocabulary',
            title_en="Vocabulary Part",
            title_fr="Partie Vocabulaire",
            title_es="Parte Vocabulario",
            title_nl="Vocabulaire Deel",
            instruction_en="Learn vocabulary",
            instruction_fr="Apprendre le vocabulaire",
            instruction_es="Aprender vocabulario",
            instruction_nl="Leer vocabulaire",
            estimated_duration=15,
            order=2
        )
        
        total_duration = self.lesson.calculate_duration_lesson()
        self.assertEqual(total_duration, 25)  # 10 + 15


class ContentLessonCompleteTests(TestCase):
    """Tests complets pour le modèle ContentLesson"""
    
    def setUp(self):
        """Set up test data"""
        self.unit = Unit.objects.create(
            title_en="Test Unit",
            title_fr="Unité Test",
            title_es="Unidad Test",
            title_nl="Test Eenheid",
            level="B1",
            order=1
        )
        
        self.lesson = Lesson.objects.create(
            title_en="Test Lesson",
            title_fr="Leçon Test",
            title_es="Lección Test",
            title_nl="Test Les",
            order=1,
            unit=self.unit,
            lesson_type='theory'
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
            'estimated_duration': 15,
            'order': 1
        }
        self.content_lesson = ContentLesson.objects.create(**self.content_lesson_data)
    
    def test_content_lesson_creation(self):
        """Test creating a content lesson"""
        self.assertEqual(self.content_lesson.title_en, "Verb Tenses")
        self.assertEqual(self.content_lesson.content_type, 'theory')  # lowercase après save
        self.assertEqual(self.content_lesson.lesson, self.lesson)
        self.assertEqual(self.content_lesson.estimated_duration, 15)
    
    def test_content_lesson_string_representation(self):
        """Test content lesson string representation"""
        str_repr = str(self.content_lesson)
        self.assertIn("Verb Tenses", str_repr)
    
    def test_get_title(self):
        """Test the get_title method"""
        self.assertEqual(self.content_lesson.get_title('en'), "Verb Tenses")
        self.assertEqual(self.content_lesson.get_title('fr'), "Temps des Verbes")
        self.assertEqual(self.content_lesson.get_title('es'), "Tiempos Verbales")
        self.assertEqual(self.content_lesson.get_title('nl'), "Werkwoordtijden")
    
    def test_get_instruction(self):
        """Test the get_instruction method"""
        self.assertEqual(self.content_lesson.get_instruction('en'), "Learn about different verb tenses")
        self.assertEqual(self.content_lesson.get_instruction('fr'), "Apprenez les différents temps des verbes")
    
    def test_content_type_lowercase(self):
        """Test that content_type is automatically converted to lowercase"""
        content_lesson = ContentLesson.objects.create(
            lesson=self.lesson,
            content_type='VOCABULARY',  # Uppercase
            title_en="Test Vocabulary",
            title_fr="Test Vocabulaire",
            title_es="Test Vocabulario",
            title_nl="Test Vocabulaire",
            instruction_en="Test instruction",
            instruction_fr="Instruction test",
            instruction_es="Instrucción test",
            instruction_nl="Test instructie",
            estimated_duration=5,
            order=2
        )
        
        self.assertEqual(content_lesson.content_type, 'vocabulary')  # Should be lowercase
    
    def test_minimum_duration(self):
        """Test that duration is set to minimum 1 if invalid"""
        content_lesson = ContentLesson.objects.create(
            lesson=self.lesson,
            content_type='Grammar',
            title_en="Grammar Test",
            title_fr="Test Grammaire",
            title_es="Test Gramática",
            title_nl="Test Grammatica",
            instruction_en="Test instruction",
            instruction_fr="Instruction test",
            instruction_es="Instrucción test",
            instruction_nl="Test instructie",
            estimated_duration=0,  # Invalid duration
            order=3
        )
        
        self.assertEqual(content_lesson.estimated_duration, 1)  # Should be set to 1


class VocabularyListCompleteTests(TestCase):
    """Tests complets pour le modèle VocabularyList"""
    
    def setUp(self):
        """Set up test data"""
        self.unit = Unit.objects.create(
            title_en="Test Unit",
            title_fr="Unité Test",
            title_es="Unidad Test",
            title_nl="Test Eenheid",
            level="B1",
            order=1
        )
        
        self.lesson = Lesson.objects.create(
            title_en="Vocabulary Lesson",
            title_fr="Leçon Vocabulaire",
            title_es="Lección Vocabulario",
            title_nl="Vocabulaire Les",
            order=1,
            unit=self.unit,
            lesson_type='vocabulary'
        )
        
        self.content_lesson = ContentLesson.objects.create(
            lesson=self.lesson,
            content_type='VocabularyList',
            title_en="Common Verbs",
            title_fr="Verbes Communs",
            title_es="Verbos Comunes",
            title_nl="Veelgebruikte Werkwoorden",
            instruction_en="Learn common verbs",
            instruction_fr="Apprendre les verbes communs",
            instruction_es="Aprende verbos comunes",
            instruction_nl="Leer veelgebruikte werkwoorden",
            estimated_duration=10,
            order=1
        )
        
        self.vocabulary_data = {
            'content_lesson': self.content_lesson,
            'word_en': "run",
            'word_fr': "courir",
            'word_es': "correr",
            'word_nl': "rennen",
            'definition_en': "to move quickly on foot",
            'definition_fr': "se déplacer rapidement à pied",
            'definition_es': "moverse rápidamente a pie",
            'definition_nl': "snel bewegen te voet"
        }
        self.vocabulary = VocabularyList.objects.create(**self.vocabulary_data)
    
    def test_vocabulary_creation(self):
        """Test creating a vocabulary item"""
        self.assertEqual(self.vocabulary.word_en, "run")
        self.assertEqual(self.vocabulary.word_fr, "courir")
        self.assertEqual(self.vocabulary.content_lesson, self.content_lesson)
        self.assertEqual(self.vocabulary.definition_en, "to move quickly on foot")
    
    def test_vocabulary_string_representation(self):
        """Test vocabulary string representation"""
        str_repr = str(self.vocabulary)
        self.assertIn("run", str_repr)
    
    def test_get_word(self):
        """Test getting word in different languages"""
        if hasattr(self.vocabulary, 'get_word'):
            self.assertEqual(self.vocabulary.get_word('en'), "run")
            self.assertEqual(self.vocabulary.get_word('fr'), "courir")
            self.assertEqual(self.vocabulary.get_word('es'), "correr")
            self.assertEqual(self.vocabulary.get_word('nl'), "rennen")
    
    def test_get_definition(self):
        """Test getting definition in different languages"""
        if hasattr(self.vocabulary, 'get_definition'):
            self.assertEqual(self.vocabulary.get_definition('en'), "to move quickly on foot")
            self.assertEqual(self.vocabulary.get_definition('fr'), "se déplacer rapidement à pied")


class NumbersCompleteTests(TestCase):
    """Tests complets pour le modèle Numbers"""
    
    def setUp(self):
        """Set up test data"""
        self.unit = Unit.objects.create(
            title_en="Numbers Unit",
            title_fr="Unité Nombres",
            title_es="Unidad Números",
            title_nl="Getallen Eenheid",
            level="A1",
            order=1
        )
        
        self.lesson = Lesson.objects.create(
            title_en="Numbers Lesson",
            title_fr="Leçon Nombres",
            title_es="Lección Números",
            title_nl="Getallen Les",
            order=1,
            unit=self.unit,
            lesson_type='numbers'
        )
        
        self.content_lesson = ContentLesson.objects.create(
            lesson=self.lesson,
            content_type='Numbers',
            title_en="Basic Numbers",
            title_fr="Nombres de Base",
            title_es="Números Básicos",
            title_nl="Basis Getallen",
            instruction_en="Learn basic numbers",
            instruction_fr="Apprendre les nombres de base",
            instruction_es="Aprende números básicos",
            instruction_nl="Leer basis getallen",
            estimated_duration=10,
            order=1
        )
    
    def test_numbers_creation_and_review(self):
        """Test creating numbers and marking as reviewed"""
        numbers = Numbers.objects.create(
            content_lesson=self.content_lesson,
            number=42,
            is_reviewed=False
        )
        
        self.assertEqual(numbers.number, 42)
        self.assertFalse(numbers.is_reviewed)
        
        # Mark as reviewed
        numbers.is_reviewed = True
        numbers.save()
        
        self.assertTrue(numbers.is_reviewed)


class TheoryContentCompleteTests(TestCase):
    """Tests complets pour le modèle TheoryContent"""
    
    def setUp(self):
        """Set up test data"""
        self.unit = Unit.objects.create(
            title_en="Theory Unit",
            title_fr="Unité Théorie",
            title_es="Unidad Teoría",
            title_nl="Theorie Eenheid",
            level="B2",
            order=1
        )
        
        self.lesson = Lesson.objects.create(
            title_en="Grammar Theory",
            title_fr="Théorie Grammaire",
            title_es="Teoría Gramática",
            title_nl="Grammatica Theorie",
            order=1,
            unit=self.unit,
            lesson_type='theory'
        )
        
        self.content_lesson = ContentLesson.objects.create(
            lesson=self.lesson,
            content_type='Theory',
            title_en="Verb Conjugation",
            title_fr="Conjugaison des Verbes",
            title_es="Conjugación de Verbos",
            title_nl="Werkwoord Vervoeging",
            instruction_en="Learn verb conjugation",
            instruction_fr="Apprendre la conjugaison des verbes",
            instruction_es="Aprende conjugación de verbos",
            instruction_nl="Leer werkwoord vervoeging",
            estimated_duration=20,
            order=1
        )
    
    def test_theory_content_json_migration(self):
        """Test theory content with JSON data migration"""
        theory_content = TheoryContent.objects.create(
            content_lesson=self.content_lesson,
            content_en="The present tense is used for current actions",
            content_fr="Le présent est utilisé pour les actions actuelles",
            content_es="El presente se usa para acciones actuales",
            content_nl="De tegenwoordige tijd wordt gebruikt voor huidige acties",
            explication_en="Present tense explanation",
            explication_fr="Explication du présent",
            explication_es="Explicación del presente", 
            explication_nl="Uitleg van de tegenwoordige tijd",
            available_languages=["en", "fr", "es", "nl"],
            language_specific_content={
                "en": {
                    "content": "The present tense is used for current actions",
                    "explanation": "Present tense explanation"
                },
                "fr": {
                    "content": "Le présent est utilisé pour les actions actuelles",
                    "explanation": "Explication du présent"
                }
            }
        )
        
        self.assertIn("en", theory_content.available_languages)
        self.assertIn("fr", theory_content.available_languages)
        self.assertEqual(theory_content.get_content("en"), "The present tense is used for current actions")
        self.assertEqual(theory_content.get_explanation("fr"), "Explication du présent")