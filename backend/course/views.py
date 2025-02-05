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

from django_filters.rest_framework import DjangoFilterBackend
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404


from .models import Unit, Lesson, ContentLesson, VocabularyList, MultipleChoiceQuestion, Numbers
from .serializers import UnitSerializer, LessonSerializer, ContentLessonSerializer, VocabularyListSerializer, ContentLessonDetailSerializer, MultipleChoiceQuestionSerializer, NumbersSerializer
from .filters import LessonFilter, VocabularyListFilter
from authentication.models import User
import random
import django_filters

# par exemple, pour limiter le nombre de unités d'apprentissage retournées par page à 15
# et pour permettre à l'utilisateur de spécifier le nombre d'unités d'apprentissage à afficher par page
# en utilisant le paramètre de requête `page_size`
class CustomPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })

# class BaseTargetLanguageMixin:
#     """
#     Mixin pour récupérer automatiquement la langue cible depuis les paramètres
#     de requête ou le profil utilisateur et l'injecter dans le contexte du sérialiseur.
#     """
#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         request = self.request
#         user = request.user
#         target_language = request.query_params.get('target_language', getattr(user, 'target_language', 'en'))
#         context['target_language'] = target_language
#         return context

class UnitAPIView(generics.ListAPIView):
    permission_classes = [AllowAny]  # Explicitly set AllowAny
    authentication_classes = []  # Remove authentication requirement
    serializer_class = UnitSerializer
    queryset = Unit.objects.all().order_by('order')

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

# class TestRecapAttemptListView(generics.ListCreateAPIView):
#     queryset = TestRecapAttempt.objects.all()
#     serializer_class = TestRecapAttemptSerializer

#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         user = request.user
#         data = request.data
#         correct_answers = 0
#         for item in data:
#             vocabulary_list = VocabularyList.objects.get(pk=item['id'])
#             if vocabulary_list.word == item['word']:
#                 correct_answers += 1

#         score = correct_answers / len(data) * 100
#         user.score = score
#         user.save()

#         return Response({'score': score}, status=status.HTTP_200_OK)
    

# class QuizAPIView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request, quiz_id=None):
#         user = request.user
#         learning_language = user.learning_language
#         level = user.level_target_language
#
#         if not learning_language or not level:
#             return Response({"error": "Please specify the learning language and level in your profile."}, status=status.HTTP_400_BAD_REQUEST)
#
#         vocabulary_words = Vocabulary.objects.filter(language_id=learning_language, level_target_language=level)
#         if not vocabulary_words.exists():
#             return Response({"error": "No words found for the specified learning language and level."}, status=status.HTTP_404_NOT_FOUND)
#
#         word_pair = random.choice(vocabulary_words)
#         word = word_pair.word
#         correct_translation = word_pair.translation
#
#         incorrect_translations = Quiz.objects.filter(language_id=learning_language.language_code, level=level).exclude(pk=quiz_id).values_list('translation', flat=True)[:3]
#         options = list(incorrect_translations) + [correct_translation]
#         random.shuffle(options)
#
#         data = {
#             'language': learning_language.language_name,
#             'word': word,
#             'options': options,
#             'correct_translation': correct_translation
#         }
#         return Response(data, status=status.HTTP_200_OK)

class SearchVocabularyAPIView(APIView):
    def get(self, request):
        query = request.GET.get('query', '')
        vocabulary_list = VocabularyList.objects.filter(word__icontains=query) if query else VocabularyList.objects.all()
        data = VocabularyListSerializer(vocabulary_list, many=True).data
        return Response({'query': query, 'vocabularies': data}, status=status.HTTP_200_OK)
