from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random
from apps.quizz.models import Quiz, Question, Answer, QuizSession, QuizResult

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample quiz data for testing analytics and leaderboard'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of test users to create (if they don\'t exist)',
        )
        parser.add_argument(
            '--quizzes',
            type=int,
            default=5,
            help='Number of test quizzes to create',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample quiz data...'))
        
        # Create test users if they don't exist
        users = []
        for i in range(options['users']):
            username = f'testuser{i+1}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'test{i+1}@example.com',
                    'first_name': f'Test{i+1}',
                    'last_name': 'User'
                }
            )
            users.append(user)
            if created:
                self.stdout.write(f'Created user: {username}')

        # Create test quizzes
        categories = ['Math', 'Science', 'History', 'Geography', 'Literature']
        difficulties = ['easy', 'medium', 'hard']
        
        for i in range(options['quizzes']):
            quiz = Quiz.objects.create(
                title=f'Test Quiz {i+1}',
                description=f'This is test quiz number {i+1}',
                category=random.choice(categories),
                difficulty=random.choice(difficulties),
                time_limit=random.randint(300, 1800),  # 5-30 minutes
                is_active=True
            )
            
            # Create questions for each quiz
            for j in range(random.randint(5, 15)):
                question = Question.objects.create(
                    quiz=quiz,
                    text=f'Question {j+1} for {quiz.title}?',
                    question_type='multiple_choice',
                    points=random.randint(1, 5),
                    order=j+1
                )
                
                # Create answers for each question
                correct_answer = random.randint(0, 3)
                for k in range(4):
                    Answer.objects.create(
                        question=question,
                        text=f'Answer {k+1}',
                        is_correct=(k == correct_answer),
                        order=k+1
                    )
            
            self.stdout.write(f'Created quiz: {quiz.title}')

        # Create quiz sessions and results
        quizzes = Quiz.objects.all()
        for user in users:
            # Create random number of quiz sessions for each user
            for _ in range(random.randint(3, 15)):
                quiz = random.choice(quizzes)
                
                # Random date within last 90 days
                days_ago = random.randint(0, 90)
                session_date = timezone.now() - timedelta(days=days_ago)
                
                session = QuizSession.objects.create(
                    user=user,
                    quiz=quiz,
                    started_at=session_date,
                    completed_at=session_date + timedelta(minutes=random.randint(5, 30)),
                    total_questions=quiz.questions.count(),
                    score=random.randint(0, quiz.questions.count()),
                    total_points=sum(q.points for q in quiz.questions.all())
                )
                
                self.stdout.write(f'Created session for {user.username} on {quiz.title}')

        self.stdout.write(self.style.SUCCESS('Sample quiz data created successfully!'))
        self.stdout.write(f'Created {len(users)} users, {quizzes.count()} quizzes, and {QuizSession.objects.count()} quiz sessions')