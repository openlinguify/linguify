# course/serializers.py
from rest_framework import serializers, generics
from .models import Unit, Lesson, ContentLesson, VocabularyList, Grammar

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
    title = serializers.CharField(source='title_en')  # Utilise le titre anglais par défaut
    description = serializers.CharField(source='description_en')  # Utilise la description anglaise par défaut

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'lesson_type', 'estimated_duration', 'order']

class ContentLessonSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    instruction = serializers.SerializerMethodField()

    class Meta:
        model = ContentLesson
        fields = [
            'id',
            'title',
            'instruction',
            'content_type',
            'estimated_duration',
            'order'
        ]

    def get_title(self, obj):
        return {
            'en': obj.title_en,
            'fr': obj.title_fr,
            'es': obj.title_es,
            'nl': obj.title_nl,
        }

    def get_instruction(self, obj):
        return {
            'en': obj.instruction_en,
            'fr': obj.instruction_fr,
            'es': obj.instruction_es,
            'nl': obj.instruction_nl,
        }

    def to_representation(self, instance):
        """Add title_en et instruction_en pour faciliter l'accès direct"""
        representation = super().to_representation(instance)
        representation['title_en'] = instance.title_en
        representation['instruction_en'] = instance.instruction_en
        return representation


class VocabularyListSerializer(serializers.ModelSerializer):
    word = serializers.SerializerMethodField()
    example_sentence = serializers.SerializerMethodField()
    definition = serializers.SerializerMethodField()
    word_type = serializers.SerializerMethodField()
    synonymous = serializers.SerializerMethodField()
    antonymous = serializers.SerializerMethodField()

    class Meta:
        model = VocabularyList
        fields = ['id', 
                  'content_lesson',
                  'word',
                  'definition',
                  'example_sentence',
                  'word_type',
                  'synonymous',
                  'antonymous',
                  'word_en', 
                  'word_fr', 
                  'word_es', 
                  'word_nl',
                  'definition_en',
                  'definition_fr',
                  'definition_es',
                  'definition_nl',
                  'example_sentence_en', 
                  'example_sentence_fr', 
                  'example_sentence_es', 
                  'example_sentence_nl',
                  'word_type_en',
                  'word_type_fr',
                  'word_type_es',
                  'word_type_nl',
                  'synonymous_en',
                  'synonymous_fr',
                  'synonymous_es',
                  'synonymous_nl',
                  'antonymous_en',
                  'antonymous_fr',
                  'antonymous_es',
                  'antonymous_nl',
                  ]

    def _get_user_languages(self, request):
        if not request or not hasattr(request, 'user'):
            return 'en', 'en'
        user = request.user
        target_lang = user.target_language.lower() if user.target_language else 'en'
        native_lang = user.native_language.lower() if user.native_language else 'en'
        return target_lang, native_lang

    def get_word(self, obj):
        target_lang, native_lang = self._get_user_languages(self.context.get('request'))
        return {
            'target_language': getattr(obj, f'word_{target_lang}', None) or obj.word_en,
            'native_language': getattr(obj, f'word_{native_lang}', None) or obj.word_en
        }

    def get_definition(self, obj):
        target_lang, native_lang = self._get_user_languages(self.context.get('request'))
        return {
            'target_language': getattr(obj, f'definition_{target_lang}', None) or obj.definition_en,
            'native_language': getattr(obj, f'definition_{native_lang}', None) or obj.definition_en
        }

    def get_example_sentence(self, obj):
        target_lang, native_lang = self._get_user_languages(self.context.get('request'))
        return {
            'target_language': getattr(obj, f'example_sentence_{target_lang}', None) or obj.example_sentence_en,
            'native_language': getattr(obj, f'example_sentence_{native_lang}', None) or obj.example_sentence_en
        }

    def get_word_type(self, obj):
        target_lang, native_lang = self._get_user_languages(self.context.get('request'))
        return {
            'target_language': getattr(obj, f'word_type_{target_lang}', None) or obj.word_type_en,
            'native_language': getattr(obj, f'word_type_{native_lang}', None) or obj.word_type_en
        }

    def get_synonymous(self, obj):
        target_lang, native_lang = self._get_user_languages(self.context.get('request'))
        return {
            'target_language': getattr(obj, f'synonymous_{target_lang}', None) or obj.synonymous_en,
            'native_language': getattr(obj, f'synonymous_{native_lang}', None) or obj.synonymous_en
        }

    def get_antonymous(self, obj):
        target_lang, native_lang = self._get_user_languages(self.context.get('request'))
        return {
            'target_language': getattr(obj, f'antonymous_{target_lang}', None) or obj.antonymous_en,
            'native_language': getattr(obj, f'antonymous_{native_lang}', None) or obj.antonymous_en
        }
class ContentLessonDetailSerializer(ContentLessonSerializer):
    vocabulary_lists = VocabularyListSerializer(many=True, read_only=True)
    
    class Meta(ContentLessonSerializer.Meta):
        fields = ContentLessonSerializer.Meta.fields + ['vocabulary_lists']


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
