# course/serializers.py
from rest_framework import serializers, generics
from .models import Unit, Lesson, VocabularyList, Grammar

class UnitSerializer(serializers.ModelSerializer):
    # Titre dynamique basé sur la langue cible
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = Unit
        fields = ['id', 'title', 'description', 'level', 'order']

    # Méthode pour récupérer le titre dans la langue de l'utilisateur
    def get_title(self, obj):
        target_language = self._get_target_language()
        return getattr(obj, f"title_{target_language}", obj.title_en)  # Fallback à l'anglais

    # Méthode pour récupérer la description dans la langue de l'utilisateur
    def get_description(self, obj):
        target_language = self._get_target_language()
        return getattr(obj, f"description_{target_language}", obj.description_en)  # Fallback à l'anglais

    # Méthode utilitaire pour récupérer la langue cible
    def _get_target_language(self):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return getattr(request.user, 'target_language', 'en')  # Langue par défaut : anglais
        return 'en'



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
