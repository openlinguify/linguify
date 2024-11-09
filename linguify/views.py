from django.shortcuts import render
from rest_framework import viewsets
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import random

from .serializers import CoursesLanguagesSerializer, CoursesLanguagesCategorySerializer
from linguify.models import (
    CoursesLanguages, Vocabulary, Grammar, Units,
    UserLessonProgress, Revision, UserRevisionProgress, Quiz, CoursesLanguagesCategory
)
from linguify.forms import ThemeForm


def base(request):
    return render(request, 'base.html')


@login_required
def home(request):
    return render(request, 'linguify/home.html')


def index(request):
    return render(request, 'index.html')


def dashboard(request):
    return render(request, 'dashboard.html')


def header(request):
    return render(request, 'header.html', {'header': 'header'})


def footer(request):
    return render(request, 'footer.html')


def vocabulaire(request):
    return render(request, 'vocabulaire.html')


def exercice_vocabulary(request):
    vocabulary = list(Vocabulary.objects.all())
    if not vocabulary:
        return HttpResponse("No vocabulary words available.")

    # Select a random word and three other words
    random_word = random.choice(vocabulary)
    other_words = random.sample(
        [word for word in vocabulary if word != random_word],
        min(3, len(vocabulary) - 1)
    )

    words = other_words + [random_word]
    random.shuffle(words)

    context = {'word': random_word, 'choices': words}
    return render(request, 'exercice_vocabulaire.html', context)


def grammaire(request):
    context = {
        'vocabulaires': Vocabulary.objects.all(),
        'grammaires': Grammar.objects.all()
    }
    return render(request, 'grammaire.html', context)


def revision(request):
    return render(request, 'revision.html')


@login_required
def quiz(request):
    learning_language = getattr(request.user, 'learning_language', None)
    level = getattr(request.user, 'level_target_language', None)

    if not learning_language or not level:
        return HttpResponse("Please specify the learning language and level in your profile.")

    vocabulary_words = Vocabulary.objects.filter(language_id=learning_language, level_target_language=level)
    if not vocabulary_words.exists():
        return HttpResponse("No words found for the specified learning language and level.")

    word_pair = random.choice(vocabulary_words)
    incorrect_translations = Vocabulary.objects.exclude(pk=word_pair.pk).values_list('translation', flat=True)[:3]

    options = list(incorrect_translations) + [word_pair.translation]
    random.shuffle(options)

    context = {
        'language': learning_language,
        'word': word_pair.word,
        'options': options,
        'correct_translation': word_pair.translation
    }
    return render(request, 'quiz.html', context)


def check_answer(request):
    if request.method == 'POST':
        selected_translation = request.POST.get('selected_translation')
        correct_translation = request.POST.get('correct_translation')
        result = "Correct!" if selected_translation == correct_translation else "Incorrect!"
        context = {'result': result, 'correct_translation': correct_translation}
        return render(request, 'result.html', context)
    return HttpResponse("Method Not Allowed")


def testlinguistique(request):
    return render(request, 'testlinguistique.html')


def courses(request):
    courses = CoursesLanguages.objects.all()
    context = {
        'course_names': [course.title for course in courses],
        'course_descriptions': [course.description for course in courses],
    }
    return render(request, 'linguify/courses.html', context)


def prices(request):
    return render(request, 'linguify/prices.html')


def contact(request):
    return render(request, 'linguify/contact.html')


def about(request):
    return render(request, 'linguify/about.html')


def search_vocabulary(request):
    query = request.GET.get('query')
    vocabulary_list = Vocabulary.objects.filter(word__icontains=query) if query else Vocabulary.objects.all()
    context = {'vocabularies': vocabulary_list, 'query': query}
    return render(request, 'linguify/search_vocabulary.html', context)


class CoursesLanguagesViewSet(viewsets.ModelViewSet):
    serializer_class = CoursesLanguagesSerializer
    queryset = CoursesLanguages.objects.all()


class CoursesLanguagesCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CoursesLanguagesCategorySerializer
    queryset = CoursesLanguagesCategory.objects.all()
