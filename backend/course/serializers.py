# backend/django_apps/course/serializers.py
from rest_framework import serializers
from backend.course.models import (LearningPath, Unit, Lesson, Activity,
                                   Vocabulary, Grammar, Listening, Speaking,
                                   Reading, Writing, Test)

class LearningPathSerializer(serializers.ModelSerializer):
    units = serializers.SerializerMethodField()

    class Meta:
        model = LearningPath
        fields = '__all__'

    def get_units(self, obj):
        # Return a list of unit titles associated with the learning path
        return [unit.title for unit in obj.unit_set.all()]

class UnitSerializer(serializers.ModelSerializer):
    lessons = serializers.SerializerMethodField()

    class Meta:
        model = Unit
        fields = '__all__'

    def get_lessons(self, obj):
        # Return a list of lesson titles for the unit
        return [lesson.title for lesson in obj.lesson_set.all()]

class LessonSerializer(serializers.ModelSerializer):
    activities = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = '__all__'

    def get_activities(self, obj):
        # Return a list of activity titles for the lesson
        return [activity.title for activity in obj.activity_set.all()]



class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = '__all__'

class VocabularySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vocabulary
        fields = ['word', 'translation', 'example_sentence']

    def validate_word(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("Word must be at least 2 characters long.")
        return value

class GrammarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grammar
        fields = ['title', 'description', 'example']

class ListeningSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listening
        fields = ['title', 'audio']

class SpeakingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Speaking
        fields = ['title', 'audio']

class ReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reading
        fields = ['title', 'text']

class WritingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Writing
        fields = ['title', 'text']

class TestSerializer(serializers.ModelSerializer):
    incorrect_answers_list = serializers.SerializerMethodField()

    class Meta:
        model = Test
        fields = ['question', 'correct_answer', 'incorrect_answers', 'incorrect_answers_list']

    def get_incorrect_answers_list(self, obj):
        # Convert the comma-separated string into a list
        return obj.incorrect_answers.split(",")
