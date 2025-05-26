# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.
import pytest
from django.core.exceptions import ValidationError
from apps.course.models import (
    Unit, Lesson, ContentLesson, VocabularyList, TheoryContent, Numbers,
    MatchingExercise, FillBlankExercise, SpeakingExercise
)


@pytest.fixture
def sample_unit():
    """Fixture providing a sample Unit instance for tests."""
    return Unit.objects.create(
        title_en="English Grammar Basics",
        title_fr="Bases de Grammaire Anglaise",
        title_es="Fundamentos de Gramática Inglesa",
        title_nl="Engelse Grammatica Basis",
        level="B1",
        order=3
    )


@pytest.fixture
def sample_lesson(sample_unit):
    """Fixture providing a sample Lesson instance for tests."""
    return Lesson.objects.create(
        title_en="Introduction to Verbs",
        title_fr="Introduction aux Verbes",
        title_es="Introducción a los Verbos",
        title_nl="Introductie tot Werkwoorden",
        order=1,
        unit=sample_unit,
        lesson_type='grammar'
    )


@pytest.fixture
def sample_content_lesson(sample_lesson):
    """Fixture providing a sample ContentLesson instance for tests."""
    return ContentLesson.objects.create(
        lesson=sample_lesson,
        content_type='Theory',
        title_en="Verb Tenses",
        title_fr="Temps des Verbes",
        title_es="Tiempos Verbales",
        title_nl="Werkwoordtijden",
        instruction_en="Learn about different verb tenses",
        instruction_fr="Apprenez les différents temps des verbes",
        instruction_es="Aprende sobre los diferentes tiempos verbales",
        instruction_nl="Leer over verschillende werkwoordtijden",
        estimated_duration=15,
        order=1
    )

@pytest.mark.django_db
class TestUnitModel:
    """Tests for the Unit model."""

    def test_unit_string_representation(self, sample_unit):
        """Test the string representation of a Unit."""
        expected = (
            "Unit 03        [B1]  EN: English Grammar Basi... | FR: Bases de Grammaire A... | "
            "ES: Fundamentos de Gramá... | NL: Engelse Grammatica B..."
        )
        assert str(sample_unit) == expected

    def test_get_unit_title(self):
        """Test the get_unit_title method with different languages."""
        unit = Unit(
            title_en="English",
            title_fr="Anglais",
            title_es="Inglés",
            title_nl="Engels",
            level="A1",
            order=1
        )
        assert unit.get_unit_title('en') == "English"
        assert unit.get_unit_title('fr') == "Anglais"
        assert unit.get_unit_title('es') == "Inglés"
        assert unit.get_unit_title('nl') == "Engels"
        assert unit.get_unit_title('de') == "Language not supported"

    def test_generate_unit_description_no_lessons(self):
        """Test description generation for a Unit with no lessons."""
        unit = Unit(
            title_en="English",
            title_fr="Anglais",
            title_es="Inglés",
            title_nl="Engels",
            level="A2",
            order=2
        )
        # Test in various languages
        assert "coming soon" in unit.generate_unit_description('en')
        assert "bientôt disponible" in unit.generate_unit_description('fr')
        assert "próximamente" in unit.generate_unit_description('es')
        assert "komt binnenkort" in unit.generate_unit_description('nl')

    @pytest.mark.django_db
    def test_generate_unit_description_with_lessons(self, sample_unit):
        """Test description generation for a Unit with lessons."""
        # Create some lessons for the unit
        Lesson.objects.create(
            title_en="Introduction",
            title_fr="Introduction",
            title_es="Introducción",
            title_nl="Introductie",
            order=1,
            unit=sample_unit,
            lesson_type='vocabulary'
        )
        Lesson.objects.create(
            title_en="Basic Grammar",
            title_fr="Grammaire de base",
            title_es="Gramática básica",
            title_nl="Basisgrammatica",
            order=2,
            unit=sample_unit,
            lesson_type='grammar'
        )

        # Test description generation
        en_desc = sample_unit.generate_unit_description('en')
        assert "Introduction" in en_desc
        assert "Basic Grammar" in en_desc
        assert "2 lessons" in en_desc

    def test_update_unit_descriptions(self, sample_unit):
        """Test the update_unit_descriptions method."""
        # Create lessons and then update descriptions
        lesson = Lesson.objects.create(
            title_en="Test Lesson",
            title_fr="Leçon de test",
            title_es="Lección de prueba",
            title_nl="Testles",
            order=1,
            unit=sample_unit,
            lesson_type='vocabulary'
        )
        
        # Force une description différente pour tester le changement
        Unit.objects.filter(pk=sample_unit.pk).update(
            description_en="Description forcée avant le test",
            description_fr="Description forcée avant le test",
            description_es="Description forcée avant le test", 
            description_nl="Description forcée avant le test"
        )
        sample_unit.refresh_from_db()
        
        # Maintenant on peut tester la mise à jour
        original_desc = sample_unit.description_en
        sample_unit.update_unit_descriptions()
        sample_unit.refresh_from_db()
        
        assert sample_unit.description_en != original_desc
        assert "Test Lesson" in sample_unit.description_en


@pytest.mark.django_db
class TestLessonModel:
    """Tests for the Lesson model."""

    def test_lesson_string_representation(self, sample_unit):
        """Test the string representation of a Lesson."""
        lesson = Lesson.objects.create(
            title_en="Introduction to English",
            title_fr="Introduction à l'anglais",
            title_es="Introducción al inglés",
            title_nl="Inleiding tot het Engels",
            order=1,
            unit=sample_unit,
            lesson_type='vocabulary'
        )
        expected = f"{lesson.unit} - {lesson.unit.title_en} - {lesson.title_en} - {lesson.lesson_type}"
        assert str(lesson) == expected

    def test_get_title(self, sample_unit):
        """Test the get_title method with different languages."""
        lesson = Lesson(
            title_en="Intro",
            title_fr="Intro FR",
            title_es="Intro ES",
            title_nl="Intro NL",
            order=1,
            unit=sample_unit,
            lesson_type='grammar'
        )
        assert lesson.get_title('en') == "Intro"
        assert lesson.get_title('fr') == "Intro FR"
        assert lesson.get_title('es') == "Intro ES"
        assert lesson.get_title('nl') == "Intro NL"
        assert lesson.get_title('de') == "Intro"  # Fallback to English

    def test_get_description(self, sample_unit):
        """Test the get_description method with different languages."""
        lesson = Lesson(
            title_en="Intro",
            title_fr="Intro FR",
            title_es="Intro ES",
            title_nl="Intro NL",
            description_en="desc en",
            description_fr="desc fr",
            description_es="desc es",
            description_nl="desc nl",
            order=1,
            unit=sample_unit,
            lesson_type='grammar'
        )
        assert lesson.get_description('en') == "desc en"
        assert lesson.get_description('fr') == "desc fr"
        assert lesson.get_description('es') == "desc es"
        assert lesson.get_description('nl') == "desc nl"
        assert lesson.get_description('de') == "desc en"  # Fallback to English

    def test_clean_professional_field_required(self, sample_unit):
        """Test that professional_field is required when lesson_type is 'professional'."""
        lesson = Lesson(
            title_en="Professional Intro",
            title_fr="Intro professionnelle",
            title_es="Intro profesional",
            title_nl="Professionele intro",
            order=1,
            unit=sample_unit,
            lesson_type='professional'  # Professional type without field
        )
        with pytest.raises(ValidationError) as excinfo:
            lesson.clean()
        assert "professional_field" in str(excinfo.value)

    def test_clean_professional_field_valid(self, sample_unit):
        """Test that professional_field validation passes with correct data."""
        lesson = Lesson(
            title_en="Legal English",
            title_fr="Anglais juridique",
            title_es="Inglés jurídico",
            title_nl="Juridisch Engels",
            order=1,
            unit=sample_unit,
            lesson_type='professional',
            professional_field='law'  # Valid professional field
        )
        # Should not raise exception
        lesson.clean()
        assert lesson.professional_field == 'law'

    def test_clean_professional_field_cleared(self, sample_unit):
        """Test that professional_field is cleared when lesson_type is not 'professional'."""
        lesson = Lesson(
            title_en="Grammar Lesson",
            title_fr="Leçon de grammaire",
            title_es="Lección de gramática",
            title_nl="Grammaticales",
            order=1,
            unit=sample_unit,
            lesson_type='grammar',
            professional_field='law'  # Should be cleared
        )
        lesson.clean()
        assert lesson.professional_field is None

    def test_calculate_duration_lesson(self, sample_unit):
        """Test calculating the total duration of a lesson from its content lessons."""
        lesson = Lesson.objects.create(
            title_en="Duration Test",
            title_fr="Test de durée",
            title_es="Prueba de duración",
            title_nl="Duurtestles",
            order=1,
            unit=sample_unit,
            lesson_type='grammar'
        )
        
        # Create content lessons with different durations
        from apps.course.models import ContentLesson
        ContentLesson.objects.create(
            lesson=lesson,
            content_type='Grammar',
            title_en="Content 1",
            title_fr="Contenu 1",
            title_es="Contenido 1",
            title_nl="Inhoud 1",
            estimated_duration=15,
            order=1
        )
        ContentLesson.objects.create(
            lesson=lesson,
            content_type='Theory',
            title_en="Content 2",
            title_fr="Contenu 2",
            title_es="Contenido 2",
            title_nl="Inhoud 2",
            estimated_duration=10,
            order=2
        )
        
        # Test the calculation
        duration = lesson.calculate_duration_lesson()
        assert duration == 25  # 15 + 10
        
        # Save should update the estimated_duration field
        lesson.save()
        lesson.refresh_from_db()
        assert lesson.estimated_duration == 25



@pytest.mark.django_db
class TestContentLessonModel:
    """Tests for the ContentLesson model."""

    def test_content_lesson_creation(self, sample_content_lesson):
        """Test creating a ContentLesson instance."""
        assert ContentLesson.objects.filter(id=sample_content_lesson.id).exists()
        assert sample_content_lesson.title_en == "Verb Tenses"
        assert sample_content_lesson.content_type == 'theory'  # Should be lowercase after save

    def test_content_lesson_string_representation(self, sample_content_lesson):
        """Test the string representation of a ContentLesson."""
        expected = f"{sample_content_lesson.lesson.title_en} - {sample_content_lesson.title_en} - {sample_content_lesson.content_type} - {sample_content_lesson.order}"
        assert str(sample_content_lesson) == expected

    def test_get_title(self, sample_content_lesson):
        """Test the get_title method with different languages."""
        assert sample_content_lesson.get_title('en') == "Verb Tenses"
        assert sample_content_lesson.get_title('fr') == "Temps des Verbes"
        assert sample_content_lesson.get_title('es') == "Tiempos Verbales"
        assert sample_content_lesson.get_title('nl') == "Werkwoordtijden"
        assert sample_content_lesson.get_title('de') == "Verb Tenses"  # Fallback to English

    def test_get_instruction(self, sample_content_lesson):
        """Test the get_instruction method with different languages."""
        assert sample_content_lesson.get_instruction('en') == "Learn about different verb tenses"
        assert sample_content_lesson.get_instruction('fr') == "Apprenez les différents temps des verbes"
        assert sample_content_lesson.get_instruction('es') == "Aprende sobre los diferentes tiempos verbales"
        assert sample_content_lesson.get_instruction('nl') == "Leer over verschillende werkwoordtijden"
        assert sample_content_lesson.get_instruction('de') == "Learn about different verb tenses"  # Fallback to English

    def test_content_type_lowercase(self, sample_lesson):
        """Test that content_type is converted to lowercase when saving."""
        content_lesson = ContentLesson.objects.create(
            lesson=sample_lesson,
            content_type='THEORY',  # Uppercase
            title_en="Test Uppercase",
            title_fr="Test Majuscules",
            title_es="Test Mayúsculas",
            title_nl="Test Hoofdletters",
            estimated_duration=10,
            order=2
        )
        assert content_lesson.content_type == 'theory'  # Should be lowercase after save

    def test_minimum_duration(self, sample_lesson):
        """Test that estimated_duration is at least 1."""
        content_lesson = ContentLesson.objects.create(
            lesson=sample_lesson,
            content_type='Theory',
            title_en="Test Min Duration",
            title_fr="Test Durée Min",
            title_es="Test Duración Mín",
            title_nl="Test Min Duur",
            estimated_duration=0,  # Invalid duration
            order=3
        )
        assert content_lesson.estimated_duration == 1  # Should be adjusted to minimum value


@pytest.fixture
def sample_vocabulary(sample_content_lesson):
    """Fixture providing a sample VocabularyList instance for tests."""
    return VocabularyList.objects.create(
        content_lesson=sample_content_lesson,
        word_en="Run",
        word_fr="Courir",
        word_es="Correr",
        word_nl="Rennen",
        definition_en="Move at a speed faster than a walk",
        definition_fr="Se déplacer à une vitesse plus rapide que la marche",
        definition_es="Moverse a una velocidad más rápida que caminar",
        definition_nl="Bewegen met een snelheid sneller dan lopen",
        example_sentence_en="I run every morning.",
        example_sentence_fr="Je cours tous les matins.",
        example_sentence_es="Corro todas las mañanas.",
        example_sentence_nl="Ik ren elke ochtend.",
        word_type_en="Verb",
        word_type_fr="Verbe",
        word_type_es="Verbo",
        word_type_nl="Werkwoord",
        synonymous_en="Sprint, jog, dash",
        synonymous_fr="Sprinter, jogger, se précipiter",
        synonymous_es="Esprintar, trotar, precipitarse",
        synonymous_nl="Sprinten, joggen, rennen",
        antonymous_en="Walk, crawl, stand",
        antonymous_fr="Marcher, ramper, être debout",
        antonymous_es="Caminar, arrastrarse, estar de pie",
        antonymous_nl="Wandelen, kruipen, staan"
    )


@pytest.mark.django_db
class TestVocabularyListModel:
    """Tests for the VocabularyList model."""

    def test_vocabulary_creation(self, sample_vocabulary):
        """Test creating a VocabularyList instance."""
        assert VocabularyList.objects.filter(id=sample_vocabulary.id).exists()
        assert sample_vocabulary.word_en == "Run"
        assert sample_vocabulary.definition_fr == "Se déplacer à une vitesse plus rapide que la marche"

    def test_vocabulary_string_representation(self, sample_vocabulary):
        """Test the string representation of a VocabularyList."""
        expected = f"{sample_vocabulary.id} - {sample_vocabulary.content_lesson} - {sample_vocabulary.word_en} - {sample_vocabulary.definition_en}"
        assert str(sample_vocabulary) == expected

    def test_get_translation(self, sample_vocabulary):
        """Test the get_translation method with different languages."""
        assert sample_vocabulary.get_translation('en') == "Run"
        assert sample_vocabulary.get_translation('fr') == "Courir"
        assert sample_vocabulary.get_translation('es') == "Correr"
        assert sample_vocabulary.get_translation('nl') == "Rennen"
        assert sample_vocabulary.get_translation('de') == "Run"  # Fallback to English

    def test_get_example_sentence(self, sample_vocabulary):
        """Test the get_example_sentence method with different languages."""
        assert sample_vocabulary.get_example_sentence('en') == "I run every morning."
        assert sample_vocabulary.get_example_sentence('fr') == "Je cours tous les matins."
        assert sample_vocabulary.get_example_sentence('es') == "Corro todas las mañanas."
        assert sample_vocabulary.get_example_sentence('nl') == "Ik ren elke ochtend."
        assert sample_vocabulary.get_example_sentence('de') == "I run every morning."  # Fallback to English

    def test_get_definition(self, sample_vocabulary):
        """Test the get_definition method with different languages."""
        assert sample_vocabulary.get_definition('en') == "Move at a speed faster than a walk"
        assert sample_vocabulary.get_definition('fr') == "Se déplacer à une vitesse plus rapide que la marche"
        assert sample_vocabulary.get_definition('es') == "Moverse a una velocidad más rápida que caminar"
        assert sample_vocabulary.get_definition('nl') == "Bewegen met een snelheid sneller dan lopen"
        assert sample_vocabulary.get_definition('de') == "Move at a speed faster than a walk"  # Fallback to English

    def test_get_word_type(self, sample_vocabulary):
        """Test the get_word_type method with different languages."""
        assert sample_vocabulary.get_word_type('en') == "Verb"
        assert sample_vocabulary.get_word_type('fr') == "Verbe"
        assert sample_vocabulary.get_word_type('es') == "Verbo"
        assert sample_vocabulary.get_word_type('nl') == "Werkwoord"
        assert sample_vocabulary.get_word_type('de') == "Verb"  # Fallback to English

    def test_get_synonymous(self, sample_vocabulary):
        """Test the get_synonymous method with different languages."""
        assert sample_vocabulary.get_synonymous('en') == "Sprint, jog, dash"
        assert sample_vocabulary.get_synonymous('fr') == "Sprinter, jogger, se précipiter"
        assert sample_vocabulary.get_synonymous('es') == "Esprintar, trotar, precipitarse"
        assert sample_vocabulary.get_synonymous('nl') == "Sprinten, joggen, rennen"
        assert sample_vocabulary.get_synonymous('de') == "Sprint, jog, dash"  # Fallback to English

    def test_get_antonymous(self, sample_vocabulary):
        """Test the get_antonymous method with different languages."""
        assert sample_vocabulary.get_antonymous('en') == "Walk, crawl, stand"
        assert sample_vocabulary.get_antonymous('fr') == "Marcher, ramper, être debout"
        assert sample_vocabulary.get_antonymous('es') == "Caminar, arrastrarse, estar de pie"
        assert sample_vocabulary.get_antonymous('nl') == "Wandelen, kruipen, staan"
        assert sample_vocabulary.get_antonymous('de') == "Walk, crawl, stand"  # Fallback to English


@pytest.fixture
def sample_theory_content(sample_content_lesson):
    """Fixture providing a sample TheoryContent instance for tests."""
    return TheoryContent.objects.create(
        content_lesson=sample_content_lesson,
        content_en="English grammar has various tense forms.",
        content_fr="La grammaire anglaise a différentes formes de temps.",
        content_es="La gramática inglesa tiene varias formas de tiempo verbal.",
        content_nl="Engelse grammatica heeft verschillende tijdsvormen.",
        explication_en="Tenses show when an action takes place.",
        explication_fr="Les temps indiquent quand une action a lieu.",
        explication_es="Los tiempos verbales muestran cuándo ocurre una acción.",
        explication_nl="Tijden tonen wanneer een actie plaatsvindt.",
        formula_en="Subject + Verb + Object",
        formula_fr="Sujet + Verbe + Objet",
        formula_es="Sujeto + Verbo + Objeto",
        formula_nl="Onderwerp + Werkwoord + Object",
        example_en="I eat apples.",
        example_fr="Je mange des pommes.",
        example_es="Yo como manzanas.",
        example_nl="Ik eet appels.",
        exception_en="Irregular verbs don't follow the normal pattern.",
        exception_fr="Les verbes irréguliers ne suivent pas le schéma normal.",
        exception_es="Los verbos irregulares no siguen el patrón normal.",
        exception_nl="Onregelmatige werkwoorden volgen niet het normale patroon."
    )


@pytest.mark.django_db
class TestTheoryContentModel:
    """Tests for the TheoryContent model."""

    def test_theory_content_creation(self, sample_theory_content):
        """Test creating a TheoryContent instance."""
        assert TheoryContent.objects.filter(id=sample_theory_content.id).exists()
        assert sample_theory_content.content_en == "English grammar has various tense forms."
        assert sample_theory_content.using_json_format == False  # Default value

    def test_theory_content_string_representation(self, sample_theory_content):
        """Test the string representation of a TheoryContent."""
        expected = f"{sample_theory_content.content_lesson} - Grammar Content"
        assert str(sample_theory_content) == expected

    def test_get_content(self, sample_theory_content):
        """Test the get_content method with different languages."""
        assert sample_theory_content.get_content('en') == "English grammar has various tense forms."
        assert sample_theory_content.get_content('fr') == "La grammaire anglaise a différentes formes de temps."
        assert sample_theory_content.get_content('es') == "La gramática inglesa tiene varias formas de tiempo verbal."
        assert sample_theory_content.get_content('nl') == "Engelse grammatica heeft verschillende tijdsvormen."
        assert sample_theory_content.get_content('de') == "English grammar has various tense forms."  # Fallback to English

    def test_get_explanation(self, sample_theory_content):
        """Test the get_explanation method with different languages."""
        assert sample_theory_content.get_explanation('en') == "Tenses show when an action takes place."
        assert sample_theory_content.get_explanation('fr') == "Les temps indiquent quand une action a lieu."
        assert sample_theory_content.get_explanation('es') == "Los tiempos verbales muestran cuándo ocurre una acción."
        assert sample_theory_content.get_explanation('nl') == "Tijden tonen wanneer een actie plaatsvindt."
        assert sample_theory_content.get_explanation('de') == "Tenses show when an action takes place."  # Fallback to English

    def test_get_formula(self, sample_theory_content):
        """Test the get_formula method with different languages."""
        assert sample_theory_content.get_formula('en') == "Subject + Verb + Object"
        assert sample_theory_content.get_formula('fr') == "Sujet + Verbe + Objet"
        assert sample_theory_content.get_formula('es') == "Sujeto + Verbo + Objeto"
        assert sample_theory_content.get_formula('nl') == "Onderwerp + Werkwoord + Object"
        assert sample_theory_content.get_formula('de') == "Subject + Verb + Object"  # Fallback to English

    def test_migrate_to_json_format(self, sample_theory_content):
        """Test migrating content to JSON format."""
        # Initially not using JSON format
        assert sample_theory_content.using_json_format == False
        assert not sample_theory_content.available_languages
        assert not sample_theory_content.language_specific_content
        
        # Migrate to JSON format
        result = sample_theory_content.migrate_to_json_format()
        assert result == True
        
        # Verify migration was successful
        assert sample_theory_content.using_json_format == True
        assert len(sample_theory_content.available_languages) == 4
        assert 'en' in sample_theory_content.available_languages
        assert 'fr' in sample_theory_content.available_languages
        
        # Check content structure
        en_content = sample_theory_content.language_specific_content.get('en', {})
        assert en_content.get('content') == "English grammar has various tense forms."
        assert en_content.get('explanation') == "Tenses show when an action takes place."
        
        # Methods should still work after migration
        assert sample_theory_content.get_content('fr') == "La grammaire anglaise a différentes formes de temps."


@pytest.fixture
def sample_vocabulary_list(sample_content_lesson):
    """Fixture providing a list of VocabularyList instances for tests."""
    vocab_items = []
    words_en = ["Run", "Walk", "Jump", "Swim", "Fly"]
    words_fr = ["Courir", "Marcher", "Sauter", "Nager", "Voler"]
    words_es = ["Correr", "Caminar", "Saltar", "Nadar", "Volar"]
    words_nl = ["Rennen", "Wandelen", "Springen", "Zwemmen", "Vliegen"]
    
    for i in range(5):
        vocab = VocabularyList.objects.create(
            content_lesson=sample_content_lesson,
            word_en=words_en[i],
            word_fr=words_fr[i],
            word_es=words_es[i],
            word_nl=words_nl[i],
            definition_en=f"Definition of {words_en[i]}",
            definition_fr=f"Définition de {words_fr[i]}",
            definition_es=f"Definición de {words_es[i]}",
            definition_nl=f"Definitie van {words_nl[i]}",
            word_type_en="Verb",
            word_type_fr="Verbe",
            word_type_es="Verbo",
            word_type_nl="Werkwoord"
        )
        vocab_items.append(vocab)
    
    return vocab_items


@pytest.fixture
def sample_matching_exercise(sample_content_lesson, sample_vocabulary_list):
    """Fixture providing a sample MatchingExercise instance for tests."""
    exercise = MatchingExercise.objects.create(
        content_lesson=sample_content_lesson,
        difficulty='medium',
        order=1,
        title_en="Match these action words",
        title_fr="Associez ces mots d'action",
        title_es="Relaciona estas palabras de acción",
        title_nl="Koppel deze actiewoorden",
        pairs_count=5
    )
    
    # Add vocabulary words to the exercise
    for vocab in sample_vocabulary_list:
        exercise.vocabulary_words.add(vocab)
    
    return exercise


@pytest.mark.django_db
class TestMatchingExerciseModel:
    """Tests for the MatchingExercise model."""

    def test_matching_exercise_creation(self, sample_matching_exercise):
        """Test creating a MatchingExercise instance."""
        assert MatchingExercise.objects.filter(id=sample_matching_exercise.id).exists()
        assert sample_matching_exercise.title_en == "Match these action words"
        assert sample_matching_exercise.vocabulary_words.count() == 5

    def test_matching_exercise_string_representation(self, sample_matching_exercise):
        """Test the string representation of a MatchingExercise."""
        expected = f"Association - {sample_matching_exercise.content_lesson.title_en} ({sample_matching_exercise.order})"
        assert str(sample_matching_exercise) == expected

    def test_get_title(self, sample_matching_exercise):
        """Test the get_title method with different languages."""
        assert sample_matching_exercise.get_title('en') == "Match these action words"
        assert sample_matching_exercise.get_title('fr') == "Associez ces mots d'action"
        assert sample_matching_exercise.get_title('de') == "Match these action words"  # Fallback to English

    def test_get_instruction(self, sample_matching_exercise):
        """Test the get_instruction method with different languages."""
        assert "Match each word" in sample_matching_exercise.get_instruction('en')
        assert "Associez chaque mot" in sample_matching_exercise.get_instruction('fr')
        assert "Match each word" in sample_matching_exercise.get_instruction('de')  # Fallback to English

    def test_get_matching_pairs(self, sample_matching_exercise):
        """Test the get_matching_pairs method."""
        target_words, native_words, correct_pairs = sample_matching_exercise.get_matching_pairs('en', 'fr')
        
        # Check results
        assert len(target_words) == 5
        assert len(native_words) == 5
        assert len(correct_pairs) == 5
        
        # Check that all words are correctly mapped
        for target_word in target_words:
            assert target_word in correct_pairs
            native_word = correct_pairs[target_word]
            assert native_word in native_words

    def test_get_exercise_data(self, sample_matching_exercise):
        """Test the get_exercise_data method."""
        data = sample_matching_exercise.get_exercise_data('en', 'fr')
        
        # Check all required fields are present
        assert 'id' in data
        assert 'title' in data
        assert 'instruction' in data
        assert 'target_language' in data
        assert 'native_language' in data
        assert 'target_words' in data
        assert 'native_words' in data
        assert 'correct_pairs' in data
        
        # Check specific values
        assert data['id'] == sample_matching_exercise.id
        assert data['target_language'] == 'fr'
        assert data['native_language'] == 'en'
        assert data['target_language_name'] == 'French'
        assert data['native_language_name'] == 'English'


@pytest.fixture
def sample_fill_blank_exercise(sample_content_lesson):
    """Fixture providing a sample FillBlankExercise instance for tests."""
    return FillBlankExercise.objects.create(
        content_lesson=sample_content_lesson,
        order=1,
        instructions={
            "en": "Fill in the blank with the correct word",
            "fr": "Complétez avec le mot correct",
            "es": "Completa con la palabra correcta",
            "nl": "Vul in met het juiste woord"
        },
        sentences={
            "en": "Paris is the capital of ___.",
            "fr": "Paris est la capitale de la ___.",
            "es": "París es la capital de ___.",
            "nl": "Parijs is de hoofdstad van ___."
        },
        answer_options={
            "en": ["France", "Spain", "Italy", "Germany"],
            "fr": ["France", "Espagne", "Italie", "Allemagne"],
            "es": ["Francia", "España", "Italia", "Alemania"],
            "nl": ["Frankrijk", "Spanje", "Italië", "Duitsland"]
        },
        correct_answers={
            "en": "France",
            "fr": "France",
            "es": "Francia",
            "nl": "Frankrijk"
        },
        hints={
            "en": "It's a country in Western Europe",
            "fr": "C'est un pays d'Europe occidentale",
            "es": "Es un país de Europa occidental",
            "nl": "Het is een land in West-Europa"
        },
        difficulty="easy",
        tags=["geography", "capitals", "europe"]
    )


@pytest.mark.django_db
class TestFillBlankExerciseModel:
    """Tests for the FillBlankExercise model."""

    def test_fill_blank_exercise_creation(self, sample_fill_blank_exercise):
        """Test creating a FillBlankExercise instance."""
        assert FillBlankExercise.objects.filter(id=sample_fill_blank_exercise.id).exists()
        assert sample_fill_blank_exercise.difficulty == "easy"
        assert len(sample_fill_blank_exercise.tags) == 3
        assert "geography" in sample_fill_blank_exercise.tags

    def test_fill_blank_exercise_string_representation(self, sample_fill_blank_exercise):
        """Test the string representation of a FillBlankExercise."""
        expected = f"Fill in the Blank - Lesson {sample_fill_blank_exercise.content_lesson_id} - {sample_fill_blank_exercise.order}"
        assert str(sample_fill_blank_exercise) == expected

    def test_get_available_languages(self, sample_fill_blank_exercise):
        """Test the get_available_languages method."""
        languages = sample_fill_blank_exercise.get_available_languages()
        assert len(languages) == 4
        assert "en" in languages
        assert "fr" in languages
        assert "es" in languages
        assert "nl" in languages

    def test_get_content_for_language(self, sample_fill_blank_exercise):
        """Test the get_content_for_language method."""
        content = sample_fill_blank_exercise.get_content_for_language('fr')
        
        assert content["instruction"] == "Complétez avec le mot correct"
        assert content["sentence"] == "Paris est la capitale de la ___."
        assert content["options"] == ["France", "Espagne", "Italie", "Allemagne"]
        assert content["correct_answer"] == "France"
        assert content["hint"] == "C'est un pays d'Europe occidentale"
        
        # Test fallback to English
        content_unknown_lang = sample_fill_blank_exercise.get_content_for_language('de')
        assert content_unknown_lang["instruction"] == "Fill in the blank with the correct word"

    def test_check_answer(self, sample_fill_blank_exercise):
        """Test the check_answer method."""
        # Correct answer
        assert sample_fill_blank_exercise.check_answer("France", 'en') == True
        assert sample_fill_blank_exercise.check_answer("Francia", 'es') == True
        
        # Wrong answer
        assert sample_fill_blank_exercise.check_answer("Spain", 'en') == False
        assert sample_fill_blank_exercise.check_answer("Espagne", 'fr') == False
        
        # Extra whitespace should be handled
        assert sample_fill_blank_exercise.check_answer(" France ", 'en') == True

    def test_format_sentence_with_blank(self, sample_fill_blank_exercise):
        """Test the format_sentence_with_blank method."""
        sentence = sample_fill_blank_exercise.format_sentence_with_blank('en')
        assert sentence == "Paris is the capital of ___."
        
        sentence_fr = sample_fill_blank_exercise.format_sentence_with_blank('fr')
        assert sentence_fr == "Paris est la capitale de la ___."

    def test_format_sentence_with_answer(self, sample_fill_blank_exercise):
        """Test the format_sentence_with_answer method."""
        sentence = sample_fill_blank_exercise.format_sentence_with_answer('en')
        assert sentence == "Paris is the capital of France."
        
        sentence_nl = sample_fill_blank_exercise.format_sentence_with_answer('nl')
        assert sentence_nl == "Parijs is de hoofdstad van Frankrijk."


@pytest.fixture
def sample_speaking_exercise(sample_content_lesson, sample_vocabulary_list):
    """Fixture providing a sample SpeakingExercise instance for tests."""
    exercise = SpeakingExercise.objects.create(
        content_lesson=sample_content_lesson
    )
    
    # Add vocabulary words to the exercise
    for vocab in sample_vocabulary_list[:3]:  # Add just 3 words
        exercise.vocabulary_items.add(vocab)
    
    return exercise


@pytest.mark.django_db
class TestSpeakingExerciseModel:
    """Tests for the SpeakingExercise model."""

    def test_speaking_exercise_creation(self, sample_speaking_exercise):
        """Test creating a SpeakingExercise instance."""
        assert SpeakingExercise.objects.filter(id=sample_speaking_exercise.id).exists()
        assert sample_speaking_exercise.vocabulary_items.count() == 3

    def test_speaking_exercise_string_representation(self, sample_speaking_exercise):
        """Test the string representation of a SpeakingExercise."""
        expected = f"{sample_speaking_exercise.content_lesson} - Speaking Exercise"
        assert str(sample_speaking_exercise) == expected

    def test_vocabulary_association(self, sample_speaking_exercise, sample_vocabulary_list):
        """Test adding and removing vocabulary items from a speaking exercise."""
        # Initial count should be 3
        assert sample_speaking_exercise.vocabulary_items.count() == 3
        
        # Add two more vocabulary items
        sample_speaking_exercise.vocabulary_items.add(sample_vocabulary_list[3], sample_vocabulary_list[4])
        assert sample_speaking_exercise.vocabulary_items.count() == 5
        
        # Check that all vocabulary items are now associated
        for vocab in sample_vocabulary_list:
            assert vocab in sample_speaking_exercise.vocabulary_items.all()
        
        # Remove a vocabulary item
        sample_speaking_exercise.vocabulary_items.remove(sample_vocabulary_list[0])
        assert sample_speaking_exercise.vocabulary_items.count() == 4
        assert sample_vocabulary_list[0] not in sample_speaking_exercise.vocabulary_items.all()


@pytest.fixture
def sample_numbers(sample_content_lesson):
    """Fixture providing a sample Numbers instance for tests."""
    return Numbers.objects.create(
        content_lesson=sample_content_lesson,
        number="123",
        number_en="one hundred twenty-three",
        number_fr="cent vingt-trois",
        number_es="ciento veintitrés",
        number_nl="honderddrieëntwintig",
        is_reviewed=False
    )


@pytest.mark.django_db
class TestNumbersModel:
    """Tests for the Numbers model."""

    def test_numbers_creation(self, sample_numbers):
        """Test creating a Numbers instance."""
        assert Numbers.objects.filter(id=sample_numbers.id).exists()
        assert sample_numbers.number == "123"
        assert sample_numbers.number_fr == "cent vingt-trois"
        assert sample_numbers.is_reviewed == False

    def test_numbers_string_representation(self, sample_numbers):
        """Test the string representation of a Numbers instance."""
        expected = f"{sample_numbers.content_lesson} - {sample_numbers.content_lesson.title_en} - {sample_numbers.number} - {sample_numbers.number_en} - {sample_numbers.is_reviewed}"
        assert str(sample_numbers) == expected

    def test_toggle_review_status(self, sample_numbers):
        """Test toggling the review status."""
        initial_status = sample_numbers.is_reviewed
        sample_numbers.is_reviewed = not initial_status
        sample_numbers.save()
        
        # Refresh from database
        sample_numbers.refresh_from_db()
        assert sample_numbers.is_reviewed == (not initial_status)