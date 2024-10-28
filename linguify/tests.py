import pytest
from django.http import HttpResponse
from django.test import TestCase
from django.template import loader, Context, Template, RequestContext
from django.core.files.uploadedfile import SimpleUploadedFile
from linguify.models import Courses_languages
from django.urls import reverse
from django.contrib.auth.models import User
from linguify.models import Vocabulary, Quiz
from django.test import RequestFactory, TestCase
from unittest.mock import patch
from linguify.views import quiz
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.models import User


# Test the models in the linguify app

class Courses_languagesTestCase(TestCase):
    def setUp(self):
        Courses_languages.objects.create(course_languages_title="French", course_description="Learn French")

    def test_course_languages_title(self):
        french = Courses_languages.objects.get(course_languages_title="French")
        self.assertEqual(french.course_languages_title, 'French')

    def test_course_description(self):
        french = Courses_languages.objects.get(course_languages_title="French")
        self.assertEqual(french.course_description, 'Learn French')


class QuizViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.user.learning_language = 'fr'
        self.user.level_target_language = 'A1'
        self.user.save()

        # Create some vocabulary entries
        Vocabulary.objects.create(language_id='fr', level_target_language='A1', word='chien', translation='dog')
        Vocabulary.objects.create(language_id='fr', level_target_language='A1', word='chat', translation='cat')
        Vocabulary.objects.create(language_id='fr', level_target_language='A1', word='oiseau', translation='bird')

        # Create some quiz entries
        Quiz.objects.create(user=self.user, correct_translation='fish')
        Quiz.objects.create(user=self.user, correct_translation='horse')
        Quiz.objects.create(user=self.user, correct_translation='cow')

    def test_quiz_view_user_not_logged_in(self):
        request = self.factory.get('/quiz')
        request.user = User(is_authenticated=False)
        response = quiz(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please log in to access this feature.")

    def test_quiz_view_no_learning_language_or_level(self):
        request = self.factory.get('/quiz')
        request.user = self.user
        request.user.learning_language = None
        response = quiz(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please specify the learning language and level in your profile.")

    def test_quiz_view_no_vocabulary_words(self):
        # Remove existing vocabulary
        Vocabulary.objects.all().delete()

        request = self.factory.get('/quiz')
        request.user = self.user
        response = quiz(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No words found for the specified learning language and level.")

    @patch('random.choice')
    def test_quiz_view_valid(self, mock_random_choice):
        mock_random_choice.return_value = Vocabulary.objects.first()

        request = self.factory.get('/quiz')
        request.user = self.user
        response = quiz(request)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz.html')
        self.assertIn('word', response.context_data)
        self.assertIn('options', response.context_data)
        self.assertIn('correct_translation', response.context_data)
        self.assertEqual(response.context_data['language'], self.user.learning_language)
