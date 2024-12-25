# course/serializers.py
from rest_framework import serializers, generics
from .models import Language, Level, LearningPath, Unit, Lesson, VocabularyList, Grammar

class LanguageSerializer(serializers.Serializer):
    class Meta:
        model = Language
        fields = ['id', 'name', 'code']

class LevelSerializer(serializers.Serializer):
    class Meta:
        model = Level
        fields = '__all__'

class LearningPathSerializer(serializers.ModelSerializer):
    units = serializers.SerializerMethodField()

    class Meta:
        model = LearningPath
        fields = '__all__'

    def get_units(self, obj):
        units = obj.unit_set.order_by('order')
        return UnitSerializer(units, many=True, context=self.context).data

    def validate(self, data):
        if not data.get('units'):
            raise serializers.ValidationError("At least one unit is required.")
        return data

class UnitSerializer(serializers.ModelSerializer):
    title_en = serializers.CharField(source='title_en')
    title_fr = serializers.CharField(source='title_fr')
    title_es = serializers.CharField(source='title_es')
    title_nl = serializers.CharField(source='title_nl')
    lessons = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Unit
        fields = ['id', 'learning_path', 'title_en', 'title_fr', 'title_es', 'title_nl', 'level', 'order', 'is_unlocked', 'progress']

    def get_title(self, obj):
        target_language = self.context.get('request').user.target_language
        return getattr(obj, f'title_{target_language}')

    def get_lessons(self, obj):
        lessons = obj.lesson_set.order_by('order')
        return LessonSerializer(lessons, many=True, context=self.context).data

    def get_progress(self, obj):
        completed_lessons = obj.lesson_set.filter(is_completed=True).count()
        total_lessons = obj.lesson_set.count()
        if total_lessons == 0:
            return 0
        return round((completed_lessons / total_lessons) * 100)

class LessonSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ['id', 'unit', 'lesson_type', 'title_en', 'title_fr', 'title_es', 'title_nl', 'description_en', 'description_fr', 'description_es', 'description_nl', 'estimated_duration', 'order', 'is_complete']

    def get_title(self, obj):
        target_language = self.context.get('request').user.target_language
        return getattr(obj, f'title_{target_language}')

    def get_description(self, obj):
        target_language = self.context.get('request').user.target_language
        return getattr(obj, f'description_{target_language}')

class VocabularyListSerializer(serializers.ModelSerializer):
    word = serializers.SerializerMethodField()
    example_sentence = serializers.SerializerMethodField()

    class Meta:
        model = VocabularyList
        fields = ['id', 'lesson', 'word_en', 'word_fr', 'word_es', 'word_nl', 'example_sentence_en', 'example_sentence_fr', 'example_sentence_es', 'example_sentence_nl']

    def get_word(self, obj):
        user = self.context['request'].user
        target_lang = user.target_language.lower()
        native_lang = user.native_language.lower()

        target_word = getattr(obj, f'word_{target_lang}', None)
        native_word = getattr(obj, f'word_{native_lang}', None)

        return {
            'target_language': target_word,
            'native_language': native_word,
        }

    def get_example_sentence(self, obj):
        user = self.context['request'].user
        target_lang = user.target_language.lower()
        native_lang = user.native_language.lower()

        target_sentence = getattr(obj, f'example_sentence_{target_lang}', None)
        native_sentence = getattr(obj, f'example_sentence_{native_lang}', None)

        return {
            'target_language': target_sentence,
            'native_language': native_sentence,
        }

class GrammarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grammar
        fields = ['title', 'description', 'example']

# class TestRecapSerializer(serializers.Serializer):
#     class Meta:
#         model = TestRecap
#         fields = ['lesson', 'score', 'total_questions', 'correct_answers', 'incorrect_answers']

# class ListeningSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Listening
#         fields = ['title', 'audio']

# class SpeakingSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Speaking
#         fields = ['title', 'audio']
#
# class ReadingSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Reading
#         fields = ['title', 'text']
#
# class WritingSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Writing
#         fields = ['title', 'text']
#
# class TestSerializer(serializers.ModelSerializer):
#     incorrect_answers_list = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Test
#         fields = ['question', 'correct_answer', 'incorrect_answers', 'incorrect_answers_list']
#
#     def get_incorrect_answers_list(self, obj):
#         # Convert the comma-separated string into a list
#         return obj.incorrect_answers.split(",")
