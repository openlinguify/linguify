# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.
"""
Tests for the exercises in the Course module.
This module particularly covers advanced exercises such as matching and speaking exercises.
"""
# Add imports to resolve import conflicts
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))

import pytest
import json
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils.timezone import now, timedelta
from django.db.utils import IntegrityError
from ..models import (
    Unit, Lesson, ContentLesson, MatchingExercise, SpeakingExercise, FillBlankExercise, 
    VocabularyList, Numbers, TheoryContent
)


@pytest.fixture
def test_unit():
    """Fixture providing a test unit for exercises."""
    return Unit.objects.create(
        title_en="Test Unit",
        title_fr="Unité de Test",
        title_es="Unidad de Prueba",
        title_nl="Test Eenheid",
        level="B1",
        order=1
    )


@pytest.fixture
def test_lesson(test_unit):
    """Fixture providing a test lesson for exercises."""
    return Lesson.objects.create(
        title_en="Test Lesson",
        title_fr="Leçon de Test",
        title_es="Lección de Prueba",
        title_nl="Test Les",
        order=1,
        unit=test_unit,
        lesson_type='vocabulary',
        created_at=now(),
        updated_at=now()
    )


@pytest.fixture
def test_content_lesson(test_lesson):
    """Fixture providing a test content lesson for exercises."""
    return ContentLesson.objects.create(
        lesson=test_lesson,
        content_type='Exercise',
        title_en="Test Content",
        title_fr="Contenu de Test",
        title_es="Contenido de Prueba",
        title_nl="Test Inhoud",
        estimated_duration=10,
        order=1
    )


@pytest.fixture
def vocabulary_items(test_content_lesson):
    """Fixture providing a list of vocabulary items for tests."""
    items = []
    # Create 10 vocabulary items
    for i in range(1, 11):
        item = VocabularyList.objects.create(
            content_lesson=test_content_lesson,
            word_en=f"Word{i}",
            word_fr=f"Mot{i}",
            word_es=f"Palabra{i}",
            word_nl=f"Woord{i}",
            definition_en=f"Definition of Word{i}",
            definition_fr=f"Définition de Mot{i}",
            definition_es=f"Definición de Palabra{i}",
            definition_nl=f"Definitie van Woord{i}",
            word_type_en="Noun" if i % 2 == 0 else "Verb",
            word_type_fr="Nom" if i % 2 == 0 else "Verbe",
            word_type_es="Sustantivo" if i % 2 == 0 else "Verbo",
            word_type_nl="Zelfstandig naamwoord" if i % 2 == 0 else "Werkwoord"
        )
        items.append(item)
    return items


@pytest.mark.django_db
class TestSpeakingExercise:
    """Tests for the SpeakingExercise model."""

    def test_speaking_exercise_creation(self, test_content_lesson, vocabulary_items):
        """Test the creation of a speaking exercise."""
        exercise = SpeakingExercise.objects.create(
            content_lesson=test_content_lesson
        )
        
        # Add vocabulary items
        for item in vocabulary_items[:5]:  # Add only 5 items
            exercise.vocabulary_items.add(item)
        
        # Check that the exercise was created with associated vocabulary
        assert exercise.id is not None
        assert exercise.vocabulary_items.count() == 5
        
        # Check methods
        assert str(exercise) == f"{test_content_lesson} - Speaking Exercise"
        
    def test_speaking_exercise_vocabulary_management(self, test_content_lesson, vocabulary_items):
        """Test vocabulary item management for a speaking exercise."""
        exercise = SpeakingExercise.objects.create(
            content_lesson=test_content_lesson
        )
        
        # Add all vocabulary items
        for item in vocabulary_items:
            exercise.vocabulary_items.add(item)
        
        assert exercise.vocabulary_items.count() == 10
        
        # Remove some items
        for item in vocabulary_items[:3]:
            exercise.vocabulary_items.remove(item)
        
        assert exercise.vocabulary_items.count() == 7
        
        # Check that the correct items were removed
        remaining_ids = [item.id for item in exercise.vocabulary_items.all()]
        for item in vocabulary_items[:3]:
            assert item.id not in remaining_ids
            
        # Clear all items
        exercise.vocabulary_items.clear()
        assert exercise.vocabulary_items.count() == 0


@pytest.mark.django_db
class TestFillBlankExercise:
    """Tests for the FillBlankExercise model."""

    def test_fill_blank_exercise_creation(self, test_content_lesson):
        """Test the creation of a fill-in-the-blank exercise."""
        exercise = FillBlankExercise.objects.create(
            content_lesson=test_content_lesson,
            instructions={
                "en": "Fill in the blank",
                "fr": "Remplissez le blanc",
                "es": "Rellena el espacio en blanco",
                "nl": "Vul de lege ruimte in"
            },
            sentences={
                "en": "The sky is ___.",
                "fr": "Le ciel est ___.",
                "es": "El cielo es ___.",
                "nl": "De lucht is ___."
            },
            answer_options={
                "en": ["blue", "red", "green", "yellow"],
                "fr": ["bleu", "rouge", "vert", "jaune"],
                "es": ["azul", "rojo", "verde", "amarillo"],
                "nl": ["blauw", "rood", "groen", "geel"]
            },
            correct_answers={
                "en": "blue",
                "fr": "bleu",
                "es": "azul",
                "nl": "blauw"
            },
            hints={
                "en": "The color of the sky during a clear day",
                "fr": "La couleur du ciel pendant une journée claire",
                "es": "El color del cielo durante un día despejado",
                "nl": "De kleur van de lucht tijdens een heldere dag"
            },
            difficulty="easy",
            tags=["colors", "nature", "basic"]
        )
        
        # Check that the exercise was created
        assert exercise.id is not None
        assert exercise.difficulty == "easy"
        assert len(exercise.tags) == 3
        assert "colors" in exercise.tags
        
        # Check methods
        available_languages = exercise.get_available_languages()
        assert len(available_languages) == 4
        assert "en" in available_languages
        assert "fr" in available_languages
        
        # Check content for different languages
        en_content = exercise.get_content_for_language("en")
        assert en_content["instruction"] == "Fill in the blank"
        assert en_content["sentence"] == "The sky is ___."
        assert "blue" in en_content["options"]
        
        fr_content = exercise.get_content_for_language("fr")
        assert fr_content["instruction"] == "Remplissez le blanc"
        assert fr_content["sentence"] == "Le ciel est ___."
        assert "bleu" in fr_content["options"]
        
        # Test answer checking
        assert exercise.check_answer("blue", "en") is True
        assert exercise.check_answer("bleu", "fr") is True
        assert exercise.check_answer("red", "en") is False
        assert exercise.check_answer("rouge", "fr") is False
        
        # Test whitespace handling
        assert exercise.check_answer(" blue ", "en") is True
        
        # Test sentence formatting
        assert exercise.format_sentence_with_blank("en") == "The sky is ___."
        assert exercise.format_sentence_with_answer("en") == "The sky is blue."
        
    def test_fill_blank_exercise_fallback(self, test_content_lesson):
        """Test fallback behavior for unavailable languages."""
        exercise = FillBlankExercise.objects.create(
            content_lesson=test_content_lesson,
            instructions={
                "en": "Fill in the blank",
                "fr": "Remplissez le blanc"
            },
            sentences={
                "en": "The sky is ___.",
                "fr": "Le ciel est ___."
            },
            answer_options={
                "en": ["blue", "red", "green", "yellow"],
                "fr": ["bleu", "rouge", "vert", "jaune"]
            },
            correct_answers={
                "en": "blue",
                "fr": "bleu"
            },
            hints={
                "en": "The color of the sky during a clear day",
                "fr": "La couleur du ciel pendant une journée claire"
            },
            difficulty="easy"
        )
        
        # Check fallback to English for Spanish
        es_content = exercise.get_content_for_language("es")
        assert es_content["instruction"] == "Fill in the blank"  # Fallback to English
        assert es_content["sentence"] == "The sky is ___."  # Fallback to English
        
        # Check answer checking for unavailable languages
        assert exercise.check_answer("blue", "es") is True  # Uses English answer


@pytest.mark.django_db
class TestMatchingExercise:
    """Tests for the MatchingExercise model."""

    def test_matching_exercise_creation(self, test_content_lesson, vocabulary_items):
        """Test the creation of a matching exercise."""
        exercise = MatchingExercise.objects.create(
            content_lesson=test_content_lesson,
            difficulty="medium",
            order=1,
            title_en="Match the words",
            title_fr="Associez les mots",
            title_es="Relaciona las palabras",
            title_nl="Koppel de woorden",
            pairs_count=5
        )
        
        # Add vocabulary items
        for item in vocabulary_items[:5]:
            exercise.vocabulary_words.add(item)
        
        # Check that the exercise was created with associated vocabulary
        assert exercise.id is not None
        assert exercise.vocabulary_words.count() == 5
        assert exercise.pairs_count == 5
        
        # Check string representation
        assert str(exercise) == f"Association - {test_content_lesson.title_en} (1)"
        
        # Check methods
        assert exercise.get_title("en") == "Match the words"
        assert exercise.get_title("fr") == "Associez les mots"
        assert "Match" in exercise.get_instruction("en")
        assert "Associez" in exercise.get_instruction("fr")
        
        # Test matching pair generation
        target_words, native_words, correct_pairs = exercise.get_matching_pairs("fr", "en")
        
        # Check that we have the correct number of words
        assert len(target_words) == 5
        assert len(native_words) == 5
        assert len(correct_pairs) == 5
        
        # Check that each target word matches a native word
        for target_word in target_words:
            assert target_word in correct_pairs
            native_word = correct_pairs[target_word]
            assert native_word in native_words
            
        # Test exercise data generation
        data = exercise.get_exercise_data("fr", "en")
        assert data["id"] == exercise.id
        assert data["title"] == exercise.get_title("fr")
        assert "target_words" in data
        assert "native_words" in data
        assert "correct_pairs" in data
        assert data["target_language"] == "fr"
        assert data["native_language"] == "en"


@pytest.mark.django_db
class TestTheoryContent:
    """Tests for the TheoryContent model."""
    
    def test_theory_content_json_migration(self, test_content_lesson):
        """Test migration of theory content to JSON format."""
        theory = TheoryContent.objects.create(
            content_lesson=test_content_lesson,
            content_en="This is the theory content in English.",
            content_fr="Ceci est le contenu théorique en français.",
            content_es="Este es el contenido teórico en español.",
            content_nl="Dit is de theoretische inhoud in het Nederlands.",
            explication_en="This is the explanation in English.",
            explication_fr="Ceci est l'explication en français.",
            formula_en="Formula in English",
            formula_fr="Formule en français",
            example_en="Example in English",
            example_fr="Exemple en français"
        )
        
        # Check initial state
        assert theory.using_json_format is False
        assert not theory.available_languages
        assert not theory.language_specific_content
        
        # Migrate to JSON format
        result = theory.migrate_to_json_format()
        
        # Check that migration succeeded
        assert result is True
        assert theory.using_json_format is True
        
        # Check available languages
        assert len(theory.available_languages) >= 2
        assert "en" in theory.available_languages
        assert "fr" in theory.available_languages
        
        # Check JSON content
        assert isinstance(theory.language_specific_content, dict)
        assert "en" in theory.language_specific_content
        assert "fr" in theory.language_specific_content
        
        # Check that content was correctly migrated
        en_content = theory.language_specific_content["en"]
        assert en_content["content"] == "This is the theory content in English."
        assert en_content["explanation"] == "This is the explanation in English."
        
        fr_content = theory.language_specific_content["fr"]
        assert fr_content["content"] == "Ceci est le contenu théorique en français."
        assert fr_content["explanation"] == "Ceci est l'explication en français."
        
        # Check that retrieval methods still work
        assert theory.get_content("en") == "This is the theory content in English."
        assert theory.get_content("fr") == "Ceci est le contenu théorique en français."
        assert theory.get_explanation("en") == "This is the explanation in English."


@pytest.mark.django_db
class TestNumbersExercise:
    """Tests for the Numbers model."""
    
    def test_numbers_creation_and_review(self, test_content_lesson):
        """Test creation and review of a numbers exercise."""
        number = Numbers.objects.create(
            content_lesson=test_content_lesson,
            number="42",
            number_en="forty-two",
            number_fr="quarante-deux",
            number_es="cuarenta y dos",
            number_nl="tweeënveertig",
            is_reviewed=False
        )
        
        # Check initial state
        assert number.number == "42"
        assert number.number_en == "forty-two"
        assert number.number_fr == "quarante-deux"
        assert number.is_reviewed is False
        
        # Change review state
        number.is_reviewed = True
        number.save()
        
        # Check the change
        number.refresh_from_db()
        assert number.is_reviewed is True
        
        # Check string representation
        expected_str = f"{test_content_lesson} - {test_content_lesson.title_en} - 42 - forty-two - True"
        assert str(number) == expected_str