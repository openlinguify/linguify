# course/serializers.py
from rest_framework import serializers, generics
from .models import Unit, Lesson, ContentLesson, VocabularyList, Grammar, MultipleChoiceQuestion, Numbers

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
                  'antonymous_nl']

    def get_word(self, obj):
        target_language = self.context.get('target_language', 'en')
        return obj.get_translation(target_language)

    def get_example_sentence(self, obj):
        target_language = self.context.get('target_language', 'en')
        return obj.get_example_sentence(target_language)

    def get_definition(self, obj):
        target_language = self.context.get('target_language', 'en')
        return obj.get_definition(target_language)

    def get_word_type(self, obj):
        target_language = self.context.get('target_language', 'en')
        return obj.get_word_type(target_language)

    def get_synonymous(self, obj):
        target_language = self.context.get('target_language', 'en')
        return obj.get_synonymous(target_language)

    def get_antonymous(self, obj):
        target_language = self.context.get('target_language', 'en')
        return obj.get_antonymous(target_language)


class ContentLessonDetailSerializer(ContentLessonSerializer):
    vocabulary_lists = VocabularyListSerializer(many=True, read_only=True)
    
    class Meta(ContentLessonSerializer.Meta):
        fields = ContentLessonSerializer.Meta.fields + ['vocabulary_lists']


class MultipleChoiceQuestionSerializer(serializers.ModelSerializer):
    question = serializers.SerializerMethodField()
    correct_answer = serializers.SerializerMethodField()
    fake_answers = serializers.SerializerMethodField()
    hint_answer = serializers.SerializerMethodField()

    class Meta:
        model = MultipleChoiceQuestion
        fields = [
            'id',
            'content_lesson',
            'question',
            'correct_answer',
            'fake_answers',
            'hint_answer',
            # Champs originaux pour référence
            'question_en',
            'question_fr',
            'question_es',
            'question_nl',
            'correct_answer_en',
            'correct_answer_fr',
            'correct_answer_es',
            'correct_answer_nl',
            'fake_answer1_en',
            'fake_answer2_en',
            'fake_answer3_en',
            'fake_answer4_en',
            'fake_answer1_fr',
            'fake_answer2_fr',
            'fake_answer3_fr',
            'fake_answer4_fr',
            'fake_answer1_es',
            'fake_answer2_es',
            'fake_answer3_es',
            'fake_answer4_es',
            'fake_answer1_nl',
            'fake_answer2_nl',
            'fake_answer3_nl',
            'fake_answer4_nl',
            'hint_answer_en',
            'hint_answer_fr',
            'hint_answer_es',
            'hint_answer_nl'
        ]

    def get_question(self, obj):
        target_language = self.context.get('target_language', 'en')
        return getattr(obj, f'question_{target_language}', obj.question_en)

    def get_correct_answer(self, obj):
        target_language = self.context.get('target_language', 'en')
        return getattr(obj, f'correct_answer_{target_language}', obj.correct_answer_en)

    def get_fake_answers(self, obj):
        target_language = self.context.get('target_language', 'en')
        fake_answers = []
        for i in range(1, 5):
            answer = getattr(obj, f'fake_answer{i}_{target_language}')
            if answer:
                fake_answers.append(answer)
        return fake_answers

    def get_hint_answer(self, obj):
        target_language = self.context.get('target_language', 'en')
        return getattr(obj, f'hint_answer_{target_language}', obj.hint_answer_en)

    def to_representation(self, instance):
        """Personnaliser la sortie finale du serializer"""
        data = super().to_representation(instance)
        
        # Ajouter toutes les réponses mélangées dans un seul tableau
        all_answers = [data['correct_answer']] + data['fake_answers']
        import random
        random.shuffle(all_answers)
        
        # Créer la représentation finale
        return {
            'id': data['id'],
            'content_lesson': data['content_lesson'],
            'question': data['question'],
            'answers': all_answers,  # Toutes les réponses mélangées
            'correct_answer': data['correct_answer'],  # Pour la vérification
            'hint': data['hint_answer']
        }


class NumbersSerializer(serializers.ModelSerializer):
    number = serializers.SerializerMethodField()

    class Meta:
        model = Numbers
        fields = ['id', 'content_lesson', 'number', 'number_en', 'number_fr', 'number_es', 'number_nl', 'is_reviewed']

    def get_number(self, obj):
        target_language = self.context.get('target_language', 'en')
        return getattr(obj, f'number_{target_language}', obj.number_en)
    
    def get_is_reviewed(self, obj):
        # user = self.context.get('request').user
        # if user and user.is_authenticated:
        return obj.is_reviewed
        # return False
    

    





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
