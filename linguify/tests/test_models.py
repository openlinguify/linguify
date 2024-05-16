import pytest
from django.core.exceptions import ValidationError
from authentication.models import Language, LevelTarget, User
from linguify.models import Flashcard, Vocabulary, Theme

@pytest.fixture
def user():
    return User.objects.create(username='testuser', password='testpass123')

@pytest.fixture
def language():
    return Language.objects.create(name='English')

@pytest.fixture
def level_target():
    return LevelTarget.objects.create(name='Intermediate')

@pytest.fixture
def vocabulary(user, language, level_target):
    return Vocabulary.objects.create(
        vocabulary_id=1,
        language_id=language,
        level_target_language=level_target,
        vocabulary_title='Test Vocabulary',
        word='Test',
        translation='Test',
        example_sentence='This is a test.'
    )

@pytest.fixture
def theme():
    return Theme.objects.create(theme_name='Test Theme', theme_description='This is a test theme.')

@pytest.fixture
def flashcard(user, language, level_target, vocabulary, theme):
    return Flashcard.objects.create(
        user=user,
        language=language,
        level=level_target,
        vocabulary=vocabulary,
        theme=theme,
        flashcard_title='Test Flashcard',
        word='Test',
        translation='Test',
        example_sentence='This is a test.'
    )

def flashcard_creation(flashcard):
    assert flashcard is not None

def flashcard_str_representation(flashcard):
    assert str(flashcard) == f"{flashcard.flashcard_id} - {flashcard.user} - {flashcard.language} - {flashcard.flashcard_title} - {flashcard.word} - {flashcard.translation} - {flashcard.level}"

def flashcard_get_flashcard(flashcard):
    assert flashcard.get_flashcard == f"{flashcard.word} - {flashcard.translation}"

def add_vocabulary_to_flashcard(flashcard, vocabulary):
    flashcard.add_vocabulary_to_flashcard(vocabulary.vocabulary_id)
    assert flashcard.vocabulary == vocabulary

def remove_vocabulary_from_flashcard(flashcard, vocabulary):
    flashcard.add_vocabulary_to_flashcard(vocabulary.vocabulary_id)
    flashcard.remove_vocabulary_from_flashcard(vocabulary.vocabulary_id)
    assert flashcard.vocabulary is None

def modify_flashcard(flashcard):
    flashcard.modify_flashcard(flashcard.flashcard_id)
    assert flashcard.word == 'new word'
    assert flashcard.translation == 'new translation'