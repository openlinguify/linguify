# course/views.py
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status, filters, generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.exceptions import ValidationError
from rest_framework.authentication import TokenAuthentication

from django_filters.rest_framework import DjangoFilterBackend
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404


from .models import (
    Unit, 
    Lesson, 
    ContentLesson, 
    TheoryContent,
    VocabularyList, 
    MultipleChoiceQuestion, 
    Numbers,
    ExerciseGrammarReordering,
    FillBlankExercise
)
from .serializers import (
    TargetLanguageMixin,
    UnitSerializer, 
    LessonSerializer, 
    ContentLessonSerializer, 
    VocabularyListSerializer, 
    ContentLessonDetailSerializer, 
    MultipleChoiceQuestionSerializer, 
    NumbersSerializer, 
    TheoryContentSerializer,
    ExerciseGrammarReorderingSerializer,
    FillBlankExerciseSerializer
)
from .filters import LessonFilter, VocabularyListFilter
from authentication.models import User
import random
import django_filters

import logging

logger = logging.getLogger(__name__)

# par exemple, pour limiter le nombre de unités d'apprentissage retournées par page à 15
# et pour permettre à l'utilisateur de spécifier le nombre d'unités d'apprentissage à afficher par page
# en utilisant le paramètre de requête `page_size`
class CustomPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })

class UnitAPIView(TargetLanguageMixin, generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = UnitSerializer
    
    def get_queryset(self):
        queryset = Unit.objects.all().order_by('order')
        
        # Filtrer par niveau si spécifié
        level = self.request.query_params.get('level')
        if level:
            queryset = queryset.filter(level=level)
            
        return queryset

class LessonAPIView(TargetLanguageMixin, generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = LessonSerializer

    def get_queryset(self):
        unit_id = self.request.query_params.get('unit')
        # Log pour debugger
        target_language = self.get_target_language()
        logger.info(f"LessonAPIView - Fetching lessons with language: {target_language}")
        
        if unit_id:
            try:
                return Lesson.objects.filter(unit_id=unit_id).order_by('order')
            except ValueError:
                raise ValidationError({"error": "Invalid unit ID"})
        return Lesson.objects.all().order_by('order')
    
    # Méthode explicite pour s'assurer que le contexte contient la langue cible
    def get_serializer_context(self):
        context = super().get_serializer_context()
        target_language = self.get_target_language()
        context['target_language'] = target_language
        logger.info(f"LessonAPIView - Adding target_language to context: {target_language}")
        return context

class ContentLessonViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = ContentLessonSerializer

    def get_queryset(self):
        lesson_id = self.request.query_params.get('lesson')
        queryset = ContentLesson.objects.all().order_by('order')
        if lesson_id:
            try:
                return queryset.filter(lesson_id=lesson_id).order_by('order')
            except ValueError:
                raise ValidationError({"error": "Invalid lesson ID"})
        return queryset.order_by('order')
    
    def get_serializer_context(self):
        """Assure que la langue cible est dans le contexte"""
        context = super().get_serializer_context()
        
        # Log pour débugger
        logger.info(f"ContentLessonViewSet Headers: {self.request.headers}")
        logger.info(f"ContentLessonViewSet Query params: {self.request.query_params}")
        
        # Priorité 1: paramètre de requête
        target_language = self.request.query_params.get('target_language')
        
        # Priorité 2: header Accept-Language 
        if not target_language and 'Accept-Language' in self.request.headers:
            accept_lang = self.request.headers['Accept-Language'].split(',')[0].split('-')[0]
            if accept_lang in ['en', 'fr', 'es', 'nl']:
                target_language = accept_lang
                logger.info(f"ContentLessonViewSet - Langue depuis Accept-Language: {target_language}")
        
        # Priorité 3: utilisateur authentifié
        if not target_language and hasattr(self.request, 'user') and self.request.user.is_authenticated:
            target_language = getattr(self.request.user, 'target_language', 'en').lower()
            logger.info(f"ContentLessonViewSet - Langue depuis profil: {target_language}")
        
        # Valeur par défaut
        if not target_language:
            target_language = 'en'
            
        logger.info(f"ContentLessonViewSet - Langue finale: {target_language}")
        context['target_language'] = target_language
        return context
        
    def list(self, request, *args, **kwargs):
        logger.info(f"ContentLessonViewSet.list - Paramètres: {request.query_params}")
        
        queryset = self.get_queryset()
        logger.info(f"ContentLessonViewSet - Trouvé {queryset.count()} contenus")
        
        context = self.get_serializer_context()
        serializer = self.get_serializer(queryset, many=True, context=context)
        
        # Log d'exemple pour vérification
        if serializer.data:
            logger.info(f"ContentLessonViewSet - Exemple de réponse: {serializer.data[0]}")
            
        return Response(serializer.data)

class TheoryContentViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    authentication_classes = []
    queryset = TheoryContent.objects.select_related('content_lesson').all()
    serializer_class = TheoryContentSerializer

    def get_queryset(self):
        """
        Optionally filters the theories by content_lesson
        """
        queryset = super().get_queryset()
        content_lesson_id = self.request.query_params.get('content_lesson', None)
        
        if content_lesson_id is not None:
            queryset = queryset.filter(content_lesson_id=content_lesson_id)
        return queryset


    @action(detail=False, methods=['GET'], url_path='by-lesson/(?P<lesson_id>[^/.]+)')
    def by_lesson(self, request, lesson_id=None):
        """
        Retrieve theory content by lesson ID
        """
        try:
            # Vérifier d'abord si le ContentLesson existe et est de type 'theory'
            content_lesson = get_object_or_404(
                ContentLesson, 
                id=lesson_id,
                content_type='theory'
            )
            
            # Récupérer la théorie associée
            theory = get_object_or_404(
                TheoryContent,
                content_lesson=content_lesson
            )
            
            serializer = self.get_serializer(theory)
            return Response(serializer.data)
        
        except ContentLesson.DoesNotExist:
            return Response(
                {"error": "Theory lesson not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except TheoryContent.DoesNotExist:
            return Response(
                {"error": "Theory content not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )


    def create(self, request, *args, **kwargs):
        """
        Créer un nouveau contenu théorique
        Vérifie que le content_lesson est de type 'theory'
        """
        content_lesson_id = request.data.get('content_lesson')
        try:
            content_lesson = ContentLesson.objects.get(
                id=content_lesson_id,
                content_type='theory'
            )
        except ContentLesson.DoesNotExist:
            return Response(
                {"error": "Invalid content lesson or not a theory type"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().create(request, *args, **kwargs)


    def update(self, request, *args, **kwargs):
        """
        Mettre à jour un contenu théorique existant
        Vérifie que le content_lesson est de type 'theory' si modifié
        """
        content_lesson_id = request.data.get('content_lesson')
        if content_lesson_id:
            try:
                content_lesson = ContentLesson.objects.get(
                    id=content_lesson_id,
                    content_type='theory'
                )
            except ContentLesson.DoesNotExist:
                return Response(
                    {"error": "Invalid content lesson or not a theory type"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return super().update(request, *args, **kwargs)
    
class VocabularyListFilter(django_filters.FilterSet):
    content_lesson = django_filters.NumberFilter(field_name='content_lesson')

    class Meta:
        model = VocabularyList
        fields = ['content_lesson']

class VocabularyListAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = VocabularyListSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = VocabularyListFilter
    search_fields = ['word_en', 'word_fr', 'word_es', 'word_nl']
    ordering_fields = ['word_en', 'word_fr', 'word_es', 'word_nl']

    def get_queryset(self):
        return VocabularyList.objects.all()

    def filter_queryset(self, queryset):
        for backend in self.filter_backends:
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def get_serializer_context(self):
        context = {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }
        user = self.request.user
        context['target_language'] = self.request.query_params.get(
            'target_language', 
            getattr(user, 'target_language', 'en')
        )
        return context

    def get(self, request):
        queryset = self.get_queryset()
        filtered_queryset = self.filter_queryset(queryset)
        
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(filtered_queryset, request)
        
        serializer = self.serializer_class(
            page, 
            many=True, 
            context=self.get_serializer_context()
        )
        
        return paginator.get_paginated_response(serializer.data)
    
class NumbersViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = NumbersSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['content_lesson']

    def get_queryset(self):
        return Numbers.objects.all()
    
    def get(self, request):
        content_lesson = request.query_params.get('content_lesson')
        target_language = request.query_params.get('target_language', 'en')

        queryset = self.get_queryset()
        if content_lesson:
            queryset = queryset.filter(content_lesson=content_lesson)

        serializer = self.serializer_class(
            queryset,
            many=True,
            context={'target_language': target_language, 'request': request}
        )

        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle_review(self, request, pk=None):
        number = self.get_object()
        number.is_reviewed = not number.is_reviewed
        number.save()
        return Response({'message': 'Number reviewed'}, status=status.HTTP_200_OK)

class MultipleChoiceQuestionAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = MultipleChoiceQuestionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['content_lesson']

    def get_queryset(self):
        return MultipleChoiceQuestion.objects.all()

    def get(self, request, *args, **kwargs):
        content_lesson = request.query_params.get('content_lesson')
        target_language = request.query_params.get('target_language', 'en')


        queryset = self.get_queryset()
        if content_lesson:
            queryset = queryset.filter(content_lesson=content_lesson)

        serializer = self.serializer_class(
            queryset,
            many=True,
            context={'target_language': target_language, 'request': request}
        )

        return Response(serializer.data)

class ExerciseGrammarReorderingViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = ExerciseGrammarReorderingSerializer
    queryset = ExerciseGrammarReordering.objects.all()

    @action(detail=False, methods=['GET'], url_path='random', url_name='random')
    def random(self, request):
        content_lesson = request.query_params.get('content_lesson')
        queryset = self.get_queryset()
        
        if content_lesson:
            queryset = queryset.filter(content_lesson=content_lesson)
        
        exercise = queryset.order_by('?').first()

        if not exercise:
            return Response(
                {
                    "error": f"No exercise available for content lesson {content_lesson}"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(exercise)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        content_lesson = request.query_params.get('content_lesson')
        queryset = self.get_queryset()
        
        if content_lesson:
            queryset = queryset.filter(content_lesson=content_lesson)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class ExerciceVocabularyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        vocab_count = VocabularyList.objects.count()
        if vocab_count == 0:
            return Response({"error": "No vocabulary available."}, status=status.HTTP_404_NOT_FOUND)

        random_word = VocabularyList.objects.order_by('?').first()
        # Récupère 3 autres mots différents
        other_words = VocabularyList.objects.exclude(pk=random_word.pk).order_by('?')[:3]
        words = list(other_words) + [random_word]
        random.shuffle(words)
        data = {
            'word': random_word.word,
            'choices': [{'id': w.id, 'word': w.word} for w in words]
        }
        return Response(data, status=status.HTTP_200_OK)

class SearchVocabularyAPIView(APIView):
    def get(self, request):
        query = request.GET.get('query', '')
        vocabulary_list = VocabularyList.objects.filter(word__icontains=query) if query else VocabularyList.objects.all()
        data = VocabularyListSerializer(vocabulary_list, many=True).data
        return Response({'query': query, 'vocabularies': data}, status=status.HTTP_200_OK)

class FillBlankExerciseViewSet(viewsets.ModelViewSet):
    """
    API pour les exercices de type "fill in the blank"
    Permet de lister, créer, récupérer, mettre à jour et supprimer des exercices
    """
    queryset = FillBlankExercise.objects.all()
    serializer_class = FillBlankExerciseSerializer
    permission_classes = [AllowAny]  # À ajuster selon vos besoins de sécurité
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['content_lesson', 'difficulty', 'tags']
    search_fields = ['sentences', 'tags']
    ordering_fields = ['order', 'created_at', 'updated_at']
    
    def get_queryset(self):
        """Personnaliser le queryset avec des filtres supplémentaires"""
        queryset = super().get_queryset()
        
        # Filtrer par leçon
        content_lesson_id = self.request.query_params.get('content_lesson')
        if content_lesson_id:
            queryset = queryset.filter(content_lesson_id=content_lesson_id)
        
        # Filtrer par langue disponible
        language = self.request.query_params.get('language') or self.request.query_params.get('target_language')
        if language:
            # Filtrer les exercices qui ont du contenu dans cette langue
            queryset = queryset.filter(sentences__has_key=language, answer_options__has_key=language)
        
        return queryset
    
    @action(detail=False, methods=['GET'], url_path='by-lesson/(?P<lesson_id>[^/.]+)')
    def by_lesson(self, request, lesson_id=None):
        """Récupère tous les exercices d'une leçon donnée"""
        try:
            # Vérifier que la leçon existe
            content_lesson = ContentLesson.objects.get(pk=lesson_id)
            
            # Récupérer les exercices de cette leçon
            exercises = self.get_queryset().filter(content_lesson=content_lesson).order_by('order')
            
            # Sérialiser les résultats
            serializer = self.get_serializer(exercises, many=True)
            
            return Response(serializer.data)
        except ContentLesson.DoesNotExist:
            return Response(
                {"error": f"Content lesson with ID {lesson_id} does not exist"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['GET'], url_path='random')
    def random(self, request):
        """Récupère un exercice aléatoire en appliquant les filtres actuels"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Si aucun exercice ne correspond aux critères
        if not queryset.exists():
            return Response(
                {"error": "No exercises match the current filters"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Sélectionner un exercice aléatoirement
        random_exercise = queryset.order_by('?').first()
        serializer = self.get_serializer(random_exercise)
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['POST'], url_path='check-answer')
    def check_answer(self, request, pk=None):
        """
        Vérifie si une réponse est correcte
        
        Attend un corps de requête au format:
        {
            "answer": "is not",
            "language": "en"  // Optionnel, utilise la langue de la requête par défaut
        }
        """
        exercise = self.get_object()
        
        # Valider les données de la requête
        if 'answer' not in request.data:
            return Response(
                {"error": "Missing 'answer' field in request body"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_answer = request.data['answer']
        language = request.data.get('language') or self._get_target_language(request)
        
        # Vérifier la réponse
        is_correct = exercise.check_answer(user_answer, language)
        
        # Préparer la réponse
        response_data = {
            "is_correct": is_correct,
            "correct_answer": exercise.correct_answers.get(language, exercise.correct_answers.get('en', "")),
        }
        
        # Ajouter l'explication si disponible
        if exercise.explanations and language in exercise.explanations:
            response_data["explanation"] = exercise.explanations[language]
        elif exercise.explanations and 'en' in exercise.explanations:
            response_data["explanation"] = exercise.explanations['en']
        
        return Response(response_data)
    
    def _get_target_language(self, request):
        """Détermine la langue cible pour une requête"""
        # 1. Vérifier les paramètres de requête
        target_language = request.query_params.get('language') or request.query_params.get('target_language')
        if target_language:
            return target_language.lower()
        
        # 2. Vérifier l'en-tête Accept-Language
        if 'Accept-Language' in request.headers:
            accept_lang = request.headers['Accept-Language'].split(',')[0].split(';')[0].strip()
            if accept_lang and len(accept_lang) >= 2:
                return accept_lang[:2].lower()
        
        # 3. Vérifier le profil utilisateur
        if hasattr(request, 'user') and request.user.is_authenticated:
            user_language = getattr(request.user, 'target_language', None)
            if user_language:
                return user_language.lower()
        
        # 4. Valeur par défaut
        return 'en'