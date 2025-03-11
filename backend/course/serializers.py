# course/serializers.py
from rest_framework import serializers, generics
from .models import Unit, Lesson, ContentLesson, VocabularyList, Grammar, MultipleChoiceQuestion, Numbers, TheoryContent, ExerciseGrammarReordering
import logging
logger = logging.getLogger(__name__)


class TargetLanguageMixin:
    """
    Mixin pour récupérer automatiquement la langue cible depuis les paramètres
    de requête, l'utilisateur ou les en-têtes HTTP.
    """
    def get_target_language(self):
        # Priorité 1: paramètre de requête
        target_language = self.request.query_params.get('target_language')
        
        # Ajoutez des logs pour déboguer
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"get_target_language - Lang from query params: {target_language}")
        
        # Priorité 2: header Accept-Language 
        if not target_language and 'Accept-Language' in self.request.headers:
            accept_lang = self.request.headers['Accept-Language'].split(',')[0].split('-')[0]
            if accept_lang in ['en', 'fr', 'es', 'nl']:
                target_language = accept_lang
                logger.info(f"get_target_language - Lang from Accept-Language: {target_language}")
                
        # Priorité 3: utilisateur authentifié
        if not target_language and hasattr(self.request, 'user') and self.request.user.is_authenticated:
            user_lang = getattr(self.request.user, 'target_language', None)
            if user_lang:
                target_language = user_lang.lower()
                logger.info(f"get_target_language - Lang from user profile: {target_language}")
        
        # Normaliser à minuscules
        if target_language and target_language.upper() in ['EN', 'FR', 'ES', 'NL']:
            target_language = target_language.lower()
        
        # Valeur par défaut
        if not target_language or target_language not in ['en', 'fr', 'es', 'nl']:
            target_language = 'en'
            
        logger.info(f"get_target_language - Final lang: {target_language}")
        return target_language
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        target_language = self.get_target_language()
        context['target_language'] = target_language
        
        # Log pour déboguer
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"get_serializer_context - Adding target_language to context: {target_language}")
        
        return context
class UnitSerializer(serializers.ModelSerializer):
    # Titre dynamique basé sur la langue cible
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = Unit
        fields = ['id', 'title', 'description', 'level', 'order']

    # Méthode pour récupérer le titre dans la langue de l'utilisateur
    def get_title(self, obj):
        target_language = self._get_target_language().lower()
        field_name = f'title_{target_language}'
        return getattr(obj, field_name, obj.title_en)
    
    def get_description(self, obj):
        target_language = self._get_target_language().lower()
        field_name = f"description_{target_language}"
        value = getattr(obj, field_name, obj.description_en)
        return value
    
    def _get_target_language(self):
        request = self.context.get('request')
        target_lang = None
        
        # Priorité 1: contexte direct (ajouté par la vue)
        if 'target_language' in self.context:
            target_lang = self.context.get('target_language')
            logger.info(f"Langue cible depuis le contexte direct: {target_lang}")
            return target_lang
            
        # Priorité 2: paramètre de requête
        if request and request.query_params.get('target_language'):
            target_lang = request.query_params.get('target_language')
            logger.info(f"Langue cible depuis les paramètres: {target_lang}")
            return target_lang
            
        # Priorité 3: utilisateur authentifié
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            target_lang = getattr(request.user, 'target_language', 'en').lower()
            logger.info(f"Langue cible depuis le profil utilisateur: {target_lang}")
            return target_lang
            
        # Valeur par défaut
        logger.info("Utilisation de la langue par défaut: en")
        return 'en'


class LessonSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'lesson_type', 'estimated_duration', 'order']

    def get_title(self, obj):
        # Récupérer la langue cible du contexte
        target_language = self.context.get('target_language', 'en')
        
        # S'assurer que la langue est en minuscules
        if target_language.upper() in ['EN', 'FR', 'ES', 'NL']:
            target_language = target_language.lower()
            
        # Construire le nom du champ dynamiquement
        field_name = f'title_{target_language}'
        
        # Log pour déboguer
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"LessonSerializer.get_title - Langue: {target_language}, Field: {field_name}")
        logger.info(f"LessonSerializer.get_title - Valeur: {getattr(obj, field_name, obj.title_en)}")
        
        # Retourner le titre dans la langue cible ou l'anglais par défaut
        return getattr(obj, field_name, obj.title_en)

    def get_description(self, obj):
        # Récupérer la langue cible du contexte
        target_language = self.context.get('target_language', 'en')
        
        # S'assurer que la langue est en minuscules
        if target_language.upper() in ['EN', 'FR', 'ES', 'NL']:
            target_language = target_language.lower()
            
        # Construire le nom du champ dynamiquement
        field_name = f'description_{target_language}'
        
        # Log pour déboguer
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"LessonSerializer.get_description - Langue: {target_language}, Field: {field_name}")
        logger.info(f"LessonSerializer.get_description - Valeur: {getattr(obj, field_name, obj.description_en)}")
        
        # Retourner la description dans la langue cible ou l'anglais par défaut
        return getattr(obj, field_name, obj.description_en)



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
        target_language = self._get_target_language().lower()
        field_name = f'title_{target_language}'
        value = getattr(obj, field_name, obj.title_en)
        logger.info(f"ContentLesson {obj.id}: {field_name} = {value}")
        return value

    def get_instruction(self, obj):
        target_language = self._get_target_language().lower()
        field_name = f'instruction_{target_language}'
        return getattr(obj, field_name, obj.instruction_en)
        
    def _get_target_language(self):
        request = self.context.get('request')
        
        # Priorité 1: contexte direct (ajouté par la vue)
        if 'target_language' in self.context:
            target_lang = self.context.get('target_language')
            logger.info(f"ContentLesson - Langue depuis le contexte: {target_lang}")
            return target_lang
            
        # Priorité 2: paramètre de requête
        if request and request.query_params.get('target_language'):
            target_lang = request.query_params.get('target_language')
            logger.info(f"ContentLesson - Langue depuis les paramètres: {target_lang}")
            return target_lang
            
        # Priorité 3: utilisateur authentifié
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            target_lang = getattr(request.user, 'target_language', 'en').lower()
            logger.info(f"ContentLesson - Langue depuis le profil: {target_lang}")
            return target_lang
            
        # Valeur par défaut
        logger.info("ContentLesson - Langue par défaut: en")
        return 'en'
    





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

class TheoryContentSerializer(serializers.ModelSerializer):
    content_lesson = ContentLessonSerializer(read_only=True)

    class Meta:
        model = TheoryContent
        fields = '__all__'

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
        # need to active this code when the feature of authenticated user is implemented
        # user = self.context.get('request').user
        # if user and user.is_authenticated:
        return obj.is_reviewed
        # return False
    
class ExerciseGrammarReorderingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExerciseGrammarReordering
        fields = ['id', 'content_lesson', 'sentence_en', 'sentence_fr', 'sentence_es', 'sentence_nl', 'explanation', 'hint']
    





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
