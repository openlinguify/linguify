# course/views.py
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status, filters, generics
from rest_framework.pagination import PageNumberPagination

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Unit, Lesson, VocabularyList
from .serializers import UnitSerializer, LessonSerializer, VocabularyListSerializer
from .filters import LessonFilter, VocabularyListFilter
from authentication.models import User
import random


class CustomPagination(PageNumberPagination):
    page_size = 10
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

class UnitAPIView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = UnitSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = Unit.objects.all().order_by('order')  # Trier par ordre croissant
        request = self.request

        # Filtrer selon la langue cible de l'utilisateur s'il est authentifié
        if request.user.is_authenticated:
            target_language = getattr(request.user, 'target_language', None)
            if target_language:
                # Ajoutez des filtres spécifiques si besoin
                queryset = queryset.filter(description_en__isnull=False)

        return queryset

class LessonAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = LessonFilter
    search_fields = ['title_en', 'title_fr', 'title_es', 'title_nl']
    ordering_fields = ['order', 'estimated_duration']
    pagination_class = CustomPagination

    def get_serializer_context(self):
        context = super().get_serializer_context()
        requests = self.request
        user = requests.user
        target_language = requests.query_params.get('target_language', user.target_language)
        context['target_language'] = target_language
        return context
class VocabularyListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = VocabularyListSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = VocabularyListFilter
    search_fields = ['word_en', 'word_fr', 'word_es', 'word_nl']
    ordering_fields = ['word_en', 'word_fr', 'word_es', 'word_nl']

    def get(self, request):
        # Retrieve all vocabulary lists
        vocabulary_lists = VocabularyList.objects.all()

        # Apply filtering dynamically using DjangoFilterBackend
        filterset = self.filterset_class(request.GET, queryset=vocabulary_lists)
        if not filterset.is_valid():
            return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)

        filtered_queryset = filterset.qs

        # Apply search and ordering
        search_query = request.query_params.get('search')
        if search_query:
            filtered_queryset = filtered_queryset.filter(
                word_en__icontains=search_query
            ) | filtered_queryset.filter(
                word_fr__icontains=search_query
            ) | filtered_queryset.filter(
                word_es__icontains=search_query
            ) | filtered_queryset.filter(
                word_nl__icontains=search_query
            )

        ordering = request.query_params.get('ordering')
        if ordering:
            filtered_queryset = filtered_queryset.order_by(ordering)

        # Apply pagination
        paginator = self.pagination_class()
        paginated_vocabulary_lists = paginator.paginate_queryset(filtered_queryset, request)

        # Serialize the paginated queryset
        serializer = self.serializer_class(
            paginated_vocabulary_lists, many=True, context={'request': request}
        )

        # Return the paginated response
        return paginator.get_paginated_response(serializer.data)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        user = self.request.user
        target_language = self.request.query_params.get('target_language', getattr(user, 'target_language', 'en'))
        context['target_language'] = target_language
        return context
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
