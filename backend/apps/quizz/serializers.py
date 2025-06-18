from rest_framework import serializers
from .models import Quiz, Question, Answer, QuizSession, QuizResult


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'text', 'is_correct', 'order']
        read_only_fields = ['id']


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'question_type', 'text', 'points', 'order', 'explanation', 'answers']
        read_only_fields = ['id']


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    question_count = serializers.IntegerField(source='questions.count', read_only=True)
    
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'creator', 'creator_name', 
                  'category', 'difficulty', 'is_public', 'time_limit', 
                  'created_at', 'updated_at', 'questions', 'question_count']
        read_only_fields = ['id', 'creator', 'created_at', 'updated_at']


class QuizSessionSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    percentage_score = serializers.SerializerMethodField()
    
    class Meta:
        model = QuizSession
        fields = ['id', 'quiz', 'quiz_title', 'started_at', 'completed_at', 
                  'score', 'total_points', 'percentage_score', 'time_spent']
        read_only_fields = ['id', 'started_at', 'score', 'total_points']
    
    def get_percentage_score(self, obj):
        if obj.total_points > 0:
            return round((obj.score / obj.total_points) * 100, 2)
        return 0


class QuizResultSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.text', read_only=True)
    
    class Meta:
        model = QuizResult
        fields = ['id', 'session', 'question', 'question_text', 
                  'selected_answer', 'text_answer', 'is_correct', 'points_earned']
        read_only_fields = ['id', 'is_correct', 'points_earned']