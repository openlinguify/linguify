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
)
from .serializers import (
    UnitSerializer, 
    LessonSerializer, 
    ContentLessonSerializer, 
    VocabularyListSerializer, 
    ContentLessonDetailSerializer, 
    MultipleChoiceQuestionSerializer, 
    NumbersSerializer, 
    TheoryContentSerializer,
    ExerciseGrammarReorderingSerializer,
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

class UnitAPIView(generics.ListAPIView):
    """
    Vue pour lister les unités d'apprentissage avec support multilingue.
    Permet de filtrer par niveau et de récupérer les titres/descriptions 
    dans la langue cible de l'utilisateur.
    """
    permission_classes = [AllowAny]
    serializer_class = UnitSerializer
    
    def get_queryset(self):
        """Filtre les unités par niveau si spécifié"""
        queryset = Unit.objects.all().order_by('order')
        
        # Filtrer par niveau
        level = self.request.query_params.get('level')
        if level:
            queryset = queryset.filter(level=level)
            
        return queryset
    
    def get_serializer_context(self):
        """Ajoute la langue cible au contexte du sérialiseur"""
        context = super().get_serializer_context()
        
        # Priorité 1: paramètre de requête
        target_language = self.request.query_params.get('target_language')
        
        # Priorité 2: utilisateur authentifié
        if not target_language and self.request.user.is_authenticated:
            target_language = getattr(self.request.user, 'target_language', 'en').lower()
        
        # Valeur par défaut si nécessaire
        if not target_language:
            target_language = 'en'
            
        logger.debug(f"Using target language: {target_language}")
        context['target_language'] = target_language
        return context

    def list(self, request, *args, **kwargs):
        """Liste les unités avec leur titre/description dans la langue cible"""
        # Récupère le queryset filtré
        queryset = self.get_queryset()
        
        # Récupère le contexte incluant la langue cible
        context = self.get_serializer_context()
        
        # Sérialise les unités
        serializer = self.get_serializer(queryset, many=True, context=context)
        
        # Renvoie la réponse
        return Response(serializer.data)
    
class LessonAPIView(generics.ListAPIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = LessonSerializer

    def get_queryset(self):
        unit_id = self.request.query_params.get('unit')
        if unit_id:
            try:
                return Lesson.objects.filter(unit_id=unit_id).order_by('order')
            except ValueError:
                raise ValidationError({"error": "Invalid unit ID"})
        return Lesson.objects.all().order_by('order')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        
        # Log pour vérifier les headers
        logger.info(f"Headers: {self.request.headers}")
        logger.info(f"Query params: {self.request.query_params}")
        
        # Priorité 1: paramètre de requête
        target_language = self.request.query_params.get('target_language')
        
        # Priorité 2: header Accept-Language 
        if not target_language and 'Accept-Language' in self.request.headers:
            accept_lang = self.request.headers['Accept-Language'].split(',')[0].split('-')[0]
            if accept_lang in ['en', 'fr', 'es', 'nl']:
                target_language = accept_lang
                logger.info(f"Langue cible depuis Accept-Language: {target_language}")
        
        # Priorité 3: utilisateur authentifié
        if not target_language and hasattr(self.request, 'user') and self.request.user.is_authenticated:
            target_language = getattr(self.request.user, 'target_language', 'en').lower()
            logger.info(f"Langue cible depuis le profil utilisateur: {target_language}")
        
        # Valeur par défaut
        if not target_language:
            target_language = 'en'
            
        logger.info(f"Langue cible finale: {target_language}")
        context['target_language'] = target_language
        return context

    def list(self, request, *args, **kwargs):
        logger.info(f"LessonAPIView.list - Paramètres: {request.query_params}")
        logger.info(f'Query params: {request.query_params}')
        
        if  'target_language' in request.query_params:
            logger.info(f"Langue cible: {request.query_params['target_language']}")
        else:
            logger.info("Pas de langue cible spécifiée")
        if hasattr(request, 'user') and request.user.is_authenticated:
            logger.info(f"Utilisateur authentifié: {request.user.username}")
        # Récupération des données
        queryset = self.get_queryset()
        logger.info(f"Trouvé {queryset.count()} leçons")
        
        context = self.get_serializer_context()
        serializer = self.get_serializer(queryset, many=True, context=context)
        
        # Log d'exemple pour vérification
        if serializer.data:
            logger.info(f"Exemple de réponse: {serializer.data[0]}")
            
        return Response(serializer.data)


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
