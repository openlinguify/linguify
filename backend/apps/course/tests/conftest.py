"""
Fichier de configuration pytest pour les tests du module Course.
Ce fichier définit les fixtures partagées par les différents tests.
"""
import pytest
from django.utils import timezone
# Import the models with absolute import to avoid conflicts
from apps.course.models import Unit, Lesson, ContentLesson, VocabularyList


@pytest.fixture
def create_unit():
    """
    Fixture pour créer une unité de test.
    
    Retourne une fonction factory qui peut être utilisée pour créer des unités
    avec des attributs personnalisés.
    """
    def _create_unit(**kwargs):
        unit_data = {
            'title_en': 'Test Unit',
            'title_fr': 'Unité de Test',
            'title_es': 'Unidad de Prueba',
            'title_nl': 'Test Eenheid',
            'level': 'B1',
            'order': 1,
        }
        unit_data.update(kwargs)
        return Unit.objects.create(**unit_data)
    
    return _create_unit


@pytest.fixture
def create_lesson():
    """
    Fixture pour créer une leçon de test.
    
    Retourne une fonction factory qui peut être utilisée pour créer des leçons
    avec des attributs personnalisés.
    """
    def _create_lesson(unit=None, **kwargs):
        # Créer une unité si non fournie
        if unit is None:
            unit = Unit.objects.create(
                title_en='Default Unit',
                title_fr='Unité par défaut',
                title_es='Unidad predeterminada',
                title_nl='Standaard eenheid',
                level='A2',
                order=1
            )
        
        lesson_data = {
            'title_en': 'Test Lesson',
            'title_fr': 'Leçon de Test',
            'title_es': 'Lección de Prueba',
            'title_nl': 'Test Les',
            'order': 1,
            'unit': unit,
            'lesson_type': 'vocabulary',
            'created_at': timezone.now(),
            'updated_at': timezone.now()
        }
        lesson_data.update(kwargs)
        return Lesson.objects.create(**lesson_data)
    
    return _create_lesson


@pytest.fixture
def create_content_lesson():
    """
    Fixture pour créer un contenu de leçon de test.
    
    Retourne une fonction factory qui peut être utilisée pour créer des contenus de leçon
    avec des attributs personnalisés.
    """
    def _create_content_lesson(lesson=None, **kwargs):
        # Créer une leçon si non fournie
        if lesson is None:
            unit = Unit.objects.create(
                title_en='Default Unit',
                title_fr='Unité par défaut',
                title_es='Unidad predeterminada',
                title_nl='Standaard eenheid',
                level='A2',
                order=1
            )
            lesson = Lesson.objects.create(
                title_en='Default Lesson',
                title_fr='Leçon par défaut',
                title_es='Lección predeterminada',
                title_nl='Standaardles',
                order=1,
                unit=unit,
                lesson_type='vocabulary'
            )
        
        content_data = {
            'lesson': lesson,
            'content_type': 'Theory',
            'title_en': 'Test Content',
            'title_fr': 'Contenu de Test',
            'title_es': 'Contenido de Prueba',
            'title_nl': 'Test Inhoud',
            'estimated_duration': 10,
            'order': 1
        }
        content_data.update(kwargs)
        return ContentLesson.objects.create(**content_data)
    
    return _create_content_lesson


@pytest.fixture
def create_vocabulary():
    """
    Fixture pour créer un élément de vocabulaire de test.
    
    Retourne une fonction factory qui peut être utilisée pour créer des éléments de vocabulaire
    avec des attributs personnalisés.
    """
    def _create_vocabulary(content_lesson=None, **kwargs):
        # Créer un contenu de leçon si non fourni
        if content_lesson is None:
            unit = Unit.objects.create(
                title_en='Default Unit',
                title_fr='Unité par défaut',
                title_es='Unidad predeterminada',
                title_nl='Standaard eenheid',
                level='A2',
                order=1
            )
            lesson = Lesson.objects.create(
                title_en='Default Lesson',
                title_fr='Leçon par défaut',
                title_es='Lección predeterminada',
                title_nl='Standaardles',
                order=1,
                unit=unit,
                lesson_type='vocabulary'
            )
            content_lesson = ContentLesson.objects.create(
                lesson=lesson,
                content_type='Vocabulary',
                title_en='Default Content',
                title_fr='Contenu par défaut',
                title_es='Contenido predeterminado',
                title_nl='Standaardinhoud',
                estimated_duration=10,
                order=1
            )
        
        vocab_data = {
            'content_lesson': content_lesson,
            'word_en': 'Test Word',
            'word_fr': 'Mot de Test',
            'word_es': 'Palabra de Prueba',
            'word_nl': 'Test Woord',
            'definition_en': 'Definition of Test Word',
            'definition_fr': 'Définition du Mot de Test',
            'definition_es': 'Definición de la Palabra de Prueba',
            'definition_nl': 'Definitie van Test Woord',
            'word_type_en': 'Noun',
            'word_type_fr': 'Nom',
            'word_type_es': 'Sustantivo',
            'word_type_nl': 'Zelfstandig naamwoord'
        }
        vocab_data.update(kwargs)
        return VocabularyList.objects.create(**vocab_data)
    
    return _create_vocabulary