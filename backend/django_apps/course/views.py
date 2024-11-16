# backend/django_apps/course/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import Vocabulary, Grammar, Quiz


import random

class HomeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        content = {'message': 'Welcome to the home page!'}
        return Response(content), status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED

class ExerciceVocabularyAPIView(APIView):
    def get(self, request):
        random_word = random.choice(Vocabulary.objects.all())
        other_words = Vocabulary.objects.exclude(pk=random_word.pk).order_by('?')[:3]
        words = list(other_words) + [random_word]
        random.shuffle(words)
        data = {
            'word': random_word.word,
            'choices': [{'id': w.id, 'word': w.word} for w in words]
        }
        return Response(data, status=status.HTTP_200_OK)

class GrammaireAPIView(APIView):
    def get(self, request):
        vocabulaires = Vocabulary.objects.all()
        grammaires = Grammar.objects.all()
        data = {
            'vocabulaires': [{'id': v.id, 'word': v.word} for v in vocabulaires],
            'grammaires': [{'id': g.id, 'title': g.grammar_title, 'description': g.grammar_description} for g in grammaires]
        }
        return Response(data, status=status.HTTP_200_OK)

class QuizAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, quiz_id=None):
        user = request.user
        learning_language = user.learning_language
        level = user.level_target_language

        if not learning_language or not level:
            return Response({"error": "Please specify the learning language and level in your profile."}, status=status.HTTP_400_BAD_REQUEST)

        vocabulary_words = Vocabulary.objects.filter(language_id=learning_language, level_target_language=level)
        if not vocabulary_words.exists():
            return Response({"error": "No words found for the specified learning language and level."}, status=status.HTTP_404_NOT_FOUND)

        word_pair = random.choice(vocabulary_words)
        word = word_pair.word
        correct_translation = word_pair.translation

        incorrect_translations = Quiz.objects.filter(language_id=learning_language.language_code, level=level).exclude(pk=quiz_id).values_list('translation', flat=True)[:3]
        options = list(incorrect_translations) + [correct_translation]
        random.shuffle(options)

        data = {
            'language': learning_language.language_name,
            'word': word,
            'options': options,
            'correct_translation': correct_translation
        }
        return Response(data, status=status.HTTP_200_OK)

class SearchVocabularyAPIView(APIView):
    def get(self, request):
        query = request.GET.get('query', '')
        vocabulary_list = Vocabulary.objects.filter(word__icontains=query) if query else Vocabulary.objects.all()
        data = [{'id': v.id, 'word': v.word, 'translation': v.translation} for v in vocabulary_list]
        return Response({'query': query, 'vocabularies': data}, status=status.HTTP_200_OK)
