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

    class Meta:
        model = VocabularyList
        fields = ['id', 
                  'lesson', 
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
