import pytest
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from linguify.views import index, home, vocabulaire, exercice_vocabulary, grammaire, revision, testlinguisitique, courses, prices, contact, about, search_vocabulary, add_vocabulary_to_flashcard, quiz, check_answer
from linguify.models import Vocabulary, Flashcards
from authentication.models import User

@pytest.fixture
def factory():
    return RequestFactory()

@pytest.fixture
def user():
    return User.objects.create(username='testuser', password='testpass123')

def view_index(factory):
    request = factory.get('/')
    response = index(request)
    assert response.status_code == 200

def view_home(factory, user):
    request = factory.get('/home')
    request.user = user
    response = home(request)
    assert response.status_code == 200

def view_vocabulaire(factory):
    request = factory.get('/vocabulaire')
    response = vocabulaire(request)
    assert response.status_code == 200

def view_exercice_vocabulary(factory):
    request = factory.get('/exercice_vocabulaire')
    response = exercice_vocabulary(request)
    assert response.status_code == 200

def view_grammaire(factory):
    request = factory.get('/grammaire')
    response = grammaire(request)
    assert response.status_code == 200

def view_revision(factory):
    request = factory.get('/revision')
    response = revision(request)
    assert response.status_code == 200

def view_testlinguisitique(factory):
    request = factory.get('/testlinguistique')
    response = testlinguisitique(request)
    assert response.status_code == 200

def courses_view(factory):
    request = factory.get('/courses')
    response = courses(request)
    assert response.status_code == 200
    assert 'course_names' in response.context
    assert 'course_description' in response.context

def view_prices(factory):
    request = factory.get('/prices')
    response = prices(request)
    assert response.status_code == 200

def view_contact(factory):
    request = factory.get('/contact')
    response = contact(request)
    assert response.status_code == 200

def about_view(factory):
    request = factory.get('/about')
    response = about(request)
    assert response.status_code == 200
    assert 'Linguify is a language school' in response.content.decode()

def search_vocabulary_view(factory):
    request = factory.get('/search_vocabulary', {'query': 'Test'})
    response = search_vocabulary(request)
    assert response.status_code == 200
    assert 'vocabularies' in response.context
    assert 'query' in response.context

def add_vocabulary_to_flashcard_view(factory, user):
    flashcard = Flashcards.objects.create(user=user, flashcard_title='Test Flashcard')
    vocabulary = Vocabulary.objects.create(word='Test', translation='Test')
    request = factory.get(f'/add_vocabulary_to_flashcard/{flashcard.flashcard_id}')
    request.user = user
    response = add_vocabulary_to_flashcard(request, flashcard.flashcard_id)
    assert response.status_code == 200
    assert vocabulary in flashcard.vocabulary.all()

def quiz_view(factory, user):
    request = factory.get('/quiz')
    request.user = user
    response = quiz(request)
    assert response.status_code == 200
    assert 'language' in response.context
    assert 'word' in response.context
    assert 'options' in response.context
    assert 'correct_translation' in response.context

def check_answer_view(factory):
    request = factory.post('/check_answer', data={'selected_translation': 'Test', 'correct_translation': 'Test'})
    response = check_answer(request)
    assert response.status_code == 200
    assert 'Correct!' in response.content.decode()

def view_revision_with_no_authenticated_user(factory):
    request = factory.get('/revision')
    request.user = AnonymousUser()
    response = revision(request)
    assert response.status_code == 302

def view_testlinguisitique_with_no_authenticated_user(factory):
    request = factory.get('/testlinguistique')
    request.user = AnonymousUser()
    response = testlinguisitique(request)
    assert response.status_code == 302

def view_courses_with_no_authenticated_user(factory):
    request = factory.get('/courses')
    request.user = AnonymousUser()
    response = courses(request)
    assert response.status_code == 302

def view_prices_with_no_authenticated_user(factory):
    request = factory.get('/prices')
    request.user = AnonymousUser()
    response = prices(request)
    assert response.status_code == 302

def view_contact_with_no_authenticated_user(factory):
    request = factory.get('/contact')
    request.user = AnonymousUser()
    response = contact(request)
    assert response.status_code == 302

def view_about_with_no_authenticated_user(factory):
    request = factory.get('/about')
    request.user = AnonymousUser()
    response = about(request)
    assert response.status_code == 302

def search_vocabulary_view_with_no_query(factory):
    request = factory.get('/search_vocabulary')
    response = search_vocabulary(request)
    assert response.status_code == 200
    assert 'vocabularies' in response.context
    assert 'query' not in response.context

def add_vocabulary_to_flashcard_view_with_nonexistent_flashcard(factory, user):
    request = factory.get('/add_vocabulary_to_flashcard/999')
    request.user = user
    response = add_vocabulary_to_flashcard(request, 999)
    assert response.status_code == 404

def quiz_view_with_no_authenticated_user(factory):
    request = factory.get('/quiz')
    request.user = AnonymousUser()
    response = quiz(request)
    assert response.status_code == 302

def check_answer_view_with_no_post_data(factory):
    request = factory.post('/check_answer')
    response = check_answer(request)
    assert response.status_code == 400