from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Quiz, Question, Answer, QuizSession, QuizResult

User = get_user_model()


class QuizModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass123'
        )
        
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            description='A test quiz',
            creator=self.user,
            category='Test',
            difficulty='easy'
        )
    
    def test_quiz_creation(self):
        self.assertEqual(self.quiz.title, 'Test Quiz')
        self.assertEqual(self.quiz.creator, self.user)
        self.assertTrue(self.quiz.is_public)
    
    def test_question_creation(self):
        question = Question.objects.create(
            quiz=self.quiz,
            question_type='mcq',
            text='What is 2+2?',
            points=1
        )
        self.assertEqual(question.quiz, self.quiz)
        self.assertEqual(question.points, 1)
    
    def test_answer_creation(self):
        question = Question.objects.create(
            quiz=self.quiz,
            question_type='mcq',
            text='What is 2+2?'
        )
        answer = Answer.objects.create(
            question=question,
            text='4',
            is_correct=True
        )
        self.assertEqual(answer.question, question)
        self.assertTrue(answer.is_correct)


class QuizAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.quiz = Quiz.objects.create(
            title='API Test Quiz',
            creator=self.user,
            category='Test'
        )
        
        self.question = Question.objects.create(
            quiz=self.quiz,
            question_type='mcq',
            text='Test question?',
            points=1
        )
        
        self.correct_answer = Answer.objects.create(
            question=self.question,
            text='Correct',
            is_correct=True
        )
        
        self.wrong_answer = Answer.objects.create(
            question=self.question,
            text='Wrong',
            is_correct=False
        )
    
    def test_list_quizzes(self):
        response = self.client.get('/api/v1/quizz/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_create_quiz(self):
        data = {
            'title': 'New Quiz',
            'description': 'A new quiz',
            'category': 'New',
            'difficulty': 'medium'
        }
        response = self.client.post('/api/v1/quizz/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Quiz.objects.count(), 2)
    
    def test_start_session(self):
        response = self.client.post(f'/api/v1/quizz/{self.quiz.id}/start_session/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(QuizSession.objects.count(), 1)
    
    def test_submit_correct_answer(self):
        session = QuizSession.objects.create(
            user=self.user,
            quiz=self.quiz,
            total_points=1
        )
        
        data = {
            'session_id': session.id,
            'question_id': self.question.id,
            'answer_id': self.correct_answer.id
        }
        response = self.client.post(f'/api/v1/quizz/{self.quiz.id}/submit_answer/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['is_correct'])
        self.assertEqual(response.data['points_earned'], 1)